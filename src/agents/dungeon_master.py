from __future__ import annotations

from camel.agents import ChatAgent
from camel.messages import BaseMessage
from pydantic import BaseModel, ConfigDict


class DungeonMaster(BaseModel):
    agent: ChatAgent
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def create(cls) -> DungeonMaster:
        msg = BaseMessage.make_assistant_message(
            "Dungeon Master",
            f"""
            <role>
                <description>
                    You are a seasoned Dungeon Master (DM) and an expert in crafting and refining Dungeons & Dragons campaign materials. Your primary role is to review scene descriptions and story outlines to ensure they are polished, engaging, and practical for live gameplay. You will provide constructive feedback from a DM's perspective, focusing on enhancing player immersion and maintaining game flow.
                </description>
                <responsibilities>
                    <analysis>
                        - Carefully examine each scene description for clarity, completeness, and relevance to the overarching story.
                        - Identify optional steps or scenes and suggest how they might be integrated effectively.
                        - Highlight elements that can be reordered without disrupting the narrative.
                    </analysis>
                    <feedback>
                        - Add comments on how to make scenes more interactive and immersive for players.
                        - Suggest improvements for balancing gameplay elements (e.g., combat, puzzles, roleplay).
                        - Recommend adjustments to pacing or narrative flow if necessary.
                    </feedback>
                    <guidelines>
                        - Feedback should prioritize actionable suggestions.
                        - Use concise language and bullet points for clarity.
                        - Always consider how the scene will play out in a dynamic game setting.
                    </guidelines>
                </responsibilities>
            </role>""")
        agent = ChatAgent(msg)
        return cls(agent=agent)

    def provide_feedback_to(self, scene_text) -> string:
        refined_user_msg = BaseMessage.make_user_message(
            "User",
            f"""
<prompt>
    <description>
        Analyse the given Dungeons & Dragons scene_description and evaluate it from the perspective of a Dungeon Master (DM) running the game.
    </description>
    <instructions>
        - Carefully review the scene description for clarity, usability, and relevance during gameplay.
        - Provide constructive feedback on what could be improved to enhance the experience for the DM and players.
        - Consider elements such as pacing, player engagement opportunities, balance of challenge, and how well the scene integrates with the overall story arc.
        - Focus on practical suggestions for improvement.
    </instructions>
    <output_format>
        <feedback>
            <format>Present the feedback in a bullet point list for easy reference.</format>
            <example_feedback>
                - The description of the setting is clear, but it could benefit from more sensory details to immerse the players.
                - Include a stronger hook to encourage player interaction with the NPC in this scene.
                - The combat encounter lacks balance; consider reducing the number of enemies to match the players' level.
                - The scene transitions well to the next, but the resolution of the previous scene's conflict feels rushed.
                - Add a puzzle or trap to give non-combat-focused players more to do in this scene.
            </example_feedback>
        </feedback>
    </output_format>
    <scene_description>
       {scene_text}
    </scene_description>
</prompt>""")
        return self.agent.step(refined_user_msg).msg.content