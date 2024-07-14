import json
import multiprocessing
import os
import subprocess
import sys
import argparse
from typing import Optional
from questionary import Style
from questionary import Choice, select
from rich.console import Console

# from server.server import query_collection, object_collection, hdri_collection, texture_collection

console = Console()


def select_mode():
    custom_style = Style([
        ('question', 'fg:#FF9D00 bold'),  # Orange color for the question
        ('pointer', 'fg:#FF9D00 bold'),   # Orange color for the pointer
        ('highlighted', 'fg:#00FFFF bold'),  # Cyan color for highlighted option
        ('default', 'fg:#FFFFFF'),  # White color for non-highlighted options
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
        qmark="",  # Remove the question mark
        pointer="▶",  # Use a triangle as a pointer
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


def parse_args(args_list=None) -> argparse.Namespace:
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
    while True:
        prompt = input("Enter your prompt (or 'quit' to exit): ")
        if prompt.lower() == 'quit':
            break
        
        # Process the prompt here
        # This could involve parsing the prompt, setting up parameters, and calling render_objects
        print(f"Processing prompt: {prompt}")

        # call llm to extract objects, hdri, textures
        objects = ["A person playing the guitar in a studio", "A person playing the piano in a studio"]
        hdri = ["A studio with a guitar", "A studio with a piano"]
        textures = ["Wooden texture", "Metal texture"]

        # query the collections and loop through the results
        for obj in objects:
            object_results = query_collection(obj, object_collection, n_results=2)
        
        for h in hdri:
            hdri_results = query_collection(h, hdri_collection, n_results=2)
        
        for t in textures:
            texture_results = query_collection(t, texture_collection, n_results=2)        

        # Example (you'll need to implement the actual logic):
        # params = parse_prompt(prompt)
        # render_objects(**params)


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
