import json
import os

def load_json_file(file_path='combinations.json'):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data['combinations'][0]

def extract_structured_data(scene_data):
    output = []

    # Objects
    for obj in scene_data['objects']:
        output.extend([
            f"# Scene Object",
            f"## {obj['name']}",
            f"### Attributes",
            f"- Scale: {obj['scale']['factor']}",
            f"- Size: {obj['scale']['name_synonym']}",
            f"### Position and Placement",
            f"- Placement: {obj['placement']}",
            f"- Position: [{obj['transformed_position'][0]:.2f}, {obj['transformed_position'][1]:.2f}]",
            ""
        ])

    # Camera Settings
    output.extend([
        "# Camera Settings",
        "## Orientation",
        f"- Yaw: {scene_data['orientation']['yaw']}",
        f"- Pitch: {scene_data['orientation']['pitch']}",
        f"- Description: {scene_data['orientation_caption'].split(': ')[-1]}",
        "",
        "## Framing",
        f"- FOV: {scene_data['framing']['fov']}",
        f"- Focal Length: {float(scene_data['framing_caption'].split('(')[-1].split()[0]):.2f}",
        f"- Description: {scene_data['framing_caption'].split(': ')[-1].split('.')[0]}",
        "",
        "## Animation",
        f"- Type: {scene_data['animation']['name']}",
        f"- Speed Factor: {scene_data['animation']['speed_factor']:.2f}",
        f"- Description: {scene_data['animation_caption'].split(': ')[-1]}",
        "",
        "## Keyframes",
        f"- Start: {scene_data['animation']['keyframes'][0]['CameraAnimationPivot']['position']}",
        f"- End: {scene_data['animation']['keyframes'][-1]['CameraAnimationPivot']['position']}",
        ""
    ])

    # Scene Environment
    output.extend([
        "# Scene Environment",
        "## Background",
        f"- Name: {scene_data['background']['name']}",
        "",
        "## Stage",
        f"- Material: {scene_data['stage']['material']['name']}",
        f"- UV Scale: [{scene_data['stage']['uv_scale'][0]:.2f}, {scene_data['stage']['uv_scale'][1]:.2f}]",
        f"- UV Rotation: {scene_data['stage']['uv_rotation']:.2f}",
        ""
    ])

    # Post-processing Effects
    output.extend([
        "# Post-processing Effects",
        f"Caption: {scene_data['postprocessing_caption']}",
        "",
        "## Bloom",
        f"- Type: {scene_data['postprocessing']['bloom']['type']}",
        f"- Threshold: {scene_data['postprocessing']['bloom']['threshold']:.2f}",
        f"- Intensity: {scene_data['postprocessing']['bloom']['intensity']:.2f}",
        f"- Radius: {scene_data['postprocessing']['bloom']['radius']:.2f}",
        "",
        "## Ambient Occlusion",
        f"- Type: {scene_data['postprocessing']['ssao']['type']}",
        f"- Distance: {scene_data['postprocessing']['ssao']['distance']:.2f}",
        f"- Factor: {scene_data['postprocessing']['ssao']['factor']:.2f}",
        "",
        "## Ray Tracing",
        f"- Type: {scene_data['postprocessing']['ssrr']['type']}",
        f"- Max Roughness: {scene_data['postprocessing']['ssrr']['max_roughness']:.2f}",
        f"- Thickness: {scene_data['postprocessing']['ssrr']['thickness']:.2f}",
        "",
        "## Motion Blur",
        f"- Type: {scene_data['postprocessing']['motionblur']['type']}",
        f"- Shutter Speed: {scene_data['postprocessing']['motionblur']['shutter_speed']:.2f}",
        ""
    ])

    return '\n'.join(output)

def main():
    scene_data = load_json_file()
    structured_data = extract_structured_data(scene_data)

    # Write to file
    with open('scene_data_structured.md', 'w') as f:
        f.write(structured_data)

    print(f"Results have been saved to {os.path.abspath('scene_data_structured.md')}")

if __name__ == "__main__":
    main()