from typing import TypedDict, List, Any

class AgentState(TypedDict):
    """
    Shared state dictionary for the LangGraph workflow.
    This maintains the context as it flows through the various agents.
    """
    task: str
    plan: List[str]
    memory_context: List[str]
    knowledge_chunks: List[str] # Will hold chunked document context from RAG
    web_search_results: List[Any]  # Will hold ResearchResult objects
    final_answer: Any            # Will hold the FinalResponse object
    critic_feedback: str         # Holds feedback from the Critic Agent
    is_approved: bool            # Indicates if the final answer passed review
    iterations: int              # Number of times the writer has attempted an answer
    max_iterations: int          # Maximum number of writer attempts allowed
    knowledge_used: bool         # Indicates whether local RAG was successfully utilized
    needs_web_search: bool       # Indicates if the Planner decided Web Search is required
    
    # Coding Pathway Variables
    task_type: str               # "research" or "coding"
    generated_code: str
    improved_code: str
    review_feedback: str
    
    # Latency Observability Metrics
    latency_ms: float
    planner_time: float
    retrieval_time: float
    writer_time: float
    critic_time: float
    classifier_time: float
    code_generator_time: float
    code_reviewer_time: float
