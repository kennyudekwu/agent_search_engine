from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
qdrant = QdrantClient("http://localhost:6333")

COLLECTION_NAME = "agents"

def match_agents(prompt: str, top_k: int = 5):
    vector = model.encode(prompt).tolist()

    results = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=vector,
        limit=top_k,
        with_payload=True,
    )

    matched_agents = []
    for result in results:
        payload = result.payload
        matched_agents.append({
            "id": payload["id"],
            "skills": payload.get("skills", []),
            "prompt_template": payload.get("prompt_template", None),
            "score": result.score
        })

    return matched_agents

def craft_agent_prompts(original_prompt: str, agents: List[Dict]) -> Dict[str, str]:
    prompts = {}

    for agent in agents:
        template = agent.get("prompt_template")

        if template:
            prompt = template.format(query=original_prompt)
        else:
            prompt = f"Please address the following from your domain expertise: {original_prompt}"

        prompts[agent["id"]] = prompt

    return prompts

# def craft_agent_prompts(original_prompt: str, agents: List[Dict]) -> Dict[str, str]:
#     prompts = {}

#     for agent in agents:
#         prompts[agent["id"]] = generate_agent_prompt(agent)

#     return prompts

# def generate_agent_prompt(agent: Dict) -> str:
#     pass