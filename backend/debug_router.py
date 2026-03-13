import sys
from llm.llm_provider import LLMProvider

def main():
    llm = LLMProvider()
    task = 'famous hotel in japan'
    prompt = f"""You are a routing agent.

    Decide which tool should answer the question.
    Use knowledge_base for questions about stored documents, company specifics, or internal data.
    Use web_search for questions requiring external, current, or public world information.

    User Task: '{task}'

    Return ONLY a JSON object in this exact format:
    {{
      "tool": "knowledge_base"  or "web_search"
    }}"""

    response = llm.generate_response(prompt)
    print('---RAW OUTPUT---')
    print(repr(response))
    print('---PRINT OUTPUT---')
    print(response)

if __name__ == "__main__":
    main()
