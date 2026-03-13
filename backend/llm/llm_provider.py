from openai import OpenAI
import time
from config.settings import settings

class LLMProvider:
    def __init__(self):
        self.model = settings.MODEL_NAME
        
        if settings.USE_OPENROUTER_LLM:
            print(f"[LLMProvider] Initializing OPENROUTER connection to {settings.OPENAI_BASE_URL}")
            self.client = OpenAI(
                api_key=settings.OPENROUTER_API_KEY,
                base_url=settings.OPENAI_BASE_URL,
                timeout=120.0,
                default_headers={
                    "HTTP-Referer": "http://localhost:3000", # Optional, for including your app on openrouter.ai rankings.
                    "X-Title": "Agentic AI System", # Optional. Shows in rankings on openrouter.ai.
                }
            )
        elif settings.USE_LOCAL_LLM:
            print(f"[LLMProvider] Initializing LOCAL connection to {settings.OPENAI_BASE_URL}")
            self.client = OpenAI(
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_BASE_URL,
                timeout=120.0
            )
        else:
            print(f"[LLMProvider] Initializing OFFICIAL OpenAI Cloud connection.")
            self.client = OpenAI(
                api_key=settings.OPENAI_API_KEY,
                timeout=120.0
                # base_url is intentionally omitted to default to https://api.openai.com/v1
            )

    def generate_response(self, prompt: str, max_tokens: int = 200) -> str:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful AI assistant. Be highly concise. Answer directly."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=max_tokens,
                    temperature=0.2,
                    top_p=0.9
                )
                content = response.choices[0].message.content
                return content if content is not None else ""
            except Exception as e:
                error_msg = str(e).replace('"', '\\"').replace('\n', ' ')
                print(f"[LLMProvider] Attempt {attempt + 1} failed: {error_msg}")
                if attempt < max_retries - 1:
                    time.sleep((attempt + 1) * 2)
                else:
                    return f'{{"summary": "Task aborted due to persistent API error: {error_msg}", "recommendations": [], "steps": [], "needs_web_search": false}}'
        
        return "{\"summary\": \"Task aborted unexpectedly.\", \"recommendations\": [], \"steps\": [], \"needs_web_search\": false}"
