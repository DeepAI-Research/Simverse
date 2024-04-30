import os
import requests
import bpy

def reset_background(context) -> None:
    """Reset the background"""
    # TODO: Implement this function, we may want to clean out the background image
    pass

def get_background_path(args, combination) -> str:
    background = combination['background']
    background_id = background['id']
    background_from = background['from']
    background_path = f"{args.background_path}/{background_from}/{background_id}.hdr"
    return background_path

def get_background(args, combination) -> None:
    """Set the background hdr of the scene."""
    # first, download the background image to /backgrounds
    
    background_path = get_background_path(args, combination)
    
    background = combination['background']
    background_url = background['url']

    # make sure each folder in the path exists
    os.makedirs(os.path.dirname(background_path), exist_ok=True)
    
    if not os.path.exists(background_path):
        print(f"Downloading {background_url} to {background_path}")
        response = requests.get(background_url)
        with open(background_path, 'wb') as file:
            file.write(response.content)
    else:
        print(f"Background {background_path} already exists")
        
def set_background(context, args, combination) -> None:
    """Set the background HDR image of the scene."""
    get_background(args, combination)
    background_path = get_background_path(args, combination)
    
    # Ensure world nodes are used
    context.scene.world.use_nodes = True
    tree = context.scene.world.node_tree
    
    # Find the existing Environment Texture node
    env_tex_node = None
    for node in tree.nodes:
        if node.type == 'TEX_ENVIRONMENT':
            env_tex_node = node
            break
    
    if env_tex_node is None:
        raise ValueError("Environment Texture node not found in the world node graph")
    
    # Load the HDR image
    env_tex_node.image = bpy.data.images.load(background_path)
    
    # Connect the Environment Texture node to the Background node
    background_node = tree.nodes.get("Background")
    if background_node is None:
        # If the Background node doesn't exist, create it
        background_node = tree.nodes.new(type="ShaderNodeBackground")
    
    # Connect the Environment Texture node to the Background node
    tree.links.new(env_tex_node.outputs["Color"], background_node.inputs["Color"])
    
    # Connect the Background node to the World Output
    output_node = tree.nodes.get("World Output")
    if output_node is None:
        # If the World Output node doesn't exist, create it
        output_node = tree.nodes.new(type="ShaderNodeOutputWorld")
    
    # Connect the Background node to the World Output
    tree.links.new(background_node.outputs["Background"], output_node.inputs["Surface"])
    
    # Enable the world background in the render settings
    context.scene.render.film_transparent = False
    
    print(f"Set background to {background_path}")
    