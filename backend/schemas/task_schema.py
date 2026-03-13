from pydantic import BaseModel

class TaskRequest(BaseModel):
    task: str

class TaskResponse(BaseModel):
    response: str
