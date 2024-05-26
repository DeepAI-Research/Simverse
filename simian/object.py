from typing import List, Optional, Callable, Dict
import bpy
from mathutils import Vector

"""
A dictionary mapping file extensions to Blender's import functions.
This allows for dynamic selection of the appropriate import function based on the file type.
Each key is a string representing the file extension, and the value is a callable Blender function.

Supported file types include:
- "obj": Imports Wavefront OBJ files.
- "glb": Imports GLB (binary glTF) files.
- "gltf": Imports glTF files.
- "usd": Imports Universal Scene Description (USD) files.
- "fbx": Imports Autodesk FBX files.
- "stl": Imports Stereolithography (STL) files.
- "usda": Imports ASCII format of Universal Scene Description files.
- "dae": Imports Collada (DAE) files.
- "ply": Imports Polygon File Format (PLY) files.
- "abc": Imports Alembic files.
- "blend": Appends or links from a Blender (.blend) file.
"""
IMPORT_FUNCTIONS: Dict[str, Callable] = {
    "obj": bpy.ops.import_scene.obj,
    "glb": bpy.ops.import_scene.gltf,
    "gltf": bpy.ops.import_scene.gltf,
    "usd": bpy.ops.import_scene.usd,
    "fbx": bpy.ops.import_scene.fbx,
    "stl": bpy.ops.import_mesh.stl,
    "usda": bpy.ops.import_scene.usda,
    "dae": bpy.ops.wm.collada_import,
    "ply": bpy.ops.import_mesh.ply,
    "abc": bpy.ops.wm.alembic_import,
    "blend": bpy.ops.wm.append,
}


def load_object(object_path: str) -> None:
    """
    Loads a model with a supported file extension into the scene.

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

    # load from existing import functions
    import_function = IMPORT_FUNCTIONS[file_extension]

    if file_extension == "blend":
        import_function(directory=object_path, link=False)
    elif file_extension in {"glb", "gltf"}:
        import_function(filepath=object_path, merge_vertices=True)
    else:
        import_function(filepath=object_path)


def delete_invisible_objects() -> None:
    """
    Deletes all invisible objects in the scene.

    Args:
        None

    Returns:
        None
    """
    bpy.ops.object.select_all(action="DESELECT")
    for obj in bpy.context.scene.objects:
        if obj.hide_select:
            continue
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


def get_hierarchy_bbox(obj) -> tuple[float, float]:
    """
    Calculate the bounding box of an object and its children.

    Args:
        obj (bpy.types.Object): The root object.

    Returns:
        tuple: A tuple containing the minimum and maximum coordinates of the bounding box.
    """
    # Ensure the object's matrix_world is updated
    bpy.context.view_layer.update()

    # Initialize min and max coordinates with extremely large and small values
    min_coord = [float("inf"), float("inf"), float("inf")]
    max_coord = [-float("inf"), -float("inf"), -float("inf")]

    # Function to update min and max coordinates
    def update_bounds(obj: bpy.types.Object) -> None:
        """
        Update the minimum and maximum coordinates based on the object's bounding box.

        Args:
            obj (bpy.types.Object): The object whose bounding box is to be updated.

        Returns:
            None
        """
        # Update the object's bounding box based on its world matrix
        bbox_corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
        for corner in bbox_corners:
            for i in range(3):
                min_coord[i] = min(min_coord[i], corner[i])
                max_coord[i] = max(max_coord[i], corner[i])

    # Recursive function to process each object
    def process_object(obj: bpy.types.Object) -> None:
        """
        Recursively process each object and update bounding box coordinates.

        Args:
            obj (bpy.types.Object): The object to be processed.

        Returns:
            None
        """
        update_bounds(obj)
        for child in obj.children:
            process_object(child)

    # Start processing from the root object
    process_object(obj)

    return min_coord, max_coord


def remove_small_geometry(
    obj: bpy.types.Object, min_vertex_count: int = 10
) -> Optional[bpy.types.Object]:
    """
    Remove free-hanging geometry with fewer vertices than specified by separating by loose parts,
    deleting small ones, and re-joining them.

    Args:
        obj (bpy.types.Object): The object to process.
        min_vertex_count (int, optional): Minimum number of vertices required to keep a part of the mesh. Default is 10.

    Returns:
        bpy.types.Object or None: The processed object if successful, None otherwise.
    """
    # Ensure the object is a mesh
    if obj is not None and obj.type != "MESH":
        print("Object is not a mesh.")
        return None

    # Make sure the object is active and we're in object mode
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    # select all children
    for child in obj.children:
        child.select_set(True)
    bpy.ops.object.mode_set(mode="OBJECT")

    # Separate by loose parts
    bpy.ops.mesh.separate(type="LOOSE")
    bpy.ops.object.mode_set(mode="OBJECT")

    # Deselect all to start clean
    bpy.ops.object.select_all(action="DESELECT")

    # Iterate over all new objects created by the separate operation
    for ob in bpy.context.selected_objects:
        # Re-select the object to make it active
        bpy.context.view_layer.objects.active = ob
        ob.select_set(True)

        # Check vertex count
        if len(ob.data.vertices) < min_vertex_count:
            # Delete the object if it doesn't meet the vertex count requirement
            bpy.ops.object.delete()

    # Optionally, re-join remaining objects if necessary
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.join()
    bpy.ops.object.mode_set(mode="OBJECT")
    print(
        "Processed geometry, removing parts with fewer than",
        min_vertex_count,
        "vertices.",
    )
    return obj


def normalize_object_scale(
    obj: bpy.types.Object, scale_factor: float = 1.0
) -> bpy.types.Object:
    """
    Scales the object by a factor.

    Args:
        obj (bpy.types.Object): The object to scale.
        scale_factor (float, optional): The factor to scale the object by. Defaults to 1.0.

    Returns:
        bpy.types.Object: The scaled object.
    """
    # Get the bounding box of the object and its children
    bbox_min, bbox_max = get_hierarchy_bbox(obj)

    # Calculate the scale of the bounding box and scale the object if necessary
    bbox_dimensions = [bbox_max[i] - bbox_min[i] for i in range(3)]
    max_dimension = max(bbox_dimensions)
    scale = scale_factor / max_dimension
    obj.scale = (scale, scale, scale)
    # make sure object is active and apply the scale
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return obj


def get_meshes_in_hierarchy(obj: bpy.types.Object) -> List[bpy.types.Object]:
    """
    Recursively collects all mesh objects in the hierarchy starting from the given object.

    Args:
        obj (bpy.types.Object): The root object from which to start collecting mesh objects.

    Returns:
        List[bpy.types.Object]: A list of mesh objects found in the hierarchy.
    """
    # Initialize an empty list to store mesh objects
    meshes = []

    # Check if the current object is a mesh and add it to the list if it is
    if obj.type == "MESH":
        meshes.append(obj)

    # Initialize an empty list to store mesh objects from child objects
    new_meshes = []

    # Recursively call the function for each child object and collect their meshes
    for child in obj.children:
        # Add meshes from child objects to the list
        new_meshes += get_meshes_in_hierarchy(child)

    # Combine meshes from the current object and its children and return the list
    return meshes + new_meshes


def remove_blendshapes_from_hierarchy(obj: bpy.types.Object) -> None:
    """
    Recursively removes blendshapes from all models in the hierarchy under the given object.

    Args:
        obj (bpy.types.Object): The root object of the hierarchy.

    Returns:
        None
    """
    # Ensure context is correct
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="DESELECT")

    def remove_blendshapes(obj):
        if obj.type == "MESH":
            # Select and make the mesh active
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)

            # Remove blendshapes
            if obj.data.shape_keys:
                obj.shape_key_clear()

    # Traverse the hierarchy and remove blendshapes
    def traverse_hierarchy(obj):
        remove_blendshapes(obj)
        for child in obj.children:
            traverse_hierarchy(child)

    # Start traversing from the given object
    traverse_hierarchy(obj)

    # Deselect everything to clean up
    bpy.ops.object.select_all(action="DESELECT")


def apply_and_remove_armatures():
    """
    Apply armature modifiers to meshes and remove armature objects.

    Args:
        None

    Returns:
        None
    """

    # Ensure context is correct
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="DESELECT")

    # Iterate over all objects in the scene
    for obj in bpy.data.objects:
        # Check if the object is a mesh with an armature modifier
        if obj.type == "MESH":
            for modifier in obj.modifiers:
                if modifier.type == "ARMATURE" and modifier.object is not None:
                    try:
                        remove_blendshapes_from_hierarchy(obj)
                    except:
                        print("Error removing blendshapes from object.")
                        # write a log file with the error
                        with open("error_log.txt", "a") as f:
                            f.write("Error removing blendshapes from object.\n")
                    # Select and make the mesh active
                    bpy.context.view_layer.objects.active = obj
                    obj.select_set(True)

                    # Apply the armature modifier
                    bpy.ops.object.modifier_apply(modifier=modifier.name)

                    # Deselect everything to clean up for the next iteration
                    bpy.ops.object.select_all(action="DESELECT")


def apply_all_modifiers(obj: bpy.types.Object):
    """
    Recursively apply all modifiers to the object and its children.

    Args:
        obj (bpy.types.Object): The root object.

    Return:
        None
    """

    # Traverse the hierarchy and apply all modifiers
    def recurse(obj):
        # Set the active object to the current object
        bpy.context.view_layer.objects.active = obj
        # Check if the object has modifiers
        if obj.modifiers:
            # Apply each modifier
            for modifier in obj.modifiers:
                bpy.ops.object.modifier_apply(modifier=modifier.name)

    # Recursively apply modifiers to children
    for child in obj.children:
        recurse(child)

    # Apply modifiers to the root object itself
    recurse(obj)


def optimize_meshes_in_hierarchy(obj: bpy.types.Object) -> None:
    """
    Recursively optimize meshes in the hierarchy by removing doubles and setting materials to double-sided.

    Args:
        obj (bpy.types.Object): The root object.

    Returns:
        None
    """

    if obj.type == "MESH":
        # Go into edit mode and select the mesh
        bpy.context.view_layer.objects.active = obj

        # Go to edit mode
        bpy.ops.object.mode_set(mode="EDIT")

        # Select all verts
        bpy.ops.mesh.select_all(action="SELECT")

        bpy.ops.mesh.remove_doubles(threshold=0.0001)
        angle_limit = 0.000174533 * 10

        # Go to lines mode
        bpy.ops.mesh.select_mode(type="EDGE")

        # Deselect all
        bpy.ops.mesh.select_all(action="DESELECT")

        # Select all edges
        bpy.ops.mesh.select_all(action="SELECT")

        # bpy.ops.mesh.dissolve_limited(angle_limit=angle_limit, use_dissolve_boundaries=True, delimit={'NORMAL', 'MATERIAL', 'SEAM', 'SHARP', 'UV'})

        # Set all materials to be double sided
        for slot in obj.material_slots:
            # slot.material.use_backface_culling = False
            if slot.material.blend_method == "BLEND":
                slot.material.blend_method = "HASHED"

        # Return to object mode
        bpy.ops.object.mode_set(mode="OBJECT")

    for child in obj.children:
        optimize_meshes_in_hierarchy(child)


def join_objects_in_hierarchy(obj: bpy.types.Object) -> None:
    """
    Joins a list of objects into a single object.

    Args:
        objects (List[bpy.types.Object]): List of objects to join.

    Returns:
        None
    """

    meshes = get_meshes_in_hierarchy(obj)

    # Select and activate meshes
    bpy.ops.object.select_all(action="DESELECT")
    for mesh in meshes:
        mesh.select_set(True)

    # Set the last selected mesh as active and check if it's valid for mode setting
    if meshes:
        bpy.context.view_layer.objects.active = meshes[0]
        if (
            bpy.context.view_layer.objects.active is not None
            and bpy.context.view_layer.objects.active.type == "MESH"
        ):
            # Use Context.temp_override() to create a temporary context override
            with bpy.context.temp_override(
                active_object=bpy.context.view_layer.objects.active,
                selected_objects=meshes,
            ):
                # Set the object mode to 'OBJECT' using the operator with the temporary context override
                bpy.ops.object.mode_set(mode="OBJECT")

                # Join meshes using the bpy.ops.object.join() operator with a custom context override
                if len(meshes) > 1:
                    bpy.ops.object.join()
                    print("Joined", len(meshes), "meshes.")
                else:
                    print("Not enough meshes to join.")
        else:
            print("Active object is not a valid mesh.")
    else:
        print("No meshes found to set as active.")


def set_pivot_to_bottom(obj: bpy.types.Object) -> None:
    """
    Set the pivot of the object to the center of mass, and the Z-coordinate to the bottom of the bounding box.

    Args:
        obj (bpy.types.Object): The object to adjust.

    Returns:
        None
    """
    # Calculate the center of mass
    bpy.context.view_layer.update()
    center_of_mass = obj.location

    # Calculate the bounding box bottom
    bbox_min = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box][0]
    for corner in obj.bound_box:
        world_corner = obj.matrix_world @ Vector(corner)
        if world_corner.z < bbox_min.z:
            bbox_min = world_corner

    # Set origin to the center of mass, then adjust Z-coordinate to the bottom of the bounding box
    bpy.ops.object.origin_set(type="ORIGIN_CENTER_OF_MASS", center="BOUNDS")
    obj.location.z = center_of_mass.z - bbox_min.z
    obj.location.y = 0
    obj.location.x = 0

    bpy.context.scene.cursor.location = (0, 0, 0)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")


def unparent_keep_transform(obj: bpy.types.Object) -> None:
    """
    Unparents an object but keeps its transform.

    Args:
        obj (bpy.types.Object): The object to unparent.

    Returns:
        None
    """
    # clear the parent object, but keep the transform
    bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")
    # clear rotation and scale and apply
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)


def delete_all_empties() -> None:
    """Deletes all empty objects in the scene.

    Args:
        None

    Returns:
        None
    """
    for obj in bpy.data.objects:
        if obj.type == "EMPTY":
            # if the object is hidden from selection, ignore
            if obj.hide_select:
                continue
            bpy.data.objects.remove(obj, do_unlink=True)


def lock_all_objects() -> None:
    """
    Locks all objects in the scene from selection and returns a list of these objects.

    Args:
        None

    Returns:
        None
    """
    locked_objects = []
    for obj in bpy.context.scene.objects:
        obj.hide_select = True
        locked_objects.append(obj)
    return locked_objects


def unlock_objects(objs: List[bpy.types.Object]) -> None:
    """
    Unlocks a given list of objects for selection.

    Args:
        objs (list): A list of Blender objects to be unlocked.

    Returns:
        None
    """
    for obj in objs:
        obj.hide_select = False
