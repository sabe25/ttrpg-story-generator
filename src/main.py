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
from camel.utils import print_text_animated
from camel.workforce import Workforce


def main(model=None, chat_turn_limit=10) -> None:

    workforce = Workforce("Dungeons and Dragons creative team"
                          ## define new_agent_kwargs
                          )

    story_msg = BaseMessage.make_user_message(
        "Story writer",
        "You want to write emerging medival stories that can be used in a DnD setting." +
        " You restrict your stories to the scope of dnd one-shots. You create diverse characters and know how to implement"+
        " drama into characters."
    )
    story_agent = ChatAgent(story_msg)

    workforce.add_single_agent_worker(
      "An agent that write medival stories. Can define the story archs, develop npc characters",
      worker=story_agent,
    )

    puzzle_msg = BaseMessage.make_user_message(
        "Puzzle creator",
        "You are a creative writer focused on puzzles in roleplaying. Your puzzles are organized in"
        "social encounters, dungeon traps and environmental challanges. You always provide the DC (difficulty level) if necessary. "
        "You always provide a description how the party could solve the puzzle. Give at least 3 possible solutions to a puzzle"
    )
    puzzle_agent = ChatAgent(puzzle_msg)

    workforce.add_single_agent_worker(
      "An agent that creates roleplaying puzzles. Ask this agent for engaging social encounters, dungeon traps and environmental challanges.",
      worker=puzzle_agent,
    )

    task = Task(content="Create a original one-shot for the roleplaying game Dungeons and Dragons. "
                "The result should be a 600 words document. It is organised in story intro and the different scences."
                "Here is the story prompt: **Title: Whispers of the Lost Church**"
                "In the heart of a dense, shadowy forest lies the quaint village of Eldergrove, a place once vibrant with laughter and warmth. However, a dark cloud now looms over the villagers, for their beloved church has mysteriously vanished, taking with it the solace and guidance it provided. The villagers, desperate and frightened, turn to a group of brave heroes for help, pleading with them to uncover the truth behind the church's disappearance."
                "As the heroes arrive, they are greeted by a palpable sense of dread. The once-bustling village square is now eerily silent, the air thick with the whispers of restless spirits. The villagers recount chilling tales of ghostly apparitions haunting their homes at night, their mournful wails echoing through the trees. The absence of the church has left a void, awakening the spirits of the past who seek resolution for their unfinished business."
                "The heroes must navigate the tangled paths of the forest, where shadows dance and the trees seem to whisper secrets. As they delve deeper into the mystery, they encounter strange phenomena: flickering lights in the distance, fleeting glimpses of spectral figures, and the feeling of being watched. The forest itself becomes a character in the story, its dense foliage and twisting paths both a guide and a trap."
                "As the heroes investigate, they learn that the priest, in a fit of rage over the villagers' doubts and fears, teleported the church to an unknown realm, believing it would teach them a lesson. However, the unintended consequence has unleashed the spirits of those who once sought refuge within its walls. The heroes must confront the priest, who is now tormented by his actions, and persuade him to help restore balance to Eldergrove."
                "In a climactic confrontation, the heroes must navigate the emotional turmoil of the priest and the anguished spirits, seeking a way to bring the church back and lay the restless souls to rest. With courage, compassion, and cleverness, they will uncover the truth behind the hauntings and restore peace to the village.",
                id="0")

    task = workforce.process_task(task)
    print_text_animated(task.content)

def refine_user_input(max_steps=10) -> str:
    refinement_msg = BaseMessage.make_assistant_message(
        "Story arch writer",
        "You are a creative writer focused on writing story arch for dnd one-shots. "
        "You create broad overviews of story archs. For you important is that each story has the following features."
        "A plot hook, something that the player want to help or solve the problem"
        "The environment, where the story is told."
        "Additionally these elements could improve the story."
        "Surprice Elements are also fun but optional, it is something the player are not expecting."
        "Interesting Characters, brings depth and live to the story"
        "A thread, something the players are eager to solve, whether it is a social conflict or existencial thread to a village you are open to it all."
    )
    refinement_agent = ChatAgent(refinement_msg)

    user_msg = input("Please specify your story.")

    initial_user_str = (
            "I will provide a description of a story arc."
            "The input should cover all information necessary to build the story. It should fullfill your important features."
            # "Think about the input as a suggestion for the story. Ask yourself: Does the input provide enough information to build a good story?"
            "If not then ask further questions about the story."
            "Never forget: Do not summarize the story until asked."
            "Never forget: If you have not further questions respond with '<NO_QUESTION>'"
            "Here is the user message:"
            + "{{" + user_msg + "}}")

    initial_user_msg = BaseMessage.make_user_message("User", initial_user_str)
    response = refinement_agent.step(initial_user_msg, )

    for i in range(max_steps):
        if i == max_steps - 1:
            break
        if "<NO_QUESTION>" in response.msg:
            break

        # print_text_animated(response.msg.content)
        print(response.msg.content)

        refined_user_input = input("Please answer the given questions.")
        refined_user_msg = BaseMessage.make_user_message(
            "User",
            "Here is an update one the story we build."
            + "{{" + refined_user_input + "}}")
        response = refinement_agent.step(refined_user_msg)

    result = refinement_agent.step(
        BaseMessage.make_user_message(
            "User",
            "Give a story overview with the information give by the user."
            "Structure the summary in the following blocks: player hook, story summary, important characters."
            "The story summary should give detailed information about necessary story elements."))

    # print_text_animated("Thank you for your input. Here is what i got: " + result.msg.content)
    print("Thank you for your input. Here is what i got: " + result.msg.content)
    return result.msg.content

def create_scene_structure(story: str) -> list:
    structure_msg = BaseMessage.make_assistant_message(
        "Scene creator",
        "You are outlining the story in steps. Each step/encounter drives the story forward or reveal more information."
        "You have three broad encounter options: combat, NPC interaction, and exploration (traps, puzzles, navigation). The goal is to make sure you don't have too much of the same stuff back-to-back."
    )
    structure_agent = ChatAgent(structure_msg)

    # create first and last scene
    firstLastResponse = structure_agent.step(
        BaseMessage.make_user_message(
            "User",
            "Given the story, define the first and last scene/encounter."
            "Each scene should be described in one sentence and should be labeled with an encounter option."
            "For example: "
            "- Follow the thief through the busteling city alleys (navigation)"
            "- Sorcerous orbs speaking in riddles (puzzle)"
            "- Secretive librarian (NPC interaction)"
            "- Final fight with thief and his friends (combat)"
            "Here is the story: "
            "{{" + story + "}}"
            "Define the first and last scene/encounter in the format of:"
            "Story Start: <first scene>"
            "Story End: <last scene>"))

    rows = firstLastResponse.msg.content.split("\n")

    # create in between steps
    response = structure_agent.step(
        BaseMessage.make_user_message(
            "User",
            "You need to find 4 to 8 encounters inbetween the first and the last scene."
            "Each step should drive the story forward and offers clues to the next step"
            "They should be ordered according to how the story unfolds"
            "Do not include the first and the last step which are"
            + firstLastResponse.msg.content +
            "For example: "
            "2. Follow the thief through the busteling city alleys (navigation)"
            "3. Sorcerous orbs speaking in riddles in the library (puzzle)"
            "4. Secretive librarian (NPC interaction)"
        )
    )
    print(response.msg.content)

    transition_steps = response.msg.content.split("\n")
    all_steps = [rows[0], *transition_steps, rows[1]]
    print(all_steps)

    return all_steps

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
    story = refine_user_input()
    all_steps = create_scene_structure(story)
    write_scenes(all_steps, story)
