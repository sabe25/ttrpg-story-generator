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
from camel.loaders.base_io import PdfFile


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
    with open("../dragon_icespire_peak_preview.pdf", "rb") as file:
        file_content = BytesIO(file.read())
        file_content.name = "dragon_icespire_peak_preview.pdf"

    # Use the read_file function to create an object based on the file extension
    file_obj = PdfFile.from_bytes(file_content, file_content.name)

    # Once you have the File object, you can access its content
    print(file_obj.docs[3]["page_content"])
    file_obj.docs.pop(0)
    file_obj.docs.pop(1)
    file_obj.docs.pop(2)

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
    for page in file_obj.docs:
        records.append(MemoryRecord(
            message=BaseMessage.make_user_message(
                role_name="Tutor",
                meta_dict=None,
                content=page["page_content"],
            ),
            role_at_backend=OpenAIBackendRole.USER,
        ))

    memory.write_records(records)
    # Get context for the agent
    context, token_count = memory.get_context()

    print(context)
    print(f"Retrieved context (token count: {token_count}):")
    for message in context:
        print(f"{message}")
    # sum_agent.memory = memory




if __name__ == "__main__":
    main()