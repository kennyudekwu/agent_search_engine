import streamlit as st
import httpx
from pydantic import BaseModel
from typing import List, Dict

class AgentTask(BaseModel):
    agent_id: str
    prompt: str

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

async def ui():
    st.title("Agent-Powered Search Engine")
    query = st.text_input("Enter query")
    if st.button("Search"):
        with httpx.AsyncClient() as client:
            response = await client.post("http://localhost:5002/search", json={"query": query})
            state = AgentState(**response.json())
        st.write("**Response**")
        st.write(state.responses[0])
        st.write("**Collaboration Trace**")
        for entry in state.trace:
            st.write(f"{entry.step}: {entry.action} (Collab Count: {entry.collab_count})")
            st.json(entry.details)


if __name__ == "__main__":
    ui()