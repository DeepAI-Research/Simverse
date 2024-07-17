import json
import readline
import multiprocessing
import os
import subprocess
import sys
import argparse
from questionary import Style
from questionary import Choice, select
from rich.console import Console
from typing import Any, Dict, List, Optional

from simian.prompts import generate_gemini, setup_gemini, parse_gemini_json, CAMERA_PROMPT, OBJECTS_JSON_PROMPT, OBJECTS_PROMPT
from .server import initialize_chroma_db, query_collection
from .combiner import calculate_transformed_positions

console = Console()

def select_mode():
    """
    Prompt the user to select the rendering mode (Prompt Mode or Batch Mode).
    """

    custom_style = Style([
        ('question', 'fg:#FF9D00 bold'), 
        ('pointer', 'fg:#FF9D00 bold'),  
        ('highlighted', 'fg:#00FFFF bold'),
        ('default', 'fg:#FFFFFF'),
    ])

    options = [
        Choice("Prompt Mode", value="Prompt Mode"),
        Choice("Batch Mode", value="Batch Mode")
    ]
    
    selected = select(
        "Select Mode",
        choices=options,
        use_indicator=True,
        style=custom_style,
        instruction='Use ↑ and ↓ to navigate, Enter to select',
        qmark="", 
        pointer="▶", 
    ).ask()

    console.print(f"\nEntering {selected}", style="bold green")
    
    return selected


def render_objects(
    processes: Optional[int] = None,
    render_timeout: int = 3000,
    width: int = 1920,
    height: int = 1080,
    start_index: int = 0,
    end_index: int = -1,
    start_frame: int = 1,
    end_frame: int = 65,
    images: bool = False,
    blend_file: Optional[str] = None,
    animation_length: int = 100
) -> None:
    """
    Automates the rendering of objects using Blender based on predefined combinations.

    This function orchestrates the rendering of multiple objects within a specified range
    from the combinations DataFrame. It allows for configuration of rendering dimensions,
    use of specific GPU devices, and selection of frames for animation sequences.

    Args:
        processes (Optional[int]): Number of processes to use for multiprocessing.
        Defaults to three times the number of CPU cores.
        render_timeout (int): Maximum time in seconds for a single rendering process.
        width (int): Width of the rendering in pixels.
        height (int): Height of the rendering in pixels.
        start_index (int): Starting index for rendering from the combinations DataFrame.
        end_index (int): Ending index for rendering from the combinations DataFrame.
        start_frame (int): Starting frame number for the animation.
        end_frame (int): Ending frame number for the animation.
        images (bool): Generate images instead of videos.
        blend_file (Optional[str]): Path to the user-specified Blender file to use as the base scene.
        animation_length (int): Percentage animation length.

    Raises:
        NotImplementedError: If the operating system is not supported.
        FileNotFoundError: If Blender is not found at the specified path.

    Returns:
        None
    """
    # Set the number of processes to three times the number of CPU cores if not specified.
    if processes is None:
        processes = multiprocessing.cpu_count() * 3

    scripts_dir = os.path.dirname(os.path.realpath(__file__))
    target_directory = os.path.join(scripts_dir, "../", "renders")
    hdri_path = os.path.join(scripts_dir, "../", "backgrounds")

    # make sure renders directory exists
    os.makedirs(target_directory, exist_ok=True)

    if end_index == -1:

        # get the length of combinations.json
        with open(os.path.join(scripts_dir, "../", "combinations.json"), "r") as file:
            data = json.load(file)
            combinations_data = data["combinations"]
            num_combinations = len(combinations_data)

        end_index = num_combinations

    # Loop over each combination index to set up and run the rendering process.
    for i in range(start_index, end_index):
        if images:
            args = f"--width {width} --height {height} --combination_index {i} --start_frame {start_frame} --end_frame {end_frame} --output_dir {target_directory} --hdri_path {hdri_path} --animation_length {animation_length} --images"
        else:
            args = f"--width {width} --height {height} --combination_index {i} --start_frame {start_frame} --end_frame {end_frame} --output_dir {target_directory} --hdri_path {hdri_path} --animation_length {animation_length}"

        if blend_file:
            args += f" --blend {blend_file}"

        command = f"{sys.executable} -m simian.render -- {args}"
        subprocess.run(["bash", "-c", command], timeout=render_timeout, check=False)


def parse_args(args_list = None) -> argparse.Namespace:
    """
    Parse the command-line arguments for the rendering process.

    Args:
        args_list (Optional[List[str]]): A list of command-line arguments. Defaults to None.

    Returns:
        argparse.Namespace: The parsed command-line arguments.
    """

    parser = argparse.ArgumentParser(
        description="Automate the rendering of objects using Blender."
    )
    parser.add_argument(
        "--processes",
        type=int,
        default=None,
        help="Number of processes to use for multiprocessing. Defaults to three times the number of CPU cores.",
    )
    parser.add_argument(
        "--render_timeout",
        type=int,
        default=3000,
        help="Maximum time in seconds for a single rendering process. Defaults to 3000.",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=1920,
        help="Width of the rendering in pixels. Defaults to 1920.",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=1080,
        help="Height of the rendering in pixels. Defaults to 1080.",
    )
    parser.add_argument(
        "--start_index",
        type=int,
        default=0,
        help="Starting index for rendering from the combinations DataFrame. Defaults to 0.",
    )
    parser.add_argument(
        "--end_index",
        type=int,
        default=-1,
        help="Ending index for rendering from the combinations DataFrame. Defaults to -1.",
    )
    parser.add_argument(
        "--start_frame",
        type=int,
        default=1,
        help="Starting frame number for the animation. Defaults to 1.",
    )
    parser.add_argument(
        "--end_frame",
        type=int,
        default=65,
        help="Ending frame number for the animation. Defaults to 65.",
    )
    parser.add_argument(
        "--images",
        action="store_true",
        help="Generate images instead of videos.",
    )
    parser.add_argument(
        "--blend",
        type=str,
        default=None,
        help="Path to the user-specified Blender file to use as the base scene.",
        required=False,
    )
    parser.add_argument(
        "--animation_length",
        type=int,
        default=100,
        help="Percentage animation length. Defaults to 100%.",
        required=False
    )

    if args_list is None:
        args = parser.parse_args()
    else:
        args = parser.parse_args(args_list)
    
    return args





def prompt_based_rendering():
    """
    Perform prompt-based rendering using the Gemini API and ChromaDB.
    """

    import random
    from chromadb.utils import embedding_functions
    from sentence_transformers import SentenceTransformer

    chroma_client = initialize_chroma_db(reset_hdri=False, reset_textures=False)
    model = SentenceTransformer('all-MiniLM-L6-v2')  # or another appropriate model
    sentence_transformer_ef = model.encode
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name='all-MiniLM-L6-v2')

    # Create or get collections for each data type
    object_collection = chroma_client.get_or_create_collection(name="object_captions")
    hdri_collection = chroma_client.get_or_create_collection(name="hdri_backgrounds")
    texture_collection = chroma_client.get_or_create_collection(name="textures")

    prompt = input("Enter your prompt (or 'quit' to exit): ")

    # Generate Gemini
    model = setup_gemini()
    objects_background_ground_prompt = generate_gemini(model, OBJECTS_PROMPT, prompt)
    objects_background_ground_list = json.loads(objects_background_ground_prompt)

    # split array, background and ground are last two elements
    objects_prompt = objects_background_ground_list[:-2]
    background_prompt = objects_background_ground_list[-2]
    ground_prompt = objects_background_ground_list[-1]
    
    object_ids = []
    for i, obj in enumerate(objects_prompt):
        object_options =  query_collection(obj, sentence_transformer_ef, object_collection, n_results=2)
        object_ids.append({object_options["ids"][0][0]: obj})
    
    background_query = query_collection(background_prompt, sentence_transformer_ef, hdri_collection, n_results=2)
    background_id = background_query["ids"][0][0]
    background_data = background_query["metadatas"][0][0]

    formatted_background = {
        "background": {
            "name": background_data['name'],
            "url": background_data['url'],
            "id": background_id,
            "from": "hdri_data"
        }
    }

    ground_texture_query = query_collection(ground_prompt, sentence_transformer_ef, texture_collection, n_results=2)
    ground_data = ground_texture_query["metadatas"][0][0]

    formatted_stage = {
        "stage": {
            "material": {
                "name": ground_data['name'],
                "maps": ground_data['maps']
            },
            "uv_scale": [random.uniform(0.8, 1.2), random.uniform(0.8, 1.2)],
            "uv_rotation": random.uniform(0, 360)
        }
    }

    prompt += str(object_ids)

    objects_json_prompt = generate_gemini(model, OBJECTS_JSON_PROMPT, prompt + str(object_ids))
    objects_parse = parse_gemini_json(objects_json_prompt)
    objects_list = objects_parse if isinstance(objects_parse, list) else []

    camera_prompt = generate_gemini(model, CAMERA_PROMPT, prompt)
    camera_parse = parse_gemini_json(camera_prompt)

    # Combine all pieces into the final structure
    final_structure = {
        "index": 0,
        "objects": objects_list,
        "background": formatted_background["background"],
        "orientation": camera_parse.get("orientation", {}),
        "framing": camera_parse.get("framing", {}),
        "animation": camera_parse.get("animation", {}),
        "stage": formatted_stage["stage"],
        "postprocessing": camera_parse.get("postprocessing", {})
    }

    updated_combination = calculate_transformed_positions(final_structure)
    write_combinations_json(updated_combination)
    
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.realpath(__file__))
    
    # Set default rendering parameters
    width = 1024
    height = 576
    start_frame = 1
    end_frame = 65

    render_objects(
        processes=None,
        render_timeout=3000,
        width=width,
        height=height,
        start_index=0, 
        end_index=1,
        start_frame=start_frame,
        end_frame=end_frame,
        images=False,  
        blend_file=None,
        animation_length=100 
    )

    return updated_combination


def write_combinations_json(combination: Dict[str, Any], output_file: str = "combinations.json"):
    """
    Write the combination data to a JSON file.

    Args:
        combination (dict): The combination data to write.
        output_file (str): The name of the output JSON file. Defaults to "combinations.json".

    Returns:
        None
    """
    # Prepare the data structure
    data = {
        "seed": 0,  # You might want to make this dynamic
        "count": 1,  # Since we're only writing one combination
        "combinations": [combination]
    }

    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.realpath(__file__))
    
    # Construct the full path for the output file
    output_path = os.path.join(current_dir, "..", output_file)

    # Write the data to the JSON file
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=4)


def main():
    simverse_ascii = """

 ░▒▓███████▓▒░▒▓█▓▒░▒▓██████████████▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓████████▓▒░▒▓███████▓▒░ ░▒▓███████▓▒░▒▓████████▓▒░ 
░▒▓█▓▒░      ░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░        
░▒▓█▓▒░      ░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░        
 ░▒▓██████▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒▒▓█▓▒░░▒▓██████▓▒░ ░▒▓███████▓▒░ ░▒▓██████▓▒░░▒▓██████▓▒░   
       ░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▓█▓▒░ ░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░▒▓█▓▒░        
       ░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▓█▓▒░ ░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░▒▓█▓▒░        
░▒▓███████▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░  ░▒▓██▓▒░  ░▒▓████████▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓███████▓▒░░▒▓████████▓▒░ 
                                                                                                          
    """

    console.print(simverse_ascii)
    selected_mode = select_mode()

    if selected_mode == "Prompt Mode":
        prompt_based_rendering()
    else:
        while True:
            console.print("Command arguments (e.g., --start_index 0 --end_index 1000 --width 1024 --height 576 --start_frame 1 --end_frame 2). Type 'quit' to exit.")
            command = input("Enter command: ")
            if command.lower() == 'quit':
                break
            try:
                args = parse_args(command.split())
                render_objects(
                    processes=args.processes,
                    render_timeout=args.render_timeout,
                    width=args.width,
                    height=args.height,
                    start_index=args.start_index,
                    end_index=args.end_index,
                    start_frame=args.start_frame,
                    end_frame=args.end_frame,
                    images=args.images,
                    blend_file=args.blend,
                    animation_length=args.animation_length
                )
            except SystemExit:
                console.print("Invalid command. Please try again.", style="bold red")


if __name__ == "__main__":
    main()
