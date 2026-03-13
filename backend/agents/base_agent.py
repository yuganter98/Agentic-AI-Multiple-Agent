from llm.llm_provider import LLMProvider

class BaseAgent:
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider

    def run(self, task: str) -> str:
        # Format the core reasoning or instruction prompt
        prompt = f"Please process the following task:\n\n{task}"
        
        # In a multi-agent or more mature system, this method might also 
        # gather context, invoke tools, and iteratively handle reasoning.
        response = self.llm_provider.generate_response(prompt)
        
        return response
