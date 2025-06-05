from contextlib import asynccontextmanager
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from typing import List
from sentence_transformers import SentenceTransformer
import json
from .fallback import fallback_match_agents
from src.common.types import ScoredAgent, AgentMetadata

qdrant = QdrantClient("http://localhost:6333")
model = SentenceTransformer("all-MiniLM-L6-v2")  # Small and fast
COLLECTION_NAME = "agents"
VECTOR_SIZE = 384

@asynccontextmanager
async def init_qdrant():
    # Event executed before app startup
    if not qdrant.collection_exists(COLLECTION_NAME):
        qdrant.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=qmodels.VectorParams(
                size=VECTOR_SIZE,  # depends on embedding model
                distance=qmodels.Distance.COSINE
            )
        )
    yield

    # Event executed before app shutdown
    qdrant.close()

def get_agent_vector(keywords: List[str], domain: str) -> List[float]:
    combined_text = " ".join(keywords) + " " + domain
    return model.encode(combined_text).tolist()

def find_relevant_agents(prompt: str, top_k: int = 5) -> List[ScoredAgent]:
    vector = model.encode(prompt).tolist()

    results = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=vector,
        limit=top_k,
        with_payload=True
    )

    scored_agents = []
    for result in results:
        payload = result.payload
        scored_agent = ScoredAgent(
            id=payload["id"],
            domain=payload["domain"],
            endpoint=payload["endpoint"],
            keywords=payload["keywords"],
            score=result.score
        )
        scored_agents.append(scored_agent)

    return scored_agents

def smart_match_agents(prompt: str, top_k: int = 5) -> List[AgentMetadata]:
    try:
        return find_relevant_agents(prompt, top_k=5)
    except Exception as e:
        print("Qdrant not available, falling back:", e)
        return fallback_match_agents(prompt)

def load_agents_to_qdrant():
    with open("agents.json") as f:
        agents = json.load(f)

    if not qdrant.collection_exists(COLLECTION_NAME):
        qdrant.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=qmodels.VectorParams(size=VECTOR_SIZE, distance=qmodels.Distance.COSINE),
        )

    points = []
    for agent in agents:
        points.append(qmodels.PointStruct(
            id=agent["id"],
            vector=get_agent_vector(agent["keywords"], agent["domain"]),
            payload=agent
        ))

    qdrant.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"Upserted {len(points)} agents to Qdrant")
