from pydantic import BaseModel
from typing import List

class PlanStep(BaseModel):
    """
    Represents a single step in a generated execution plan.
    Currently a simple string wrapper, but can be expanded with status, dependencies, etc.
    """
    description: str

class LLMPlanOutput(BaseModel):
    """
    Schema for parsing the structured JSON output directly from the LLM.
    """
    steps: List[str]

class PlanResponse(BaseModel):
    """
    Response schema for the API endpoint returning the generated plan to the user.
    """
    task: str
    plan: List[str]
