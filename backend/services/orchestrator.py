from llm.llm_provider import LLMProvider
from agents.planner_agent import PlannerAgent
from agents.research_agent import ResearchAgent
from agents.writer_agent import WriterAgent
from agents.memory_agent import MemoryAgent
from schemas.research_schema import WorkflowResponse

class Orchestrator:
    """
    Service responsible for coordinating interactions between agents.
    It abstracts agent management away from the API layer.
    """
    def __init__(self, llm_provider: LLMProvider = None):
        # Initialize providers and agents needed for the workflow
        self.llm_provider = llm_provider or LLMProvider()
        self.planner = PlannerAgent(self.llm_provider)
        self.researcher = ResearchAgent(self.llm_provider)
        self.writer = WriterAgent(self.llm_provider)
        self.memory = MemoryAgent(self.llm_provider)

    def process_task(self, task: str) -> WorkflowResponse:
        """
        Flow:
        1. Call PlannerAgent to generate a step-by-step plan.
        2. Retrieve context using MemoryAgent based on the task.
        3. Pass plan to ResearchAgent for execution.
        4. Store new research results in MemoryAgent.
        5. Pass research results (and memory optionally) to the WriterAgent.
        """
        # Step 1: Instruct Planner Agent to generate a plan
        plan_steps = self.planner.create_plan(task)
        
        # Step 2: Retrieve historical memory context specific to the overall task
        memory_context = self.memory.retrieve_context(task)
        
        # Depending on how the user wants constraints, we could insert memory directly 
        # into the Researcher or Writer prompt. For now, we will just retrieve it.
        
        # Step 3: Delegate execution to the Research Agent
        research_results = self.researcher.execute_plan(plan_steps)
        
        # Step 4: Store the newly discovered research findings into Memory
        self.memory.store_research(research_results)
        
        # Step 5: Generate the final synthesized response using Writer Agent
        # Note: Depending on further enhancements, WriterAgent can also ingest `memory_context`
        final_answer = self.writer.generate_final_answer(task, research_results)
        
        # Construct and return the full workflow response
        return WorkflowResponse(
            task=task, 
            plan=plan_steps, 
            memory_context=memory_context,
            research_results=research_results,
            final_answer=final_answer
        )
