import json
import re
from agents.base_agent import BaseAgent
from llm.llm_provider import LLMProvider

class CodeGeneratorAgent(BaseAgent):
    """
    Generates software code based on a task description.
    """
    def __init__(self, llm_provider: LLMProvider):
        super().__init__(llm_provider)

    def generate_code(self, task: str, feedback: str = "") -> dict:
        """
        Returns a dict containing 'code' and 'explanation'.
        Injects feedback from the reviewer if this is a regeneration attempt.
        """
        prompt = f"""You are an Expert Software Engineer.
Your job is to generate high-quality, reliable, and well-commented code to solve the user's task.

CRITICAL INSTRUCTIONS:
1. If the user does not specify a programming language in their task, default to Python.
2. You MUST return your response using EXACTLY this markdown structure, with no extra formatting outside of it:

### EXPLANATION
A concise explanation of how the code works.

### CODE
```python
# The raw code block goes here. Do not escape newlines or quotes.
```
"""
        if feedback:
            prompt += f"\n\nPREVIOUS CODE FAILED REVIEW. Please fix the following issues:\n[CRITIC FEEDBACK]: {feedback}"

        prompt += f"\n\nUser Task: {task}"
        
        response_text = self.llm_provider.generate_response(prompt, max_tokens=1500)
        
        # Robust Markdown Regex Extraction
        explanation = "No explanation provided."
        generated_code = "No code generated."
        
        exp_match = re.search(r"### EXPLANATION\s*(.*?)\s*### CODE", response_text, re.DOTALL | re.IGNORECASE)
        if exp_match:
            explanation = exp_match.group(1).strip()
            
        code_match = re.search(r"### CODE\s*```[a-zA-Z]*\s*(.*?)\s*```", response_text, re.DOTALL | re.IGNORECASE)
        if code_match:
            generated_code = code_match.group(1).strip()
        else:
            # Fallback if the user omitted the backticks
            alt_code_match = re.search(r"### CODE\s*(.*)", response_text, re.DOTALL | re.IGNORECASE)
            if alt_code_match:
                generated_code = alt_code_match.group(1).strip()
                
        # Final cleanup for rogue markdown blocks or escaping
        generated_code = generated_code.replace("\\n", "\n")
        
        # Nemotron frequently hallucinates `\\python` instead of ```python
        generated_code = re.sub(r"^\\\\[a-zA-Z]*\s*", "", generated_code, flags=re.IGNORECASE)
        # Nemotron occasionally finishes with a trailing `\`
        generated_code = re.sub(r"\\+$", "", generated_code).strip()

        return {
            "generated_code": generated_code,
            "explanation": explanation
        }
