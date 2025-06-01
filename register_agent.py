from fastapi import FastAPI, HTTPException
from views import AgentMetadata, RegisterAgentRequest
from typing import List
from pathlib import Path
import json
from models import AgentMetadata
from qdrant_client.http import models as qmodels
from sentence_transformers import SentenceTransformer
from qdrant import init_qdrant, qdrant, get_agent_vector, COLLECTION_NAME

app = FastAPI(lifespan=init_qdrant)

@app.get("/registry", response_model=List[AgentMetadata])
async def get_registry():
    try:
        with open("agents.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    
@app.post("/register_agent", response_model=dict)
async def register_agent(agent: RegisterAgentRequest):
    agent_dict = agent.model_dump()

    # 1. Save to agents.json (fallback)
    json_path = Path("agents.json")
    if json_path.exists():
        with open(json_path, "r") as f:
            existing = [AgentMetadata(**a) for a in json.load(f)]
    else:
        existing = []

    # Remove duplicates by ID
    existing = [a for a in existing if a.id != agent.id]
    existing.append(agent)

    with open(json_path, "w") as f:
        json.dump([a.model_dump() for a in existing], f, indent=2)

    # 2. Save to Qdrant
    vector = get_agent_vector(agent.keywords, agent.domain)
    qdrant.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            qmodels.PointStruct(
                id=agent.id,
                vector=vector,
                payload=agent_dict  # clean and safe thanks to Pydantic
            )
        ]
    )

    return {"status": "registered"}
