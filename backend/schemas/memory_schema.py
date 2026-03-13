from pydantic import BaseModel
from typing import List

class MemoryContextInfo(BaseModel):
    """
    Represents retrieved historical context from memory.
    """
    context_chunks: List[str]
