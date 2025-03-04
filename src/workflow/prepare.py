from src.agents.stroy_arch_writer import StoryArchWriter


def refine_user_input(max_steps=10) -> str:
    agent = StoryArchWriter.create()

    user_msg = input("Please specify your story.")
    print("---- Analysing -----")

    response = agent.start_refinement(user_msg)

    for i in range(max_steps):
        if i == max_steps - 1:
            break

        # print_text_animated(response.msg.content)
        print(response)

        refined_user_input = input("Please provide more information or leave blank if you are done.")
        print("---- Analysing -----")
        if len(refined_user_input) == 0:
            break

        response = agent.refine_furhter(refined_user_input)

    result = agent.summarise_using_user_input()
    print("Thank you for your input. Here is what i got:\n" + result)

    facts = agent.extract_story_facts()
    print("Here are the facts", "\n".join(facts))
    return result
