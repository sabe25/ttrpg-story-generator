from src.agents.stroy_arch_writer import StoryArchWriter
import streamlit as st

def refine_user_input(max_steps=10) -> str:
    agent = StoryArchWriter.create()
    with st.chat_message("ai"):
        st.write("Hi there 👋 I would like to create a story with you. Please, tell me about your ideas.")

    result = ""
    init_user_chat = st.chat_message("user")
    if user_msg := init_user_chat.text_area("Your Story"):

        with st.chat_message("ai"):
            st.write_stream(agent.start_refinement(user_msg))
            st.write("")
            st.write("Please provide more information or leave blank if you are done.")

        for i in range(max_steps):
            if i == max_steps - 1:
                break

            user_chat = st.chat_message("user")
            if user_msg := user_chat.text_area("Refinement"):
                if len(user_msg) == 0:
                    break

                with st.chat_message("ai"):
                    st.write_stream(agent.refine_furhter(user_msg))
                    st.write("")
                    st.write("Please provide more information or leave blank if you are done.")


        result = agent.summarise_using_user_input()
        print("Thank you for your input. Here is what i got:\n" + result)

        facts = agent.extract_story_facts()
        print("Here are the facts", "\n".join(facts))
    return result
