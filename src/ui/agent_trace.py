import streamlit as st
import hashlib

# Emojis to assign to agents deterministically
EMOJI_POOL = [
    "🧱", "📄", "🔐", "📦", "⚙️", "💬", "📊", "🧩", "🎯",
    "🔎", "🚀", "💡", "🛠️", "🎓", "📚", "💻", "📁", "🧬", "📌",
    "🗂️", "🧾", "🗃️", "📋", "🔍", "🧰", "🧮", "📈", "🪵", "🗒️"
]

def get_agent_icon(agent_id: str) -> str:
    h = int(hashlib.md5(agent_id.encode()).hexdigest(), 16)
    return EMOJI_POOL[h % len(EMOJI_POOL)]

def render_trace(trace: list):
    STEP_ICONS = {
        "supervisor": "🧠",
        "dispatcher": "🤖",
        "synthesizer": "🧩"
    }

    st.markdown("## 🧭 Interaction Trace")

    agent_ids = set()  # Track agents for optional sidebar legend

    for entry in trace:
        step = entry.get("step", "unknown")
        action = entry.get("action", "")
        count = entry.get("collab_count", 0)
        details = entry.get("details", {})

        icon = STEP_ICONS.get(step, "📦")
        title = f"{icon} **{step.title()}** → *{action.replace('_', ' ')}* (collab count: `{count}`)"

        with st.expander(title, expanded=False):
            if not details:
                st.markdown("_No additional details_")
                continue

            # Supervisor step — show agent planning
            if step == "supervisor" and "tasks" in details:
                st.markdown("### 🧠 Agent Plan")
                for task in details["tasks"]:
                    agent_id = task["agent_id"]
                    agent_ids.add(agent_id)
                    agent_icon = get_agent_icon(agent_id)
                    st.markdown(
                        f"{agent_icon} **{agent_id}**\n\n"
                        f"- Prompt: `{task['prompt']}`\n"
                        f"- Endpoint: `{task['endpoint']}`"
                    )

            # Dispatcher called agent
            elif step == "dispatcher" and "response" in details:
                agent = details.get("agent", "Unknown")
                agent_ids.add(agent)
                agent_icon = get_agent_icon(agent)
                st.markdown(f"### {agent_icon} Response from `{agent}`")
                st.code(details["response"], language="markdown")

            # Dispatcher updated
            elif step == "dispatcher" and "remaining_tasks" in details:
                remaining = details["remaining_tasks"]
                st.markdown("### 📋 Remaining Tasks")
                if remaining:
                    for t in remaining:
                        st.markdown(f"- `{t}`")
                else:
                    st.markdown("_No remaining tasks._")

            # Synthesizer or other steps
            else:
                st.markdown("### 📄 Details")
                for k, v in details.items():
                    if isinstance(v, str) and len(v) > 120:
                        st.code(v, language="markdown")
                    elif isinstance(v, list):
                        for item in v:
                            if isinstance(item, dict):
                                st.markdown("- " + ", ".join(f"`{ik}`: `{iv}`" for ik, iv in item.items()))
                            else:
                                st.markdown(f"- `{item}`")
                    elif isinstance(v, dict):
                        st.json(v)
                    else:
                        st.markdown(f"- `{k}`: `{v}`")

    # Optional: show agent icon legend in sidebar
    with st.sidebar:
        if agent_ids:
            st.markdown("### 🧾 Experts Consulted")
            for aid in sorted(agent_ids):
                st.markdown(f"{get_agent_icon(aid)} `{aid}`")