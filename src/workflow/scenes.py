import xml.etree.ElementTree as ET

from camel.tasks import Task

from src.agents.dungeon_master import DungeonMaster
from src.agents.monster_expert import MonsterExpert
from src.agents.scene_creator import SceneCreator
from src.agents.scene_writer import SceneWriter
from src.workflow.workforce import create_workforce


def create_scene_structure(story: str) -> list:
    structure_agent = SceneCreator.create()
    response = structure_agent.create_story_scenes(story)
    print(response.msg.content)

    root = ET.fromstring(response.msg.content)
    elements_list = []
    for child in root:
        child_as_string = ET.tostring(child, encoding='unicode', method='xml')
        elements_list.append(child_as_string)

    return elements_list

def create_scene_manually(all_steps) -> list:
    scene_agent = SceneWriter.create()
    dm_agent = DungeonMaster.create()
    monster_expert = MonsterExpert.create()

    previous_scene = None
    next_scene = None
    scene_list = []
    idxLast =  len(all_steps) - 1
    for cnt in range(0, idxLast):
        current_scene = all_steps[cnt]
        if cnt < idxLast:
            next_scene = all_steps[cnt + 1]
        else:
            next_scene = None
        print(current_scene, next_scene)
        # scene writer generate text
        scene_text = scene_agent.write_scene(current_scene, next_scene, previous_scene)
        print(scene_text)
        # dm feedback
        dm_feedback = dm_agent.provide_feedback_to(scene_text)
        print(dm_feedback)

        scene_text = scene_agent.adapt_to_feedback(dm_feedback)
        print(scene_text)

        # if combat: monster expert feedback
        if "Combat" in current_scene:
            me_feedback = monster_expert.provide_feedback_to(scene_text)
            print(me_feedback)

            scene_text = scene_agent.adapt_to_feedback(me_feedback)
            print(scene_text)

        scene_list.append(scene_text)
        cnt += 1

    return scene_list
