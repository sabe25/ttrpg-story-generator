from __future__ import annotations

from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, BaseMessageChunk
from langchain_ollama import ChatOllama
from pydantic import BaseModel, ConfigDict


class ChatAgent(BaseModel):
    model: ChatOllama
    system_msg: str
    msg_history: list[BaseMessage]
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def create(cls, system_msg) -> ChatAgent:
        model = ChatOllama(
            model="deepseek-r1",
            temperature=0.4,
        )

        return cls(model=model, system_msg=system_msg, msg_history=[])

    def invoke(self, msg_str: str) -> BaseMessage:
        user_msg = HumanMessage(msg_str)
        self.msg_history.append(user_msg)
        ai_msg = self.model.invoke(self.msg_history)

        self.msg_history.append(ai_msg)

        return ai_msg

    def stream(self, msg_str: str) -> list[str]:
        chunks = []
        for chunk in self.model.stream(msg_str):
            chunks.append(chunk)
            yield chunk.content
        full_msg = AIMessage(content="".join(chunk.content for chunk in chunks))
        self.msg_history.append(full_msg)