from langchain.chat_models import ChatOpenAI
from pydantic import RootModel
import httpx, json
from models import AgentState, AgentTask, TraceEntry
from langchain.chat_models import ChatOllama  # or ChatOpenAI, ChatLiteLLM, etc.
from langchain.schema import (
    SystemMessage,
    HumanMessage,
    AIMessage,
)
from qdrant import smart_match_agents
from typing import List
from models import AgentMetadata
from fastapi import FastAPI
from chat_model import RemoteChatAPI
from langchain.output_parsers import PydanticOutputParser

class AgentTaskList(RootModel[List[AgentTask]]):
    pass

parser = PydanticOutputParser(pydantic_object=AgentTaskList)

async def supervisor(state: AgentState) -> AgentState:
    llm = RemoteChatAPI(endpoint_url="http://localhost:5001/respond")

    registry: List[AgentMetadata] = smart_match_agents(state.query, top_k=50)
    agent_registry_str = "\n".join([
        "- " + ", ".join(f"{key}: {value}" if not isinstance(value, list) else f"{key}: [{', '.join(value)}]"
        for key, value in agent.model_dump().items())
        for agent in registry
    ])

    prompt = f"""
    You are a helpful agent coordination assistant.
    Your job is to read a user query and decide which agents from the registry should be called.
    Each task must have the following format:

    [
        {{
            "agent_id": "<agent ID>",
            "prompt": "<custom prompt specific to agent expertise to send to this agent for better context>"
            "endpoint": "<endpoint of agent to call>"
        }},
        ...
    ]

    Respond with JSON only.
    """

    system_prompt = SystemMessage(content=prompt)

    # prompt = (
    #     f"You are a supervisor in a multi-agent system. Your job is to select agents for the query:\n"
    #     f"'{state.query}'\n"
    #     f"Here is the agent registry:\n{agent_registry_str}\n\n"
    #     f"Choose the most relevant agents and generate a custom prompt for each. "
    #     # f"Include at most 1 round of collaboration. Respond with a JSON list of objects with 'agent_id' and 'prompt'."
    # )

    human_prompt = HumanMessage(content=f"User Query: {state.query}\nAvailable Agents:\n{agent_registry_str}")
    try:
        response = llm.invoke([system_prompt, human_prompt])
        parsed = parser.parse(response.content)
        state.agent_tasks = parsed.root
    except Exception as e:
        # could consider retrying to get compatible response before failing
        raise ValueError(f"LLM response could not be parsed: {response.content}") from e

    state.responses = []
    state.collab_count = 0
    state.trace = [
        TraceEntry(
            step="supervisor",
            action="planned",
            collab_count=0,
            details={"tasks": [task.model_dump() for task in state.agent_tasks]}
        )
    ]

    return state

if __name__ == "__main__":
    import asyncio
    state = AgentState(query="test query", responses=[], collab_count=0, agent_tasks=[], trace=[])
    print(asyncio.run(supervisor(state)))
