from pydantic import BaseModel, HttpUrl, RootModel
from typing import List, Dict

class AgentMetadata(BaseModel):
    id: str
    domain: str
    endpoint: HttpUrl
    keywords: List[str]

class ScoredAgent(AgentMetadata):
    score: float

class AgentTask(BaseModel):
    agent_id: str
    prompt: str
    endpoint: HttpUrl

class TraceEntry(BaseModel):
    step: str
    action: str
    collab_count: int
    details: Dict = {}

class AgentState(BaseModel):
    query: str
    responses: List[str]
    collab_count: int
    agent_tasks: List[AgentTask]
    trace: List[TraceEntry]

class RegisterAgentRequest(AgentMetadata):
    pass

class PromptRequest(BaseModel):
    prompt: str

class PromptResponse(BaseModel):
    response: str