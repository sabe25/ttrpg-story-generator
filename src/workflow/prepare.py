from src.agents.stroy_arch_writer import StoryArchWriter


def refine_user_input(max_steps=10) -> str:
    agent = StoryArchWriter.create()

    user_msg = input("Please specify your story.")

    response = agent.start_refinement(user_msg)

    for i in range(max_steps):
        if i == max_steps - 1:
            break
        if "<NO_QUESTION>" in response.msg:
            break

        # print_text_animated(response.msg.content)
        print(response.msg.content)

        refined_user_input = input("Please answer the given questions.")
        response = agent.refine_furhter(refined_user_input)

    result = agent.summarise()

    print("Thank you for your input. Here is what i got: " + result.msg.content)
    return result.msg.content
