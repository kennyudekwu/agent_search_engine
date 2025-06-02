from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List
from langchain.chat_models import ChatOllama  # or ChatOpenAI, etc.
from langchain.schema import HumanMessage, SystemMessage

app = FastAPI()

# Replace this with your actual local model wrapper
llm = ChatOllama(model="llama3.2")

class PromptRequest(BaseModel):
    prompt: str

class PromptResponse(BaseModel):
    response: str

@app.post("/respond", response_model=PromptResponse)
async def respond(payload: PromptRequest):
    # Optionally parse system/user roles from payload.prompt
    messages = [
        SystemMessage(content="You are a helpful assistant."),
        HumanMessage(content=payload.prompt)
    ]
    result = llm.invoke(messages)
    return {"response": result.content}