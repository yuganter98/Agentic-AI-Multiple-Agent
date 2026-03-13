import json
import re
from agents.base_agent import BaseAgent
from schemas.research_schema import ResearchResult
from schemas.final_response_schema import FinalResponse

class WriterAgent(BaseAgent):
    """
    Agent responsible for combining research findings and producing a clear,
    structured final answer without duplicate information in JSON format.
    """
    
    def generate_final_answer(self, task: str, research_results: list[ResearchResult]) -> FinalResponse:
        """
        Synthesizes the research results into a concise summary and a set
        of recommendations related to the original task.
        """
        # Format the research findings for the LLM prompt
        formatted_results = "\n\n".join(
            [f"Step: {r.step}\nFinding: {r.result}" for r in research_results]
        )
        
        # Prevent Context Window Overflow
        if len(formatted_results) > 2500:
            formatted_results = formatted_results[:2500] + "\n...[TRUNCATED DUE TO CONTEXT SIZE]"
        
        prompt = f"""You are a synthesis agent.

Your job is to combine research findings and produce a final answer for the user's task.
If critic feedback is provided in the input, you MUST improve the previous answer based on that critic feedback.
Remove any duplicate information.
Provide structured results as ONLY a JSON object exactly matching this format:

{{
  "task": "The original task description",
  "summary": "A cohesive summary of all the findings",
  "recommendations": [
    {{
      "key_1": "value_1",
      "key_2": "value_2"
    }}
  ]
}}

Original Task: {task}

Research Findings:
{formatted_results}
"""
        
        response_text = self.llm_provider.generate_response(prompt, max_tokens=1000)
        
        try:
            # Clean and parse the output
            clean_text = response_text.strip()
            
            # Use regex to aggressively extract the JSON block
            json_match = re.search(r"\{.*\}", clean_text, re.DOTALL)
            if json_match:
                clean_text = json_match.group(0)
                
            data = json.loads(clean_text)
            
            return FinalResponse(
                task=data.get("task", task),
                summary=data.get("summary", "Summary not provided."),
                recommendations=data.get("recommendations", [])
            )
        except json.JSONDecodeError:
            # Fallback handling
            return FinalResponse(
                task=task,
                summary=f"Failed to parse LLM response into structured formatting.\nRaw response:\n{response_text}",
                recommendations=[]
            )
        except Exception as e:
            return FinalResponse(
                task=task,
                summary=f"Error generating final answer: {str(e)}",
                recommendations=[]
            )
