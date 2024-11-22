from __future__ import annotations

from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.responses import ChatAgentResponse
from pydantic.dataclasses import dataclass


@dataclass
class StoryArchWriter:
    agent: ChatAgent

    @classmethod
    def create(cls) -> StoryArchWriter:
        with open("./agents/story_arch_writer_prompt.txt", "r") as file:
            prompt = file.read()

        refinement_msg = BaseMessage.make_assistant_message(
            "Story arch writer",
            prompt
        )

        agent = ChatAgent(refinement_msg)
        return cls(agent=agent)

    def start_refinement(self, user_msg) -> ChatAgentResponse:
        initial_user_str = (
            f"""<task>
                    Verify whether the provided story arc includes all necessary elements for a Dungeons & Dragons one-shot narrative.
                </task>
                <criteria>
                    <element>
                        <name>Plot Hook</name>
                        <description>A compelling reason to engage the players in the story.</description>
                    </element>
                    <element>
                        <name>Environment/Setting</name>
                        <description>A defined and immersive location where the story unfolds.</description>
                    </element>
                    <element>
                        <name>Main Thread/Conflict</name>
                        <description>A clear goal or conflict driving the story.</description>
                    </element>
                    <element>
                        <name>NPCs</name>
                        <description>Engaging non-player characters that add depth and support the narrative.</description>
                    </element>
                    <element>
                        <name>Surprise Elements</name>
                        <description>Optional twists or unexpected elements to intrigue players.</description>
                    </element>
                </criteria>
                <instructions>
                    <rule>Do not include player characters (heroes) in the assessment, as they are played by real individuals.</rule>
                    <rule>Do not summarize the story unless explicitly asked.</rule>
                    <rule>If all elements are covered and no further questions are needed, respond with "<NO_QUESTION>".</rule>
                    <rule>If any element is missing or unclear, ask specific questions to gather more details.</rule>
                    <rule>If any element is missing, provide ready-to-use examples tailored to fit the story's theme and tone.</rule>
                </instructions>
                <input>
                    <description>Here is the user message:</description>
                    <content>{user_msg}</content>
                </input>""")

        initial_user_msg = BaseMessage.make_user_message("User", initial_user_str)
        return self.agent.step(initial_user_msg, )

    def refine_furhter(self, user_msg) -> ChatAgentResponse:
        refined_user_msg = BaseMessage.make_user_message(
            "User",
            "Here is an update one the story we build."
            + "{{" + user_msg + "}}")
        return self.agent.step(refined_user_msg)

    def summarise(self) -> ChatAgentResponse:
        message = BaseMessage.make_user_message(
            "User",
            """<task>
                            Summarize the finalized story arc for a Dungeons & Dragons one-shot using the details provided in the previous conversation.
                        </task>
                        <instructions>
                            <rule>Base the summary exclusively on the information gathered during the previous interaction.</rule>
                            <rule>Structure the summary into the specified blocks for clarity and ease of understanding.</rule>
                            <rule>Provide detailed and precise information about essential story elements.</rule>
                            <rule>Focus on non-player characters (NPCs), narrative components, and setting; exclude player characters entirely.</rule>
                        </instructions>
                        <output>
                            <format>XML</format>
                            <structure>
                                <block>
                                    <name>Player Hook</name>
                                    <description>Provide a compelling reason for players to engage with the story. This should clearly present the core motivation or problem.</description>
                                </block>
                                <block>
                                    <name>Story Summary</name>
                                    <description>Offer a detailed narrative overview, covering the key elements such as the setting, main conflict, objectives, and any critical twists or surprises.</description>
                                </block>
                                <block>
                                    <name>Important Characters</name>
                                    <description>Describe significant NPCs, including their roles, motivations, and relevance to the story.</description>
                                </block>
                            </structure>
                        </output>""")
        return self.agent.step(message)
