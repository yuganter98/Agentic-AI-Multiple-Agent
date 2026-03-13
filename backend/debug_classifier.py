import sys
from llm.llm_provider import LLMProvider

def main():
    llm = LLMProvider()
    task = 'famous hotel in japan'
    
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
    
    response = llm.generate_response(prompt, max_tokens=100)
    print('---RAW OUTPUT---')
    print(repr(response))
    print('---PRINT OUTPUT---')
    print(response)

if __name__ == "__main__":
    main()
