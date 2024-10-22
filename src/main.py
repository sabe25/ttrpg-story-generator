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
from io import BytesIO

from camel.memories import LongtermAgentMemory, ScoreBasedContextCreator, ChatHistoryBlock, VectorDBBlock, MemoryRecord, \
    ChatHistoryMemory
from camel.types import ModelType, OpenAIBackendRole
from camel.workforce import Workforce
from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.tasks import Task
from camel.utils import print_text_animated, OpenAITokenCounter
from camel.loaders.base_io import TxtFile
from camel.loaders.unstructured_io import UnstructuredIO as uio
from sympy import refine
from torch import while_loop


def main(model=None, chat_turn_limit=10) -> None:

    workforce = Workforce("Dungeons and Dragons creative team")

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
                "Here is the story prompt: Over the forest a thick fog appears. Animals from the forest behave unnatural even aggresive. "
                "A demon is manipulating the area. Heros you need to help us get rid of that demon and rescue the forest.",
                id="0")

    # task = workforce.process_task(task)

    # Read a pdf file from disk
    with open("../dnd-one-shot-example.txt", "rb") as file:
        file_content = BytesIO(file.read())
        file_content.name = "dnd-one-shot-example.txt"

    # Use the read_file function to create an object based on the file extension
    file_obj = TxtFile.from_bytes(file_content, file_content.name)

    # Once you have the File object, you can access its content
    print(file_obj.docs[0]["page_content"])


    sum_msg = BaseMessage.make_assistant_message(
        "Content Creator",
        "You are a content creator that knows how to write DnD one-shots."
    )

    sum_agent = ChatAgent(sum_msg)

    ## Memory
    # Initialize the memory
    memory = ChatHistoryMemory(
        context_creator=ScoreBasedContextCreator(
            token_counter=OpenAITokenCounter(ModelType.GPT_4O_MINI),
            token_limit=1024,
        ),
    )
    records = [MemoryRecord(
        message=BaseMessage.make_user_message(
            role_name="Tutor",
            meta_dict=None,
            content="I'm going to show you how a dnd one-shot is structured. I would like you to focus on how "
                    "the story progression is written and how the scenes are structured. ",
        ),
        role_at_backend=OpenAIBackendRole.USER,
    )]
    # Set clean options
    options = [
        ('replace_unicode_quotes', {}),
        ('clean_dashes', {}),
        ('clean_non_ascii_chars', {}),
        ('clean_extra_whitespace', {}),
    ]

    cleaned_text = uio.clean_text_data(text=file_obj.docs[0]["page_content"], clean_options=options)
    records.append(MemoryRecord(
        message=BaseMessage.make_user_message(
            role_name="Tutor",
            meta_dict=None,
            content=cleaned_text,
        ),
        role_at_backend=OpenAIBackendRole.USER,
    ))

    memory.write_records(records)
    sum_agent.memory = memory

    msg = BaseMessage.make_user_message("User", "What is the story about?")
    response = sum_agent.step(msg)
    print(response.msg)

def refine_user_input(max_steps=10) -> None:
    refinement_msg = BaseMessage.make_user_message(
        "Story arch writer",
        "You are a creative writer focused on writing story arch for dnd one-shots. "
        "You create broad overviews of story archs. For you important is that each story has the following features."
        "A plot hook, something that the player want to help or solve the problem"
        "The environment, where the story is told and the vibe of the surroundings induce a certain feeling."
        "The setting, that set the overall theme of the story. "
        "Surprice Elements are also fun but optional, it is something the player are not expecting."
        "If the setting is not further discussed assume that it is a medival high fantasy setting."
        "A thread, something the players are eager to solve, whether it is a social conflict or existencial thread to a village you are open to it all."
    )
    refinement_agent = ChatAgent(refinement_msg)

    user_msg = input("Please specify your story.")

    initial_user_str = (
            "I will provide a description of a story arc."
            "If the input is not satisfying you then ask specific questions about the story."
            "Never forget: Do not summarize the story until asked."
            "Never forget: If you have not further questions respond with '<NO_QUESTION>'"
                        + user_msg)

    initial_user_msg = BaseMessage.make_user_message("User", initial_user_str)
    response = refinement_agent.step(initial_user_msg,)

    for i in range(max_steps):
        if i == max_steps - 1:
            break
        if "<NO_QUESTION>" in response.msg:
            break

        # print_text_animated(response.msg.content)
        print(response.msg.content)

        refined_user_input = input("Please answer the given questions.")
        refined_user_msg = BaseMessage.make_user_message("User",
                                                         "Here is an update one the story we build."
                                                         ""
                                                         + refined_user_input)
        response = refinement_agent.step(refined_user_msg)

    result = refinement_agent.step(BaseMessage.make_user_message("User", "Now that you have all important information please generate"
                                                                "a story description within 400 words."))
    print_text_animated("Thank you for your input. Here is what i got: " + result.msg.content )
    print("Thank you for your input. Here is what i got: " + result.msg.content )

if __name__ == "__main__":
    # main()
    refine_user_input()