import json
import re
from agents.base_agent import BaseAgent
from llm.llm_provider import LLMProvider

class RouterAgent(BaseAgent):
    """
    Agent responsible for analyzing the user task and deciding whether it should be answered
    using the internal Knowledge Base (RAG) or an external Web Search.
    """
    
    def __init__(self, llm_provider: LLMProvider):
        super().__init__(llm_provider)
        
    def route_task(self, task: str) -> dict:
        """
        Determines the most appropriate tool to answer the user's task.
        Returns a dictionary with the 'tool' key mapping to either 
        'knowledge_base' or 'web_search'.
        """
        prompt = f"""You are a routing agent.

Decide which tool should answer the question.
Use knowledge_base for questions about stored documents, company specifics, or internal data.
Use web_search for questions requiring external, current, or public world information.

User Task: "{task}"

Return ONLY a JSON object in this exact format:
{{
  "tool": "knowledge_base" or "web_search"
}}"""
        
        response_text = self.llm_provider.generate_response(prompt)
        
        try:
            # Clean and parse the output
            clean_text = response_text.strip()
            
            # Use regex to aggressively extract the JSON block
            json_match = re.search(r"\{.*\}", clean_text, re.DOTALL)
            if json_match:
                clean_text = json_match.group(0)
                
            data = json.loads(clean_text)
            
            # Default to web_search if something goes wrong in the LLM formatting
            tool = data.get("tool", "web_search")
            if tool not in ["knowledge_base", "web_search"]:
                tool = "web_search"
                
            return {"tool": tool}
            
        except json.JSONDecodeError:
            print(f"[RouterAgent] JSON parsing failure. Defaulting to web_search. Raw response: {response_text}")
            return {"tool": "web_search"}
        except Exception as e:
            print(f"[RouterAgent] Routing error: {str(e)}. Defaulting to web_search.")
            return {"tool": "web_search"}
