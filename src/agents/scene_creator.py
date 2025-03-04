from __future__ import annotations

from langchain_core.messages import BaseMessage
from pydantic import BaseModel, ConfigDict
import xml.etree.ElementTree as ET

from src.agents.chat_agent import ChatAgent


class SceneCreator(BaseModel):
    agent: ChatAgent
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def create(cls) -> SceneCreator:
        structure_msg = f"""
                        <role>
                            You are a Scene Creator, responsible for crafting compelling scenes for a Dungeons & Dragons story arc.
                            Your goal is to structure the narrative into meaningful steps, each driving the story forward while balancing variety in encounters.

                            <framework>
                                - Encounters are grouped into three main categories:
                                  1. Combat
                                  2. NPC Interaction
                                  3. Exploration
                                - Each scene must use one of the main categories but can incorporate a **subtype flavor** for variety and depth.
                                - Avoid repetition: Alternate between encounter types when possible to keep the pacing engaging.

                                <encounter_categories>
                                    <combat>
                                        - Direct Combat
                                        - Tactical Combat
                                        - Environmental Combat
                                        - Boss Battle
                                        - Mixed Combat
                                    </combat>
                                    <npc_interaction>
                                        - Quest-Giving
                                        - Diplomacy/Negotiation
                                        - Deception/Interrogation
                                        - Ally Recruitment
                                        - Mystery/Investigation
                                    </npc_interaction>
                                    <exploration>
                                        - Environmental Navigation
                                        - Puzzle-Solving
                                        - Discovery
                                        - Hazard Survival
                                        - Trap Disarmament
                                    </exploration>
                                    <additional_scenes>
                                        - Social Conflict
                                        - Moral Dilemma
                                        - Cinematic Moments
                                        - Skill Challenges
                                        - Prophecy/Mystical Guidance
                                        - Downtime and Preparation
                                    </additional_scenes>
                                </encounter_categories>
                            </framework>
                            <instructions>
                                - Analyze the story arc to determine the sequence of scenes needed to progress from the player hook to the conclusion.
                                - Ensure each scene adds value to the story, whether through advancing the plot, revealing important details, or deepening character interactions.
                                - Keep the story engaging by alternating encounter types and integrating flavor subtypes.
                                - Ensure NPCs are relevant and serve the narrative.
                            </instructions>
                        </role>"""
        structure_agent = ChatAgent.create(structure_msg)
        return cls(agent=structure_agent)

    def create_story_start_and_end(self, story) -> list:
        task = f"""
                <task>
                    Analyze the provided story arc to define the **player hook** and the **final scene** of the story.
                </task>
                <instructions>
                    1. **Player Hook**:
                        - Identify the central element that will immediately capture the players' attention and motivate them to engage with the story.
                        - Describe the setting and stakes of this initial scene.
                    2. **Final Scene**:
                        - Outline the climax and resolution of the story.
                        - Describe the setting, sequence of events, and any critical decisions or actions required to conclude the narrative.
                </instructions>
                <output>
                    <format>XML without any code code style markings</format>
                    <example>
                        <scenes>
                            <player_hook></player_hook>
                            <final_scene></final_scene>
                        </scenes>
                    </example>
                </output>
                <input>{story}</input>"""

        response = self.agent.invoke(task)

        root = ET.fromstring(response.content)
        firstLastScene = [root.find('player_hook'), root.find('final_scene')]
        return firstLastScene

    def create_story_scenes(self, story) -> BaseMessage:
        first_last_scene = self.create_story_start_and_end(story)
        task = f"""<task>
                        Create transition scenes that guide the players from the **player hook** to the **final scene** based on the given story arc.
                    </task>
                    <instructions>
                        1. Analyze the player hook, final scene, and overall story arc to ensure all transition scenes contribute to a cohesive and engaging narrative.
                        2. Transform the given player hook and final scene to scenes according to the output.
                        3. Use the XML format specified below for your output.
                        4. The scenes should be listed in order according to the given story
                    </instructions>
                    <output>
                        <format>XML without any code code style markings</format>
                        <example>
                            <scene>
                                <title>Scene Title</title>
                                <description>2-3 sentences describing the scene's purpose and actions.</description>
                                <encounter_type>Main Category (Combat, NPC Interaction, Exploration)</encounter_type>
                                <flavor>Subtype flavor chosen for the scene, if applicable.</flavor>
                                <npc_list>
                                    <npc>Name and role of NPCs involved.</npc>
                                    <!-- Add multiple <npc> entries if needed -->
                                </npc_list>
                            </scene>
                            <!-- continue with scenes in order -->
                        </example>
                    </output>
                    <input>
                        <story>{story}</story>
                        <player_hook>{first_last_scene[0]}</player_hook>
                        <final_scene>{first_last_scene[1]}</final_scene>
                    </input>"""
        return self.agent.invoke(task)
