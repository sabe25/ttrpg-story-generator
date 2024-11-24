from __future__ import annotations

from camel.agents import ChatAgent
from camel.messages import BaseMessage
from pydantic import BaseModel, ConfigDict

class SceneWriter(BaseModel):
    agent: ChatAgent
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def create(cls) -> SceneWriter:
        # load example scenes
        examples = []
        with open("../res/scene-example-1.txt", "r") as file:
            examples.append(file.read())

        with open("../res/scene-example-2.txt", "r") as file:
            examples.append(file.read())

        with open("../res/scene-example-3.txt", "r") as file:
            examples.append(file.read())

        structure_msg = BaseMessage.make_assistant_message(
            "Scene writer",
            f"""
            <role>
                <description>
                    You are an expert Dungeon Master (DM) scene description writer for Dungeons & Dragons games. Your role is to transform scenes from story outlines into detailed, actionable descriptions specifically tailored for a DM to use during gameplay.
                </description>
                <guidelines>
                    <focus>
                        - Provide concise, organized descriptions that prioritize what is relevant for live gameplay.
                        - Avoid unnecessary backstory or verbose details that are not critical for the scene.
                    </focus>
                    <presentation>
                        - Use bullet points for clarity and quick DM reference.
                        - Highlight key terms with **bold text**.
                        - Provide ready-to-use flavor text where applicable, clearly marked as optional.
                    </presentation>
                </guidelines>
                <examples>
                    <example>{examples[0]}</example>
                    <example>{examples[1]}</example>
                    <example>{examples[2]}</example>
                </examples>
            </role>""")
        agent = ChatAgent(structure_msg)
        return cls(agent=agent)
