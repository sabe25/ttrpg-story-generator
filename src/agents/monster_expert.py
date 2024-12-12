from __future__ import annotations

from camel.agents import ChatAgent
from camel.messages import BaseMessage
from pydantic import BaseModel, ConfigDict


class MonsterExpert(BaseModel):
    agent: ChatAgent
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def create(cls) -> MonsterExpert:
        msg = BaseMessage.make_assistant_message(
            "Monster Expert",
            f"""
            <role>
                <description>
                    You are a Monster Expert with extensive knowledge of the creatures in Dungeons & Dragons. Your role is to provide recommendations for monsters in combat encounters, ensuring they align with the environment and story context. You balance the challenge level, thematic relevance, and player engagement in your suggestions.
                </description>
                <responsibilities>
                    <monster_selection>
                        - Analyze combat scenes and suggest monsters that fit the environment, narrative, and party level.
                        - Ensure selected monsters align with official D&D rules and lore.
                        - Propose substitutions if a recommended monster may disrupt gameplay or story cohesion.
                    </monster_selection>
                    <feedback>
                        - Provide reasoning for monster choices, including thematic and mechanical relevance.
                        - Suggest tactics or adjustments to enhance the combat experience.
                        - Comment on how the encounter fits the overall pacing of the game.
                    </feedback>
                    <guidelines>
                        - Focus on balance, ensuring encounters are neither too easy nor overwhelmingly difficult.
                        - Use accurate terminology and respect the official D&D source material.
                        - Consider both common and lesser-known monsters to keep encounters fresh and engaging.
                    </guidelines>
                </responsibilities>
            </role>""")
        agent = ChatAgent(msg)
        return cls(agent=agent)

    def provide_feedback_to(self, scene_text) -> string:
        prompt = f"""
<prompt>
    <description>
        Analyse the provided Dungeons & Dragons scene_description and evaluate the choice of monsters from the perspective of a Monster Expert.
    </description>
    <instructions>
        - Review the scene description to assess if the selected monsters align with the environment and setting described.
        - Determine if the chosen monsters provide an appropriate level of challenge and engagement for the players' party.
        - Suggest alternative monsters if the current selection does not fit the environment, story, or difficulty level.
        - Ensure the monsters adhere to D&D rules and lore, respecting the ecosystem and thematic elements of the scene.
        - Provide feedback on potential tweaks to improve the encounter, such as adjusting monster behavior, number, or abilities.
    </instructions>
    <output_format>
        <feedback>
            <format>Present your feedback in a bullet point list for easy review.</format>
            <example_feedback>
                - The chosen monster (Goblin) fits the forest environment but is underpowered for the party's current level. Consider using Hobgoblins or Worgs.
                - The selection of Fire Elementals feels out of place in a swamp setting. Replace them with Will-o'-Wisps or Giant Frogs.
                - Include environmental hazards or terrain features to make the encounter with the Ankheg more dynamic and challenging.
                - The behavior of the monsters in this scene could better reflect their intelligence. Suggest having the Bandits retreat when outnumbered.
                - Verify the monster CR aligns with the party's average level; the encounter may need scaling.
            </example_feedback>
        </feedback>
    </output_format>
    <scene_description>
       {scene_text}
    </scene_description>
</prompt>"""
        refined_user_msg = BaseMessage.make_user_message("User", prompt)
        return self.agent.step(refined_user_msg).msg.content