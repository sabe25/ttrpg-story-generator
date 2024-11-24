from src.agents.scene_creator import SceneCreator
import xml.etree.ElementTree as ET

def create_scene_structure(story: str) -> list:
    structure_agent = SceneCreator.create()
    response = structure_agent.create_story_scenes(story)
    print(response.msg.content)

    root = ET.fromstring(response.msg.content)
    elements_list = [child.text for child in root]

    return elements_list
