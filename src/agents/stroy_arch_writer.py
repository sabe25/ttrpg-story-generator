from __future__ import annotations

from langchain_core.messages import BaseMessage
from pydantic import BaseModel
from pydantic.config import ConfigDict
from pathlib import Path

from src.agents.chat_agent import ChatAgent


class StoryArchWriter(BaseModel):
    agent: ChatAgent
    user_msgs: list[str]
    user_ass_msgs: list[tuple[str, str]]
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def create(cls) -> StoryArchWriter:
        script_dir = Path(__file__).parent
        promptPath = script_dir / "story_arch_writer_prompt.txt"
        with open(promptPath, "r") as file:
            prompt = file.read()

        agent = ChatAgent.create(prompt)
        return cls(agent=agent, user_msgs=[], user_ass_msgs=[])

    def start_refinement(self, user_msg) -> str:
        self.user_msgs.append(user_msg)
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
                    <rule>If any element is missing or unclear, ask specific questions to gather more details.</rule>
                    <rule>If any element is missing, provide ready-to-use examples tailored to fit the story's theme and tone.</rule>
                </instructions>
                <user_input>{user_msg}</user_input>""")

        return self.agent.invoke(initial_user_str).content

    def refine_furhter(self, user_msg) -> str:
        self.user_msgs.append(user_msg)
        refined_user_msg = f"""<task>Consider this update to the story arc. If I selected one of your ready-to-use examples consider them for the story arch</task>
                        <update>{user_msg}</update>"""
        assistant_msg = self.agent.invoke(refined_user_msg)
        self.user_ass_msgs.append((user_msg, assistant_msg.content))
        return assistant_msg.content

    def summarise_from_memory(self) -> str:
        message = """<task>
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
                        </output>"""
        return self.agent.invoke(message).content

    def summarise_using_user_input(self) -> str:
        message = f"""<task>
                            Summarize the finalized story arc for a Dungeons & Dragons one-shot.
                        </task>
                        <instructions>
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
                        </output>
                        <input>
                            <format>Each user message provides information about the story arc.</format>
                            { "".join(f"<content>{x}</content>" for x in self.user_msgs) }
                        </input>"""
        return self.agent.invoke(message).content

    def extract_story_facts(self) -> list[str]:
        (first_user, first_ass) = self.user_ass_msgs.pop()
        fact1 =  self.agent.invoke(
            f"""Extract facts about the story explained in the given text. 
                The facts should be one sentence long and simple. 
                The facts should be provided as a bulleted list.
                <user_message>{first_user}</user_message>""")
        print(fact1.content)
        next_ass = first_ass
        facts = [fact1.content]
        for user, ass in self.user_ass_msgs:
            fact = self.agent.invoke(
                f"""Extract facts about the story explained in the given text. 
                The facts should be one sentence long and simple. 
                The facts should be provided as a bulleted list.
                The user could choose topics or suggestions mentioned in the assistant message. Consider them as facts
                <assistant_message>{next_ass}</assistant_message>
                <user_message>{user}</user_message>""")
            facts.append(fact.content)
            next_ass = ass

        return facts
