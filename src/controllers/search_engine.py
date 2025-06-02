from fastapi import FastAPI
from pydantic import BaseModel
from src.nodes.agent_graph import app
from src.models.models import AgentState

fastapi_app = FastAPI()

class SearchRequest(BaseModel):
    prompt: str

@fastapi_app.post("/search", response_model=AgentState)
async def search(request: SearchRequest):
    state = AgentState(query=request.prompt, responses=[], collab_count=0, agent_tasks=[], trace=[])
    result = await app.ainvoke(state)
    return result