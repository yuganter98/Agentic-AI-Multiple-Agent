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
import threading
import logging

from config.settings import settings

# Global flag - prevents requests from being served until agents are fully loaded
_agents_ready = False
_startup_error = None
_last_status = "Waiting for background thread to start..."
_memory_usage = "N/A"

def get_process_memory():
    try:
        import psutil
        process = psutil.Process(os.getpid())
        mem_info = process.memory_info()
        return f"{mem_info.rss / 1024 / 1024:.2f} MB"
    except ImportError:
        return "psutil not installed"
    except Exception as e:
        return f"Error: {e}"

def _load_agents_in_background(app: FastAPI):
    """Downloads model weights and initializes agents in a background thread."""
    global _agents_ready, _startup_error, _last_status, _memory_usage
    try:
        import traceback
        _last_status = "Starting background loading..."
        
        # Determine environment
        env = "Local"
        if os.environ.get("RAILWAY_STATIC_URL"):
            env = "Railway"
        elif os.environ.get("RENDER_EXTERNAL_URL"):
            env = "Render"
        
        logger.info(f"--- Startup Diagnostics ({env}) ---")
        
        # Check OpenRouter
        or_key = settings.OPENROUTER_API_KEY
        if or_key:
            logger.info(f"[OpenRouter] API Key found (ends with ...{or_key[-4:] if len(or_key)>4 else '****'})")
        else:
            logger.warning("[OpenRouter] API Key NOT found")

        _memory_usage = get_process_memory()
        logger.info(f"[_last_status] Memory: {_memory_usage}")

        print(f"[Startup] Background thread: loading agents & models in {env}...")
        _last_status = "Importing workflow (this can take a while)..."
        _memory_usage = get_process_memory()
        
        from workflow.agent_graph import agentic_app
        from cache.redis_cache import RedisCache
        
        # Check Redis
        try:
            temp_cache = RedisCache()
            if temp_cache.client.ping():
                logger.info("[Redis] Connection successful")
            else:
                logger.warning("[Redis] Connection failed (Ping failed)")
        except Exception as re:
            logger.warning(f"[Redis] Connection error: {re}")

        _last_status = "Initializing state values..."
        app.state.agentic_app = agentic_app
        app.state.redis_cache = RedisCache()
        
        # Trigger document ingestion explicitly now that agents are loaded
        _last_status = "Ingesting knowledge base documents (RAG)..."
        try:
            from workflow.agent_graph import knowledge
            knowledge.ingest_documents()
        except Exception as ingest_e:
            logger.warning(f"Ingestion warning: {ingest_e}")
        
        _agents_ready = True
        _last_status = "Ready"

        _memory_usage = get_process_memory()
        print("[Startup] Background thread: All agents ready!")
        logger.info(f"System ready. Memory: {_memory_usage}")
    except Exception as e:
        import traceback
        _startup_error = traceback.format_exc()
        _last_status = f"CRASHED: {str(e)}"
        _memory_usage = get_process_memory()
        print(f"[Startup] ERROR loading agents: {_startup_error}")
        logger.error(f"Startup crash: {_startup_error}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start agent loading in background thread, then yield immediately so port binds."""
    thread = threading.Thread(target=_load_agents_in_background, args=(app,), daemon=True)
    thread.start()
    # Yield immediately - uvicorn binds port NOW while models load in background
    yield
    print("[Shutdown] Cleaning up...")


app = FastAPI(title="Agentic AI System API - LangGraph Edition", lifespan=lifespan)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Lightweight health check for Railway/Render."""
    return {"status": "ok", "timestamp": time.time()}

# Initialize Global Metrics Collector (lightweight, safe at import time)
metrics_collector = MetricsCollector()

@app.post("/task")
async def process_task(request: TaskRequest):
    """
    Accepts a task from the user, checks the cache, and invokes the multi-agent LangGraph workflow if necessary.
    """
    if not _agents_ready:
        raise HTTPException(status_code=503, detail="System is warming up. Please try again in 30 seconds.")
    
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

@app.get("/status")
async def get_status():
    """Returns the startup readiness of the agent system."""
    return {
        "ready": _agents_ready,
        "status": _last_status,
        "memory": get_process_memory(),
        "error": _startup_error
    }

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
