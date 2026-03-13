import json
import re
from agents.base_agent import BaseAgent
from llm.llm_provider import LLMProvider

class CodeReviewerAgent(BaseAgent):
    """
    Reviews generated code against the original task for bugs, edge cases, and missing requirements.
    """
    def __init__(self, llm_provider: LLMProvider):
        super().__init__(llm_provider)

    def review_code(self, task: str, generated_code: str) -> dict:
        """
        Analyzes the generated code and returns approval boolean and feedback.
        """
        prompt = f"""You are a senior AI platform engineer.

Think step-by-step like a senior engineer reviewing a pull request before approving it.

Your job is to review the generated code submitted to see if it accomplishes the task.
You must analyze the code for the following:
- logical correctness and edge case resilience
- defensive programming and rigorous input validation
- algorithmic complexity optimization (Time & Space)
- privacy, security, and enterprise standards
- clear readability and professional documentation

Assume the code will be merged into a mission-critical production environment. You are expected to rewrite portions of the code if it fails to meet these senior-level standards.

CRITICAL INSTRUCTIONS:
You MUST return your response using EXACTLY this markdown structure, with no extra formatting outside of it:

### REVIEW STATUS
APPROVED (or REJECTED)

### ISSUES FOUND
- Issue 1
- Issue 2

### REVIEW SUMMARY
A short explanation of improvements.

### IMPROVED CODE
```python
# The corrected code block goes here. Do not escape newlines or quotes.
```

Input example:
Task: {task}
Generated Code:
```
{generated_code}
```
"""
        
        response_text = self.llm_provider.generate_response(prompt, max_tokens=1500)
        
        # Robust Markdown Regex Extraction
        is_approved = False
        issues = []
        review_feedback = "No feedback provided."
        improved_code = generated_code
        
        status_match = re.search(r"### REVIEW STATUS\s*(.*?)\s*###", response_text, re.DOTALL | re.IGNORECASE)
        if status_match:
            is_approved = "APPROVED" in status_match.group(1).upper()
            
        issues_match = re.search(r"### ISSUES FOUND\s*(.*?)\s*###", response_text, re.DOTALL | re.IGNORECASE)
        if issues_match:
            issues = [i.strip('-* ') for i in issues_match.group(1).strip().split('\n') if i.strip()]
            
        summary_match = re.search(r"### REVIEW SUMMARY\s*(.*?)\s*### CODE", response_text, re.DOTALL | re.IGNORECASE)
        # Handle cases where summary is the last block or followed by IMPROVED CODE
        if not summary_match:
            summary_match = re.search(r"### REVIEW SUMMARY\s*(.*?)\s*###", response_text, re.DOTALL | re.IGNORECASE)
        if summary_match:
            review_feedback = summary_match.group(1).strip()
            
        code_match = re.search(r"### IMPROVED CODE\s*```[a-zA-Z]*\s*(.*?)\s*```", response_text, re.DOTALL | re.IGNORECASE)
        if code_match:
            improved_code = code_match.group(1).strip()
        else:
            # Fallback if the user omitted the backticks
            alt_code_match = re.search(r"### IMPROVED CODE\s*(.*)", response_text, re.DOTALL | re.IGNORECASE)
            if alt_code_match:
                improved_code = alt_code_match.group(1).strip()

        # Final cleanup for rogue markdown blocks or escaping
        improved_code = improved_code.replace("\\n", "\n")

        return {
            "is_approved": is_approved,
            "review_feedback": review_feedback,
            "improved_code": improved_code,
            "issues": issues
        }
