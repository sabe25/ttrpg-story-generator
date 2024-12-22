from camel.agents import ChatAgent
from camel.models import (
    ModelFactory,
)
from camel.types import ModelPlatformType

ollama_model = ModelFactory.create(
    model_platform=ModelPlatformType.OLLAMA,
    model_type="llama3.2",
    model_config_dict={"temperature": 0.4},
)

def create_chat_agent(msg) -> ChatAgent:
    return ChatAgent(model=ollama_model, system_message=msg)