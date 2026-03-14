import os
import sys
from contextlib import asynccontextmanager

# Add the parent directory to sys.path to resolve module imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from schemas.task_schema import TaskRequest
from observability.metrics_collector import MetricsCollector
import time

from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load heavy AI models and agents AFTER uvicorn has bound the port."""
    print("[Startup] Loading agents and models...")
    from workflow.agent_graph import agentic_app
    from cache.redis_cache import RedisCache
    app.state.agentic_app = agentic_app
    app.state.redis_cache = RedisCache()
    print("[Startup] All agents loaded successfully.")
    yield
    print("[Shutdown] Cleaning up...")

app = FastAPI(title="Agentic AI System API - LangGraph Edition", lifespan=lifespan)

# Allow requests from the Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Global Metrics Collector (lightweight, safe at import time)
metrics_collector = MetricsCollector()

@app.post("/task")
async def process_task(request: TaskRequest):
    """
    Accepts a task from the user, checks the cache, and invokes the multi-agent LangGraph workflow if necessary.
    """
    start_time = time.time()
    redis_cache = app.state.redis_cache
    agentic_app = app.state.agentic_app
    try:
        # Check Redis Cache
        cached_answer = redis_cache.get_cached_answer(request.task)
        if cached_answer:
            latency_ms = (time.time() - start_time) * 1000
            
            # Record Cache Hit Metrics
            metrics_collector.record_request({
                "latency_ms": latency_ms,
                "cache_hit": True,
                "rag_used": False,
                "iterations": 0
            })
            
            return {
                "task": request.task,
                "cache_hit": True,
                "final_answer": cached_answer
            }

        # Initialize the state schema based on AgentState requirements
        initial_state = {
            "task": request.task,
            "plan": [],
            "memory_context": [],
            "knowledge_chunks": [],
            "web_search_results": [],
            "final_answer": None,
            "critic_feedback": "",
            "is_approved": False,
            "iterations": 0,
            "max_iterations": 1,
            "knowledge_used": False,
            "needs_web_search": False,
            "latency_ms": 0.0,
            "planner_time": 0.0,
            "retrieval_time": 0.0,
            "writer_time": 0.0,
            "critic_time": 0.0,
            "classifier_time": 0.0,
            "code_generator_time": 0.0,
            "code_reviewer_time": 0.0,
            "improved_code": "",
            "generated_code": "",
            "review_feedback": ""
        }
        
        # Invoke the LangGraph app synchronously.
        final_state = agentic_app.invoke(initial_state)
        
        # Grab final_answer object and serialize correctly for Redis
        final_ans = final_state.get("final_answer", {})
        final_ans_dict = final_ans.dict() if hasattr(final_ans, "dict") else final_ans
        
        latency_ms = (time.time() - start_time) * 1000
        cache_hit = False
        rag_used = final_state.get("knowledge_used", False)
        iterations_used = final_state.get("iterations", 1)
        
        # Record Pipeline Execution Metrics
        metrics_collector.record_request({
            "latency_ms": latency_ms,
            "cache_hit": cache_hit,
            "rag_used": rag_used,
            "iterations": iterations_used,
            "classifier_time": final_state.get("classifier_time", 0.0),
            "code_generator_time": final_state.get("code_generator_time", 0.0),
            "code_reviewer_time": final_state.get("code_reviewer_time", 0.0)
        })
        
        # Structure payload to flexibly handle both research and coding pipelines
        response_payload = {
            "task": request.task,
            "task_type": final_state.get("task_type", "research"),
            "iterations_used": iterations_used,
            "cache_hit": cache_hit,
            "knowledge_used": rag_used,
            "knowledge_chunks": final_state.get("knowledge_chunks", []),
            "final_answer": final_ans_dict,
            "generated_code": final_state.get("generated_code", ""),
            "improved_code": final_state.get("improved_code", ""),
            "review_feedback": final_state.get("review_feedback", ""),
            "latency_ms": round(latency_ms, 2),
            "planner_time": round(final_state.get("planner_time", 0.0) * 1000, 2),
            "retrieval_time": round(final_state.get("retrieval_time", 0.0) * 1000, 2),
            "writer_time": round(final_state.get("writer_time", 0.0) * 1000, 2),
            "critic_time": round(final_state.get("critic_time", 0.0) * 1000, 2),
            "classifier_time": round(final_state.get("classifier_time", 0.0) * 1000, 2),
            "code_generator_time": round(final_state.get("code_generator_time", 0.0) * 1000, 2),
            "code_reviewer_time": round(final_state.get("code_reviewer_time", 0.0) * 1000, 2)
        }
        
        # Save to Redis Cache for future identical requests
        if final_ans_dict:
            redis_cache.set_cached_answer(request.task, final_ans_dict)
            
        return response_payload
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
async def get_metrics():
    """
    Returns an aggregated statistical summary of all platform observations.
    """
    return metrics_collector.get_metrics_summary()

if __name__ == "__main__":
    import uvicorn
    import os
    
    # Use the port assigned by the cloud platform, or default to 8000
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("api.main:app", host="0.0.0.0", port=port)
