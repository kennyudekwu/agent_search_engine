from pydantic import BaseModel

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class RespondRequest(BaseModel):
    query: str

class RespondResponse(BaseModel):
    response: str

@app.post("/respond", response_model=RespondResponse)
async def respond(request: RespondRequest):
    # Mock JSON search (5-10 pipelines)
    return RespondResponse(response=f"Jenkins: {agent_answer(request.query)}")

def agent_answer(query: str) -> str:
    pass

