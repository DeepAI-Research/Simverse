import os
from typing import Dict
import requests
import bpy


def get_hdri_path(hdri_path: str, combination: Dict) -> str:
    """
    Get the local file path for the background HDR image.

    Args:
        hdri_path (str): The base directory for storing background images.
        combination (Dict): The combination dictionary containing background
    Returns:
        str: The local file path for the background HDR image.
    """
    background = combination["background"]
    background_id = background["id"]
    background_from = background["from"]
    hdri_path = f"{hdri_path}/{background_from}/{background_id}.hdr"

    return hdri_path


def get_background(hdri_path: str, combination: Dict) -> None:
    """
    Download the background HDR image if it doesn't exist locally.

    This function checks if the background HDR image specified in the combination dictionary
    exists locally. If it doesn't exist, it downloads the image from the provided URL and
    saves it to the local file path.

    Args:
        hdri_path (str): The base directory for storing background images.
        combination (Dict): The combination dictionary containing background information.

    Returns:
        None
    """
    hdri_path = get_hdri_path(hdri_path, combination)

    background = combination["background"]
    background_url = background["url"]

    # make sure each folder in the path exists
    os.makedirs(os.path.dirname(hdri_path), exist_ok=True)

    if not os.path.exists(hdri_path):
        print(f"Downloading {background_url} to {hdri_path}")
        response = requests.get(background_url)
        with open(hdri_path, "wb") as file:
            file.write(response.content)
    else:
        print(f"Background {hdri_path} already exists")


def set_background(hdri_path: str, combination: Dict) -> None:
    """
    Set the background HDR image of the scene.

    This function sets the background HDR image of the scene using the provided combination
    dictionary. It ensures that the world nodes are used and creates the necessary nodes
    (Environment Texture, Background, and World Output) if they don't exist. It then loads
    the HDR image, connects the nodes, and enables the world background in the render settings.

    Args:
        hdri_path (str): The base directory for storing background images.
        combination (Dict): The combination dictionary containing background information.

    Returns:
        None
    """
    get_background(hdri_path, combination)
    hdri_path = get_hdri_path(hdri_path, combination)

    # Check if the scene has a world, and create one if it doesn't
    if bpy.context.scene.world is None:
        bpy.context.scene.world = bpy.data.worlds.new("World")

    # Ensure world nodes are used
    bpy.context.scene.world.use_nodes = True
    tree = bpy.context.scene.world.node_tree

    # Clear existing nodes
    tree.nodes.clear()

    # Create the Environment Texture node
    env_tex_node = tree.nodes.new(type="ShaderNodeTexEnvironment")
    env_tex_node.location = (-300, 0)

    # Load the HDR image
    env_tex_node.image = bpy.data.images.load(hdri_path)

    # Create the Background node
    background_node = tree.nodes.new(type="ShaderNodeBackground")
    background_node.location = (0, 0)

    # Connect the Environment Texture node to the Background node
    tree.links.new(env_tex_node.outputs["Color"], background_node.inputs["Color"])

    # Create the World Output node
    output_node = tree.nodes.new(type="ShaderNodeOutputWorld")
    output_node.location = (300, 0)

    # Connect the Background node to the World Output
    tree.links.new(background_node.outputs["Background"], output_node.inputs["Surface"])

    # Enable the world background in the render settings
    bpy.context.scene.render.film_transparent = False

    print(f"Set background to {hdri_path}")


def create_photosphere(
    hdri_path: str, combination: Dict, scale: float = 10
) -> bpy.types.Object:
    """
    Create a photosphere object in the scene.

    This function creates a UV sphere object in the scene and positions it at (0, 0, 3).
    It smooths the sphere, inverts its normals, and renames it to "Photosphere". It then
    calls the `create_photosphere_material` function to create a material for the photosphere
    using the environment texture as emission.

    Args:
        hdri_path (str): The base directory for storing background images.
        combination (Dict): The combination dictionary containing background information.

    Returns:
        bpy.types.Object: The created photosphere object.
    """
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=64, ring_count=32, radius=scale, location=(0, 0, 3)
    )

    bpy.ops.object.shade_smooth()

    # invert the UV sphere normals
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.flip_normals()
    bpy.ops.object.mode_set(mode="OBJECT")

    sphere = bpy.context.object
    sphere.name = "Photosphere"
    sphere.data.name = "PhotosphereMesh"
    create_photosphere_material(hdri_path, combination, sphere)
    return sphere


def create_photosphere_material(
    hdri_path: str, combination: Dict, sphere: bpy.types.Object
) -> None:
    """
    Create a material for the photosphere object using the environment texture as emission.

    This function creates a new material for the provided photosphere object. It sets up
    the material nodes to use the environment texture as emission and assigns the material
    to the photosphere object.

    Args:
        hdri_path (str): The base directory for storing background images.
        combination (Dict): The combination dictionary containing background information.
        sphere (bpy.types.Object): The photosphere object to assign the material to.

    Returns:
        None
    """
    # Create a new material
    mat = bpy.data.materials.new(name="PhotosphereMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()

    # Create and connect the nodes
    emission = nodes.new(type="ShaderNodeEmission")
    env_tex = nodes.new(type="ShaderNodeTexEnvironment")
    env_tex.image = bpy.data.images.load(get_hdri_path(hdri_path, combination))
    mat.node_tree.links.new(env_tex.outputs["Color"], emission.inputs["Color"])
    output = nodes.new(type="ShaderNodeOutputMaterial")
    mat.node_tree.links.new(emission.outputs["Emission"], output.inputs["Surface"])

    # Assign material to the sphere
    if sphere.data.materials:
        sphere.data.materials[0] = mat
    else:
        sphere.data.materials.append(mat)

    print("Material created and applied to Photosphere")
