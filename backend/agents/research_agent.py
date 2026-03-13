import json
from agents.base_agent import BaseAgent
from llm.llm_provider import LLMProvider
from schemas.research_schema import ResearchResult
from tools.web_search import WebSearchTool
from tools.calculator import CalculatorTool
from tools.file_reader import FileReaderTool

class ResearchAgent(BaseAgent):
    """
    Agent responsible for executing individual plan steps.
    It can decide to use tools or answer directly based on LLM reasoning.
    """
    def __init__(self, llm_provider: LLMProvider):
        super().__init__(llm_provider)
        # Initialize available tools
        self.web_search = WebSearchTool()
        self.calculator = CalculatorTool()
        self.file_reader = FileReaderTool()

    def execute_step(self, step: str) -> str:
        """
        Executes WebSearch Tool directly to save massive latency loops.
        """
        try:
            # Latency Optimization: Bypass the LLM "tool choice" decision and execute WebSearch directly
            # assuming the router approved web search needs.
            tool_result = self.web_search.search(step)
            
            # Prevent Context Window overflow on large web/file returns
            if len(tool_result) > 2000:
                tool_result = tool_result[:2000] + "\n...[TRUNCATED DUE TO CONTEXT SIZE]"
                
            return tool_result
            
        except Exception as e:
            return f"Error executing WebSearch step: {str(e)}"

    def execute_plan(self, plan_steps: list[str]) -> list[ResearchResult]:
        """
        Loops through all generated plan steps, executes them individually,
        and returns the consolidated results.
        """
        results = []
        for step in plan_steps:
            # Execute each step and capture the summarized output
            summary = self.execute_step(step)
            # Append the structured result
            results.append(ResearchResult(step=step, result=summary))
            
        return results
