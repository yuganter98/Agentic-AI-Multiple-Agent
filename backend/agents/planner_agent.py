import json
import re
from agents.base_agent import BaseAgent
from llm.llm_provider import LLMProvider

class PlannerAgent(BaseAgent):
    """
    Agent responsible for breaking down a high-level task into actionable steps.
    Inherits from BaseAgent but overrides the run behavior to focus on planning.
    """
    def __init__(self, llm_provider: LLMProvider):
        super().__init__(llm_provider)

    def create_plan(self, task: str) -> list[str]:
        """
        Takes a user task and returns a list of string steps to execute.
        Instructs the LLM to return structured JSON.
        """
        prompt = f"""Break the following task into logical steps to execute.
Additionally, determine if this task requires searching the public internet for recent facts (needs_web_search).
Return ONLY structured JSON in the following format, with no markdown code blocks or extra text:
{{
  "steps": [
    "step 1",
    "step 2"
  ],
  "needs_web_search": true or false
}}

Task: {task}"""
        
        # Generate the response using the LLM Provider
        response_text = self.llm_provider.generate_response(prompt)
        
        try:
            clean_text = response_text.strip()
            
            # Use regex to aggressively extract the JSON block
            json_match = re.search(r"\{.*\}", clean_text, re.DOTALL)
            if json_match:
                clean_text = json_match.group(0)
                
            data = json.loads(clean_text)
            steps = data.get("steps", [])
            needs_web = data.get("needs_web_search", False)
            return steps, needs_web
        except json.JSONDecodeError:
            # Fallback
            return [], False
