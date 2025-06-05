from langgraph.graph import StateGraph, END
from .supervisor import supervisor
from .dispatcher import dispatcher
from .synthesizer import synthesizer
from src.common.types import AgentState

workflow = StateGraph(AgentState)
workflow.add_node("supervisor", supervisor)
workflow.add_node("dispatcher", dispatcher)
workflow.add_node("synthesizer", synthesizer)
workflow.set_entry_point("supervisor")
workflow.add_conditional_edges("supervisor", lambda state: "dispatcher")
workflow.add_conditional_edges("dispatcher", lambda state: "dispatcher" if state.agent_tasks and state.collab_count < 1 else "synthesizer")
workflow.add_edge("synthesizer", END)
app = workflow.compile()

async def main():
    state = AgentState(query="We need to document our CI/CD pipeline architecture and ensure it satisfies current compliance requirements. Can you help?", responses=[], collab_count=0, agent_tasks=[], trace=[])
    return await app.ainvoke(state)

if __name__ == "__main__":
    import asyncio
    result = asyncio.run(main())
    print(result["responses"][0])