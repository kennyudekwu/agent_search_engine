# ui.py

import streamlit as st
import httpx
import time
from agent_trace import render_trace

st.set_page_config(page_title="Agent Search", layout="centered")

st.markdown("## 🔍 Ask a question")
# Changed to st.text_input for Enter key submission
query = st.text_input("Query...", placeholder="Type your question...", label_visibility="collapsed")
placeholder = st.empty()

if query.strip():
    with st.spinner("Thinking..."):
        response = httpx.post("http://localhost:5002/search", json={"prompt": query}, timeout=100)
        result = response.json()
        markdown_response = result["responses"][0]  # assuming backend sends AgentState

    # Typing animation
    placeholder = st.empty()
    full = ""
    for char in markdown_response:
        full += char
        placeholder.markdown(full)
        time.sleep(0.01)

    render_trace(result["trace"])