from typing import Any, List
from langchain_core.runnables import Runnable
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
import httpx
from pydantic import HttpUrl

class RemoteChatAPI(Runnable):
    def __init__(self, endpoint_url: HttpUrl):
        self.endpoint_url = endpoint_url

    def invoke(self, input_: List[BaseMessage], **kwargs: Any) -> AIMessage:
        prompt = self._format_messages(input_)
        response = httpx.post(str(self.endpoint_url), json={"prompt": prompt})
        result_text = response.json()["response"]

        return AIMessage(content=result_text)

    def _format_messages(self, messages: List[BaseMessage]) -> str:
        return "\n".join([
            f"{m.type.upper()}: {m.content}" for m in messages
        ])