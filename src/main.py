from src.workflow import prepare, scenes
import streamlit as st


if __name__ == "__main__":
    # main()
    story = prepare.refine_user_input()
    all_steps = scenes.create_scene_structure(story)
    scene_decs = scenes.create_scene_manually(all_steps)
    print(str.join('\n', scene_decs))
