from __future__ import annotations

from camel.agents import ChatAgent
from camel.messages import BaseMessage
from pydantic import BaseModel, ConfigDict

from src.agents.chat_agents_factory import create_chat_agent


class SceneWriter(BaseModel):
    agent: ChatAgent
    example_text: str
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

        example_text = f"""
                <examples>
                    <example>{examples[0]}</example>
                    <example>{examples[1]}</example>
                    <example>{examples[2]}</example>
                </examples>"""
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
            </role>""")
        agent = create_chat_agent(structure_msg)
        return cls(agent=agent, example_text=example_text)

    def write_scene(self, current_scene, next_scene, previous_scene: str | None) -> str:
        prompt = self.create_scene_prompt(current_scene, next_scene, previous_scene)
        refined_user_msg = BaseMessage.make_user_message("User", prompt)
        return self.agent.step(refined_user_msg).msg.content

    def adapt_to_feedback(self, feedback) -> str:
        prompt = f"""
<prompt>
    <description>
        I would like to suggest changes to the scene description. Please integrate them as best as possible.
    </description>
    <feedback>
        {feedback}
    </feedback>
</prompt>"""
        user_msg = BaseMessage.make_user_message("User", prompt)
        return self.agent.step(user_msg).msg.content


    def create_scene_prompt(self, current_scene, next_scene, previous_scene: str | None) -> str:
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

