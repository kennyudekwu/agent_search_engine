from fastapi import FastAPI
from langchain.chat_models import ChatOllama  # or ChatOpenAI, etc.
from langchain.schema import HumanMessage, SystemMessage
from common.types import PromptRequest, PromptResponse

app = FastAPI()

# Replace this with your actual local model wrapper
llm = ChatOllama(model="llama3.2")

@app.post("/respond", response_model=PromptResponse)
async def respond(payload: PromptRequest):
    # Optionally parse system/user roles from payload.prompt
    messages = [
        SystemMessage(content="You are a helpful assistant."),
        HumanMessage(content=payload.prompt)
    ]
    result = llm.invoke(messages)
    return {"response": result.content}