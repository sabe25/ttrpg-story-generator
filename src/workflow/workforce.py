from camel.configs import ChatGPTConfig
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType
from camel.workforce import Workforce


def create_workforce(scene_agent, dm_agent, monster_expert) -> Workforce:
    # Set the LLM model type and model config
    model_platform = ModelPlatformType.OPENAI
    model_type = ModelType.GPT_4O_MINI
    model_config = ChatGPTConfig(
        temperature=0.8,  # the sampling temperature; the higher the more random
        n=3,  # the no. of completion choices to generate for each input
    )
    # Create the backend model
    model = ModelFactory.create(
        model_platform=model_platform,
        model_type=model_type,
        model_config_dict=model_config.as_dict())

    workforce = Workforce(
        "Dungeons and Dragons creative team",
        # task_agent_kwargs= {"model": model},
        new_worker_agent_kwargs={"model": model},
        # coordinator_agent_kwargs={"model": model},
    )

    workforce.add_single_agent_worker(
        "Agent that specializes in crafting intricate and immersive scene descriptions for storytelling, focusing on plot development and thematic elements.",
        worker=scene_agent,
    )
    workforce.add_single_agent_worker(
        "Agent that will use the scene description to run a game of dnd. Acts as a validator for the scenes.",
        worker=dm_agent,
    )
    workforce.add_single_agent_worker(
        "Agent that knows everything about monsters and how to balance fights.",
        worker=monster_expert,
    )

    return workforce