import asyncio
import httpx
from models import AgentState, AgentTask, TraceEntry, AgentMetadata
from typing import List

async def call_agent(task: AgentTask):
    async with httpx.AsyncClient(timeout=60) as client:
        response = (await client.post(str(task.endpoint), json={"prompt": task.prompt})).json()
        return response["response"], task.agent_id

async def dispatcher_async(state: AgentState) -> AgentState:
    if not state.agent_tasks or state.collab_count >= 1:
        state.agent_tasks = []
        return state
    current_tasks = state.agent_tasks[:5]  # Parallel batch (2 for demo)
    tasks = [call_agent(task) for task in current_tasks]
    results = await asyncio.gather(*tasks)
    for result, agent_id in results:
        state.responses.append(result)
        state.trace.append(TraceEntry(
            step="dispatcher",
            action="called",
            collab_count=state.collab_count,
            details={"agent": agent_id, "response": result}
        ))
    state.agent_tasks = state.agent_tasks[len(current_tasks):]
    if state.agent_tasks:  # Collaboration round
        state.collab_count += 1
    state.trace.append(TraceEntry(
        step="dispatcher",
        action="updated",
        collab_count=state.collab_count,
        details={"remaining_tasks": [task.dict() for task in state.agent_tasks]}
    ))
    return state

def dispatcher(state: AgentState) -> AgentState:
    return asyncio.run(dispatcher_async(state))

if __name__ == "__main__":
    import asyncio
    
    state = AgentState(
        query="We need to document our CI/CD pipeline architecture and ensure it satisfies current compliance requirements. Can you help?",
        responses=[],
        collab_count=0,
        agent_tasks=[
            AgentTask(
                agent_id="JenkinsAgent",
                prompt="Describe the CI/CD pipeline.",
                endpoint="http://localhost:5001/respond"
            ),
            AgentTask(
                agent_id="DocsAgent",
                prompt="Summarize compliance requirements.",
                endpoint="http://localhost:5001/respond"
            )
        ],
        trace=[]
    )

    print(dispatcher(state))