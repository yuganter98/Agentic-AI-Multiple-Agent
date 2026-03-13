import time
from langgraph.graph import StateGraph, END
from schemas.agent_state import AgentState
from llm.llm_provider import LLMProvider

# General Agents
from agents.planner_agent import PlannerAgent
from agents.research_agent import ResearchAgent
from agents.writer_agent import WriterAgent
from agents.memory_agent import MemoryAgent
from agents.knowledge_agent import KnowledgeAgent
from agents.critic_agent import CriticAgent

# Coding Agents
from code_agents.task_classifier import TaskClassifier
from code_agents.code_generator_agent import CodeGeneratorAgent
from code_agents.code_reviewer_agent import CodeReviewerAgent

# Initialize shared resources
llm_provider = LLMProvider()
planner = PlannerAgent(llm_provider)
researcher = ResearchAgent(llm_provider)
writer = WriterAgent(llm_provider)
memory = MemoryAgent(llm_provider)
knowledge = KnowledgeAgent(llm_provider)
critic = CriticAgent(llm_provider)

classifier = TaskClassifier(llm_provider)
code_generator = CodeGeneratorAgent(llm_provider)
code_reviewer = CodeReviewerAgent(llm_provider)

# Run initial ingestion of PDF documents inside data/documents automatically
knowledge.ingest_documents()

# ----------------------------
# General & Research Nodes
# ----------------------------
def planner_node(state: AgentState):
    print(f"[Graph] Executing planner_node for task: {state['task']}")
    start = time.time()
    plan, needs_web = planner.create_plan(state["task"])
    elapsed = time.time() - start
    return {"plan": plan, "needs_web_search": needs_web, "planner_time": elapsed}

def retrieval_node(state: AgentState):
    print(f"[Graph] Executing sequential retrieval_node...")
    start = time.time()
    task = state["task"]
    plan = state["plan"]
    needs_web = state.get("needs_web_search", False)
    
    # 1. Retrieve Past Memory
    context = memory.retrieve_context(task)
    
    # 2. Retrieve Local Knowledge Base (RAG)
    knowledge_chunks = knowledge.retrieve_knowledge(task)
    knowledge_used = len(knowledge_chunks) > 0
    
    # 3. Evaluate Early Exit for Web Search via Similarity Score (>= 0.8)
    high_similarity_found = False
    if knowledge_used:
        for chunk in knowledge_chunks:
            if isinstance(chunk, dict) and chunk.get("score", 0) >= 0.8:
                high_similarity_found = True
                print("[Graph] ⚡ Early Exit condition met (knowledge similarity >= 0.8). Skipping Web Search.")
                break
                
    # 4. Execute Web Search only if Planner demanded it AND no local high-similarity answer exists
    web_results = []
    if needs_web and not high_similarity_found:
        print("[Graph] Executing web search research...")
        web_results = researcher.execute_plan(plan)
        memory.store_research(web_results)
        
    elapsed = time.time() - start
    return {
        "memory_context": context,
        "knowledge_chunks": knowledge_chunks,
        "knowledge_used": knowledge_used,
        "web_search_results": web_results,
        "retrieval_time": elapsed
    }

def writer_node(state: AgentState):
    print(f"[Graph] Executing writer_node... Iteration: {state.get('iterations', 0) + 1}")
    start = time.time()
    task_context = state["task"]
    
    # Appending retrieved contexts alongside task for analysis
    context_str = "\\n\\nMemory Context: " + str(state.get("memory_context", []))
    
    if state.get("knowledge_chunks"):
        context_str += "\\n\\nDocument Context: " + str(state.get("knowledge_chunks", []))
    if state.get("web_search_results"):
        context_str += "\\n\\nWeb Search Results: " + str(state.get("web_search_results", []))
    if state.get("critic_feedback") and not state.get("is_approved"):
        task_context += f"\\n\\n[CRITIC FEEDBACK FOR REVISION]: {state['critic_feedback']}"
        
    task_context += context_str
        
    final_answer = writer.generate_final_answer(task_context, state.get("web_search_results", []))
    
    # Increment iteration counter
    new_iterations = state.get("iterations", 0) + 1
    elapsed = time.time() - start
    return {"final_answer": final_answer, "iterations": new_iterations, "writer_time": elapsed}

def critic_node(state: AgentState):
    print(f"[Graph] Executing critic_node...")
    start = time.time()
    # Currently critics are disabled for extreme latency limits (Max 2 LLM calls: Planner + Writer)
    # Automatically approve to bypass the evaluation round unless configured otherwise
    elapsed = time.time() - start
    print(f"[Graph] Critic bypassed intentionally for Latency constraints (Approved).")
    return {
        "is_approved": True,
        "critic_feedback": "Looks good.",
        "critic_time": elapsed
    }

# ----------------------------
# Coding Nodes
# ----------------------------
def classifier_node(state: AgentState):
    print(f"[Graph] Executing classifier_node...")
    start = time.time()
    task_type = classifier.classify_task(state["task"])
    elapsed = time.time() - start
    return {"task_type": task_type, "classifier_time": elapsed}

def code_generator_node(state: AgentState):
    print(f"[Graph] Executing code_generator_node... Iteration: {state.get('iterations', 0) + 1}")
    start = time.time()
    task = state["task"]
    feedback = state.get("review_feedback", "")
    
    generation_result = code_generator.generate_code(task, feedback)
    
    new_iterations = state.get("iterations", 0) + 1
    elapsed = time.time() - start
    return {
        "generated_code": generation_result["generated_code"],
        "final_answer": {"summary": generation_result["explanation"], "task": task, "recommendations": []},
        "iterations": new_iterations,
        "code_generator_time": elapsed
    }

def code_reviewer_node(state: AgentState):
    print(f"[Graph] Executing code_reviewer_node...")
    start = time.time()
    task = state["task"]
    code = state.get("generated_code", "")
    
    review_result = code_reviewer.review_code(task, code)
    
    elapsed = time.time() - start
    return {
        "is_approved": review_result["is_approved"],
        "review_feedback": review_result["review_feedback"],
        "improved_code": review_result["improved_code"],
        "code_reviewer_time": elapsed
    }

# ----------------------------
# Conditional Routers
# ----------------------------
def route_task_type(state: AgentState):
    """
    Routes the task based on the classifier's determination.
    """
    task_type = state.get("task_type", "research")
    print(f"[Graph] Routing task type: {task_type}")
    if task_type == "coding":
        return "code_generator_node"
    else:
        return "planner_node"

def should_continue(state: AgentState):
    """
    Research Pipeline router
    """
    if state["is_approved"]:
        return END
    elif state.get("iterations", 0) >= state.get("max_iterations", 1):
        return END
    else:
        return "writer_node"

def should_continue_coding(state: AgentState):
    """
    Coding Pipeline router
    """
    if state["is_approved"]:
        print("[Graph] Code approved. Finishing coding workflow.")
        return END
    elif state.get("iterations", 0) >= state.get("max_iterations", 1):
        # We only allow the code generator to retry 1 extra time for latency limits
        print(f"[Graph] Code Editor max iterations reached. Forcing finish.")
        return END
    else:
        print("[Graph] Code rejected. Looping back to Code Generator.")
        return "code_generator_node"


# ----------------------------
# Graph Construction
# ----------------------------
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("classifier_node", classifier_node)

workflow.add_node("planner_node", planner_node)
workflow.add_node("retrieval_node", retrieval_node)
workflow.add_node("writer_node", writer_node)
workflow.add_node("critic_node", critic_node)

workflow.add_node("code_generator_node", code_generator_node)
workflow.add_node("code_reviewer_node", code_reviewer_node)

# Set Entry Point
workflow.set_entry_point("classifier_node")

# Fork Pipeline after Classification
workflow.add_conditional_edges(
    "classifier_node",
    route_task_type,
    {
        "code_generator_node": "code_generator_node",
        "planner_node": "planner_node"
    }
)

# Build Research Pipeline
workflow.add_edge("planner_node", "retrieval_node")
workflow.add_edge("retrieval_node", "writer_node")
workflow.add_edge("writer_node", "critic_node")
workflow.add_conditional_edges(
    "critic_node",
    should_continue,
    {
        END: END,
        "writer_node": "writer_node"
    }
)

# Build Coding Pipeline
workflow.add_edge("code_generator_node", "code_reviewer_node")
workflow.add_conditional_edges(
    "code_reviewer_node",
    should_continue_coding,
    {
        END: END,
        "code_generator_node": "code_generator_node"
    }
)

# Compile to runnable application
agentic_app = workflow.compile()
