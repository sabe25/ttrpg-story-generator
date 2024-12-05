from camel.configs import ChatGPTConfig
from camel.models import ModelFactory
from camel.tasks import Task
from camel.types import ModelPlatformType, ModelType
from camel.workforce import Workforce

from src.agents.dungeon_master import DungeonMaster
from src.agents.monster_expert import MonsterExpert
from src.agents.scene_creator import SceneCreator
import xml.etree.ElementTree as ET

from src.agents.scene_writer import SceneWriter


def create_scene_structure(story: str) -> list:
    structure_agent = SceneCreator.create()
    response = structure_agent.create_story_scenes(story)
    print(response.msg.content)

    root = ET.fromstring(response.msg.content)
    elements_list = []
    for child in root:
        child_as_string = ET.tostring(child, encoding='unicode', method='xml')
        elements_list.append(child_as_string)

    return elements_list


def write_scenes(all_steps) -> list:
    scene_agent = SceneWriter.create()
    dm_agent = DungeonMaster.create()
    monster_expert = MonsterExpert.create()
    team = create_workforce(scene_agent.agent, dm_agent.agent, monster_expert.agent)


    previous_scene = None
    next_scene = None
    scene_list = []
    for cnt in range(0, len(all_steps) - 1):
        current_scene = all_steps[cnt]
        if cnt != len(all_steps) - 1:
            next_scene = all_steps[cnt + 1]
        print(current_scene, next_scene)
        scene_prompt = create_scene_prompt(current_scene, next_scene, previous_scene)
        print(scene_prompt)
        task = Task(content=scene_prompt)
        response = team.process_task(task)
        scene_description = response.result
        previous_scene = scene_description
        scene_list.append(scene_description)
        cnt += 1

    return scene_list


def create_scene_prompt(current_scene, next_scene, previous_scene: str | None) -> str:
    previous_prompt = f"""<previous_scene>    
                            <description>The previous scene contains information and cues that lead to the current scene. Incorporate and resolve these elements where necessary</description>
                            <content>{previous_scene}</content>
                        </previous_scene>"""
    next_prompt = f"""<next_scene>
                    <descritpion>The next scene introduces elements that the current scene may lead into. Include hints or setup information for this next scene without writing its description</descritpion>
                    <content>{next_scene}</content>
                </next_scene>"""
    prompt = f"""
        <task>
            <description>
                Create a Dungeons & Dragons scene description for the Dungeon Master to use during gameplay. Focus on the **current scene** using the provided context.
            </description>
            <context>
                <current_scene>
                    <description>The scene prompt for the current scene to describe</description>
                    <content>{current_scene}</content>
                </current_scene>
                {previous_prompt if previous_scene is not None else ""}
                {next_prompt if next_scene is not None else ""}
            </context>
            <instructions>
                - Write a description exclusively for the **current scene**.
                - Use clear, concise language suitable for Dungeon Masters to reference quickly.
                - Highlight elements that resolve cues from the previous scene.
                - Include details that naturally progress to the next scene, leaving space for player interaction.
                - Avoid describing the previous or next scenes directly.
            </instructions>
        </prompt>"""
    return prompt

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