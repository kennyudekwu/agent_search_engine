from typing import Any, Dict, List
from src.models.models import AgentState, TraceEntry
from src.controllers.chat_model import RemoteChatAPI
from langchain.schema import (
    SystemMessage,
    HumanMessage
)
import asyncio

async def synthesizer_async(state: AgentState) -> None:
    llm = RemoteChatAPI(endpoint_url="http://localhost:5001/respond")
    # prompt = f"""
    # You are a synthesis model that combines multiple agent responses into a coherent, accurate, and concise summary that directly addresses the original user query. 
    # Do not use any other information other than the ones contained here in 'Responses'
    # """
    prompt ="""
    You are primarily a synthesis engine, secondarily a conversational assistant.

    Your goal is to generate a rich, factual, coherent and structured summary based only on the content in 'Responses'.

    - Avoid non-factual based generalizations.
    - Treat the responses as knowledge to be aggregated and reported like a search engine would.
    - Make sure your final output contains all the information contained in 'Responses'.
    
    Return the final output as a Markdown-formatted string.
    Terminate the conversation after the final output, do not ask any questions.
    """
    system_prompt = SystemMessage(content=prompt)
    human_prompt = HumanMessage(content=f"User Query: {state.query}\nResponses: {state.responses}")
    try:
        response = await llm.invoke([system_prompt, human_prompt])
        response = response.content
    except Exception as e:
        response = "Failed to generate response"
        raise ValueError(response + f": {e}")
    finally:
        state.trace.append(
            TraceEntry(
                step="synthesizer",
                action="combined responses",
                collab_count=state.collab_count,
                details={}
            )
        )
        state.responses = [response]
        return state
    
def synthesizer(state: AgentState) -> AgentState:
    return asyncio.run(synthesizer_async(state))


if __name__ == "__main__":
    state = AgentState(
        query="We need to document our CI/CD pipeline architecture and ensure it satisfies current compliance requirements. Can you help?",
        responses=[
            "A CI/CD (Continuous Integration and Continuous Delivery) pipeline is a series of automated processes that work together to streamline the development, testing, and deployment of software applications.\n\n"
            "**Components of a CI/CD Pipeline:**\n"
            "1. **Development**: Developers write and modify code.\n"
            "2. **Test**: Automated tests to validate functionality.\n"
            "3. **Build**: Compiled/packaged version is created.\n"
            "4. **Deployment**: Delivered to production.\n\n"
            "**Phases:** Triggers, Stage 1 (Development), Stage 2 (Test), Stage 3 (Build), Stage 4 (Deploy).\n\n"
            "**Characteristics:** Automated, Continuous, Integrative.\n"
            "**Benefits:** Faster delivery, better quality, fewer errors.\n"
            "**Tools:** Git, Maven, Gradle, Jenkins, Travis CI, CircleCI, etc.",

            "Compliance requirements can vary depending on industry, location, and regulations.\n\n"
            "**General Requirements:** Data protection, Health & Safety, Environment, Anti-Bribery.\n\n"
            "**Industry-Specific:**\n"
            "- Financial: AML, KYC, SOX\n"
            "- Healthcare: HIPAA, OSHA\n"
            "- Manufacturing: CPSIA, FDA\n"
            "- Tech: GDPR, CCPA\n\n"
            "**Regulatory:** Government contracts (FAR), Export controls (EAR/ITAR), Tax compliance.\n\n"
            "**Other Areas:** Insurance, Consumer protection, Employment law.\n"
            "Always check relevant laws and standards specific to your case."
        ],
        collab_count=0,
        agent_tasks=[],  # Not needed for the synthesizer
        trace=[
            TraceEntry(
                step="dispatcher",
                action="called",
                collab_count=0,
                details={"agent": "JenkinsAgent", "response": "..." }
            ),
            TraceEntry(
                step="dispatcher",
                action="called",
                collab_count=0,
                details={"agent": "DocsAgent", "response": "..." }
            ),
            TraceEntry(
                step="dispatcher",
                action="updated",
                collab_count=0,
                details={"remaining_tasks": []}
            )
        ]
    )
    print(synthesizer(state))
