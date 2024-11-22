from camel.agents import ChatAgent
from camel.messages import BaseMessage

def create_story_arch_writer() -> ChatAgent:
    prompt = ""
    with open("./agents/story_arch_writer_prompt.txt", "r") as file:
        prompt = file.read()

    refinement_msg = BaseMessage.make_assistant_message(
        "Story arch writer",
        prompt
    #     "You are a creative writer focused on writing story arch for dnd one-shots. "
    #     "You create broad overviews of story archs. For you important is that each story has the following features."
    #     "A plot hook, something that the player want to help or solve the problem"
    #     "The environment, where the story is told."
    #     "Additionally these elements could improve the story."
    #     "Surprice Elements are also fun but optional, it is something the player are not expecting."
    #     "Interesting Characters, brings depth and live to the story"
    #     "A thread, something the players are eager to solve, whether it is a social conflict or existencial thread to a village you are open to it all."
    )

    return ChatAgent(refinement_msg)