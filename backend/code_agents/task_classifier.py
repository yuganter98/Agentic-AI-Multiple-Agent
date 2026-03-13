import json
from agents.base_agent import BaseAgent
from llm.llm_provider import LLMProvider

class TaskClassifier(BaseAgent):
    """
    Classifies an incoming user task as either "coding" or "research".
    Utilizes keyword heuristics first, falling back to LLM classification for ambiguity.
    """
    def __init__(self, llm_provider: LLMProvider):
        super().__init__(llm_provider)

        # Keyword heuristics to bypass LLM classification overhead
        self.coding_keywords = {"code", "function", "bug", "fix", "script", "app", 
                                "python", "javascript", "react", "html", "css",
                                "algorithm", "debug", "refactor"}

    def classify_task(self, task: str) -> str:
        """
        Returns "coding" or "research" based on the task intent.
        """
        task_lower = task.lower()
        
        # 1. Fast Keyword Heuristic
        for keyword in self.coding_keywords:
            # Simple substring matching (expand to regex boundaries for production)
            if keyword in task_lower.split():
                print(f"[TaskClassifier] Keyword '{keyword}' detected. Routing to CODING pipeline.")
                return "coding"

        # 2. LLM Fallback Classification
        print("[TaskClassifier] Ambiguous intent. Routing to LLM classifier...")
        prompt = f"""You are a task routing agent.
Analyze the following user task and classify it into exactly ONE of two categories: 'coding' or 'research'.

- Choose 'coding' if the user is asking to write, generate, debug, fix, or review software code, scripts, or building applications.
- Choose 'research' if the user is asking a general question, looking for facts, asking for advice, or anything else.

Return ONLY a JSON object exactly matching this format:
{{
  "task_type": "coding" OR "research"
}}

Task: {task}
"""
        
        response_text = self.llm_provider.generate_response(prompt, max_tokens=100)
        
        try:
            clean_text = response_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
                
            data = json.loads(clean_text)
            return data.get("task_type", "research").lower()
            
        except json.JSONDecodeError:
            print("[TaskClassifier] LLM parsing failed. Defaulting to research pipeline.")
            return "research"
