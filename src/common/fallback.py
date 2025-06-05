import json
from src.common.types import AgentMetadata, ScoredAgent
from typing import List
from rapidfuzz import fuzz
from operator import itemgetter
import os
from pathlib import Path

def fallback_match_agents(prompt: str, file_path: str = os.path.join(Path(os.path.dirname(__file__)).parent, "store/agents.json"), top_k: int = 5) -> List[AgentMetadata]:
    with open(file_path, "r") as f:
        raw_agents = json.load(f)

    agents_with_scores = []
    for agent in raw_agents:
        score = max(
            fuzz.partial_ratio(prompt.lower(), keyword.lower())
            for keyword in agent.get("keywords", [])
        )
        if score > 30:  # basic relevance threshold
            agents_with_scores.append((agent, score))

    # Sort by score descending and take top_k
    top_agents = sorted(agents_with_scores, key=itemgetter(1), reverse=True)[:top_k]

    return [ScoredAgent(**agent_dict, score=score) for agent_dict, score in top_agents]
