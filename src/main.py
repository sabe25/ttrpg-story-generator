# =========== Copyright 2023 @ CAMEL-AI.org. All Rights Reserved. ===========
# Licensed under the Apache License, Version 2.0 (the “License”);
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an “AS IS” BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =========== Copyright 2023 @ CAMEL-AI.org. All Rights Reserved. ===========

from camel.agents import ChatAgent
from camel.configs import ChatGPTConfig
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.tasks import Task
from camel.types import ModelType, OpenAIBackendRole, ModelPlatformType
from camel.workforce import Workforce

from src.workflow import prepare, scenes

def create_scene_writer_agent():
    # load example scenes
    examples = []
    with open("../res/scene-example-1.txt", "r") as file:
        examples.append(file.read())

    with open("../res/scene-example-2.txt", "r") as file:
        examples.append(file.read())

    with open("../res/scene-example-3.txt", "r") as file:
        examples.append(file.read())

    # setup scene writer
    scene_msg = BaseMessage.make_assistant_message(
        "Scene writer",
        "You write descriptions for scenes played in dnd. "
        "You are writing for the Dungeon Master(DM), not the players. "
        "Remember to make the information easy and fast for the DM to read."
        "The scene you are writing is reference material, not a novel. The DM will be using this live at the table to run games. Split your information out into bullet points and lists, use bolding, get to the point as fast as you can, and cut anything that doesn't matter to the here-and-now (do not explain the history of each room)."
        "Here are examples of how to do it:"
        ""
        "## Example 1: "
        "{{"+ examples[0] + "}}"
        "## Example 2:"
        "{{"+ examples[1] + "}}"
        "## Example 3:"
        "{{"+ examples[2] + "}}"
        "Don't forget you are writing descriptions for dnd scenes."
        "Never use double quotes \" to quote statements of characters. Use pointy brackets <> instead." 
        "Return in valid json format like: {\"content\": \"scene description\"}"
    )
    return ChatAgent(scene_msg)


def single_agent_write_scene(scene_agent, prompt):
    scene_response = scene_agent.step(BaseMessage.make_user_message(
        "User",
        prompt
    ))
    return scene_response.msg.content

def workforce_write_scene(scene_agent, prompt, story):
    dm_msg = BaseMessage.make_assistant_message(
        "Dungeon Master",
        "You are the dungeon master runnng the discussed game. You want to create an emerging and interesting experience for the players."
        "You need to know how the story will unfold. Which steps are optional and which one can be run in different order."
    )
    dm_agent = ChatAgent(dm_msg)

    bm_msg = BaseMessage.make_assistant_message(
        "Beast Master",
        "You know everything about how to balance a good fight and which monsters are allowed in an dnd game."
        "Make sure the right terms are used when adressing monsters or enemies."
    )
    bm_agent = ChatAgent(bm_msg)

    story_msg = BaseMessage.make_assistant_message(
        "Story creator",
        "You write background stories for dnd campaigns. You understand the scope of a one-shot and how much story can be told in such."
        "You keep the story compact yet multiple connection are allowed."
    )
    story_agent = ChatAgent(story_msg)
    story_agent.update_memory(BaseMessage.make_user_message("user", story), OpenAIBackendRole.USER)

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
      worker=bm_agent,
    )
    workforce.add_single_agent_worker(
      "Agent that knows the background information of the story.",
      worker=story_agent,
    )
    task = Task(content=prompt)
    response = workforce.process_task(task)
    print("content: " + response.content)
    print("result: " + response.result)
    return response.result

# write a scene
def write_scene(scene_agent, current_scene, next_scene, previous_scene, story) -> str:
    previous_prompt = "The previous scene contains information and cues that leads to the current scene. Incoorporate these as needed and resolve them. Here is the previous scene: {{" + (
                previous_scene or "") + "}}. "
    next_prompt = "The scene description should contain information that leads to the next scene. Here is the next scene: {{" + (
                next_scene or "") + "}}. " if next_scene is not None else ""
    prompt = ("Create a scene description. "
              "Here is the prompt for the current scene you should write a description about: {{" + current_scene + "}}"
              + (previous_prompt if previous_scene is not None else "")
              + next_prompt +
              "Do not write a description for the next scene or the previous scene."
              "Don't forget you are writing a description for the current scene."
              )
    scene_response_content = workforce_write_scene(scene_agent, prompt, story)
    # scene_response_content = single_agent_write_scene(scene_agent, prompt)

    print(scene_response_content + "/n")

    return scene_response_content

def write_scenes(all_steps, story) -> None:
    scene_agent = create_scene_writer_agent()

    cnt = 0
    previous_scene = None
    next_scene = None
    scene_list = []
    for cnt in range(0, len(all_steps) - 1):
        current_scene = all_steps[cnt]
        if cnt != len(all_steps) - 1:
            next_scene = all_steps[cnt + 1]

        current_scene_desc = write_scene(scene_agent, current_scene, next_scene, previous_scene, story)
        previous_scene = current_scene_desc
        scene_list.append(current_scene_desc)
        cnt += 1


if __name__ == "__main__":
    # main()
    story = prepare.refine_user_input()
    all_steps = scenes.create_scene_structure(story)
    write_scenes(all_steps, story)
