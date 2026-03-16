import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    # LLM Toggle: Set to 'true' for LM Studio/Ollama, 'false' for official OpenAI API
    USE_LOCAL_LLM = os.getenv("USE_LOCAL_LLM", "false").lower() == "true"
    USE_OPENROUTER_LLM = os.getenv("USE_OPENROUTER_LLM", "true").lower() == "true"
    
    # Official API / Local Credentials
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "lm-studio")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
    
    # Defaults to OpenRouter API if no base URL is provided in env
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
    
    # Model configuration (Nemotron 3 Super by default for OpenRouter)
    MODEL_NAME = os.getenv("MODEL_NAME", "nvidia/nemotron-3-super-120b-a12b:free")
    
    # Tooling
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
    
    # Redis configuration
    REDIS_URL = os.getenv("REDIS_URL", "")

    # Security & Networking
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    
    # Vector Database
    VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./chroma_db")

settings = Settings()
