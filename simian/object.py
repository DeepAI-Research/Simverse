import os
import random
from typing import Any, Dict, Generator, Tuple
from mathutils import Vector

from .constants import IMPORT_FUNCTIONS
import bpy

def load_object(object_path: str, context) -> None:
    """Loads a model with a supported file extension into the scene.

    Args:
        object_path (str): Path to the model file.

    Raises:
        ValueError: If the file extension is not supported.

    Returns:
        None
    """
    file_extension = object_path.split(".")[-1].lower()
    if file_extension is None:
        raise ValueError(f"Unsupported file type: {object_path}")

    if file_extension == "usdz":
        # install usdz io package
        dirname = os.path.dirname(os.path.realpath(__file__))
        usdz_package = os.path.join(dirname, "plugins/io_scene_usdz.zip")
        bpy.ops.preferences.addon_install(filepath=usdz_package)
        # enable it
        addon_name = "io_scene_usdz"
        bpy.ops.preferences.addon_enable(module=addon_name)
        # import the usdz
        from io_scene_usdz.import_usdz import import_usdz

        import_usdz(context, filepath=object_path, materials=True, animations=True)
        return None

    # load from existing import functions
    import_function = IMPORT_FUNCTIONS[file_extension]

    if file_extension == "blend":
        import_function(directory=object_path, link=False)
    elif file_extension in {"glb", "gltf"}:
        import_function(filepath=object_path, merge_vertices=True)
    else:
        import_function(filepath=object_path)

def delete_invisible_objects(context) -> None:
    """Deletes all invisible objects in the scene.

    Returns:
        None
    """
    bpy.ops.object.select_all(action="DESELECT")
    for obj in context.scene.objects:
        if obj.hide_viewport or obj.hide_render:
            obj.hide_viewport = False
            obj.hide_render = False
            obj.hide_select = False
            obj.select_set(True)
    bpy.ops.object.delete()

    # Delete invisible collections
    invisible_collections = [col for col in bpy.data.collections if col.hide_viewport]
    for col in invisible_collections:
        bpy.data.collections.remove(col)


def get_hierarchy_bbox(context, obj):
    """Calculate the bounding box of an object and its children."""
    # Ensure the object's matrix_world is updated
    context.view_layer.update()
    
    # Initialize min and max coordinates with extremely large and small values
    min_coord = [float('inf'), float('inf'), float('inf')]
    max_coord = [-float('inf'), -float('inf'), -float('inf')]
    
    # Function to update min and max coordinates
    def update_bounds(obj):
        # Update the object's bounding box based on its world matrix
        bbox_corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
        for corner in bbox_corners:
            for i in range(3):
                min_coord[i] = min(min_coord[i], corner[i])
                max_coord[i] = max(max_coord[i], corner[i])
    
    # Recursive function to process each object
    def process_object(obj):
        update_bounds(obj)
        for child in obj.children:
            process_object(child)

    # Start processing from the root object
    process_object(obj)
    
    return min_coord, max_coord

def remove_small_geometry(context, obj, min_vertex_count: int = 10) -> bpy.types.Object:
    """Remove free-hanging geometry with fewer vertices than specified by separating by loose parts,
    deleting small ones, and re-joining them.

    Args:
        obj (bpy.types.Object): The object to process.
        min_vertex_count (int): Minimum number of vertices required to keep a part of the mesh.

    Returns:
        None
    """
    # Ensure the object is a mesh
    if obj is not None and obj.type != 'MESH':
        print("Object is not a mesh.")
        return

    # Make sure the object is active and we're in object mode
    context.view_layer.objects.active = obj
    obj.select_set(True)
    # select all children
    for child in obj.children:
        child.select_set(True)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Separate by loose parts
    bpy.ops.mesh.separate(type='LOOSE')
    bpy.ops.object.mode_set(mode='OBJECT')

    # Deselect all to start clean
    bpy.ops.object.select_all(action='DESELECT')

    # Iterate over all new objects created by the separate operation
    for ob in context.selected_objects:
        # Re-select the object to make it active
        context.view_layer.objects.active = ob
        ob.select_set(True)

        # Check vertex count
        if len(ob.data.vertices) < min_vertex_count:
            # Delete the object if it doesn't meet the vertex count requirement
            bpy.ops.object.delete()

    # Optionally, re-join remaining objects if necessary
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.join()
    bpy.ops.object.mode_set(mode='OBJECT')
    print("Processed geometry, removing parts with fewer than", min_vertex_count, "vertices.")
    return obj

import bpy

def merge_close_vertices(context, obj: bpy.types.Object, distance_threshold: float = 0.001):
    """Merges vertices that are closer than the specified distance threshold in a given object.
    
    Args:
        obj_name (str): The name of the object whose vertices need to be merged.
        distance_threshold (float): The maximum distance between vertices to be merged.
    
    Returns:
        None
    """
    # Ensure the object exists
    if not obj:
        print(f"No object found")
        return

    # Make sure the object is a mesh
    if obj.type != 'MESH':
        print("Selected object is not a mesh")
        return
    
    # Store the current mode to restore later
    prev_mode = context.object.mode
    
    # Ensure we're in Object mode
    if context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    
    # Activate and select the object
    context.view_layer.objects.active = obj
    obj.select_set(True)
    
    # Enter Edit mode
    bpy.ops.object.mode_set(mode='EDIT')
    
    # Deselect all to start clean
    bpy.ops.mesh.select_all(action='DESELECT')
    
    # Select all vertices (necessary for the 'merge by distance' operation)
    bpy.ops.mesh.select_all(action='SELECT')
    
    # Merge vertices by distance
    bpy.ops.mesh.remove_doubles(threshold=distance_threshold)
    
    # Return to the original mode
    bpy.ops.object.mode_set(mode=prev_mode)
    
    print(f"Vertices closer than {distance_threshold} units have been merged in object.")


def combine_and_centralize_hierarchy(context: bpy.types.Context, obj: bpy.types.Object) -> bpy.types.Object:
    """Combines all meshes in the hierarchy of the specified object, removes specific empties, and centralizes the new mesh.
    Args:
        obj (bpy.types.Object): The root object whose hierarchy to process.
        context (context): Blender context.
    Returns:
        None
    """
    
    # Helper function to check for the presence of an Armature modifier
    def has_armature_modifier(obj):
        return any(mod for mod in obj.modifiers if mod.type == 'ARMATURE')
    
    # Helper function to check the hierarchy for armatures or animations
    def check_hierarchy_for_armatures(obj):
        if obj.type == 'ARMATURE' or has_armature_modifier(obj) or (obj.animation_data and obj.animation_data.action):
            return True
        for child in obj.children:
            if check_hierarchy_for_armatures(child):
                return True
        return False

    # Check if there is an armature or animation in the hierarchy
    if check_hierarchy_for_armatures(obj):
        print("Skipping combining hierarchy with armature or animation.")
        return obj

    # If no armature or animation, proceed with combining
    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')
    
    # Helper function to select all mesh objects and collect empties
    empties_to_remove = set()

    def select_hierarchy_and_collect_empties(obj):
        if obj.type == 'MESH':
            obj.select_set(True)
            # Collect potential empty objects to remove
            parent = obj.parent
            while parent:
                if parent.type == 'EMPTY':
                    empties_to_remove.add(parent)
                parent = parent.parent
        for child in obj.children:
            select_hierarchy_and_collect_empties(child)

    # Select the object and its children
    select_hierarchy_and_collect_empties(obj)

    # Ensure an active mesh object is set
    context.view_layer.objects.active = next((ob for ob in bpy.context.selected_objects if ob.type == 'MESH'), None)

    # Join selected meshes, if more than one mesh object is selected
    if len(context.selected_objects) > 1:
        bpy.ops.object.join()

    # # Remove specified empties
    # for empty in empties_to_remove:
    #     bpy.data.objects.remove(empty, do_unlink=True)

    # Centralize the new combined mesh
    new_obj = context.view_layer.objects.active
    if new_obj and new_obj.type == 'MESH':
        # Reset position and rotation
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='BOUNDS')
        new_obj.location = (0, 0, 0)
        new_obj.scale = (1, 1, 1)

    return new_obj

def normalize_object_scale(context, obj: bpy.types.Object, scale_factor: float = 1.0) -> bpy.types.Object:
    """Scales the object by a factor.

    Args:
        obj (bpy.types.Object): The object to scale.
        scale_factor (float, optional): The factor to scale the object by. Defaults to 1.0.

    Returns:
        None
    """
    
    # Get the bounding box of the object and its children
    bbox_min, bbox_max = get_hierarchy_bbox(context, obj)
    print("Bounding box:", bbox_min, bbox_max)
    
    # Calculate the scale of the bounding box and scale the object if necessary
    bbox_dimensions = [bbox_max[i] - bbox_min[i] for i in range(3)]
    max_dimension = max(bbox_dimensions)
    print("Max dimension:", max_dimension)
    
    print("Scaling object")
    scale = scale_factor / max_dimension
    print("scale", scale)
    obj.scale = (scale, scale, scale)
    return obj
