import os
import numpy as np

from .constants import IMPORT_FUNCTIONS
import bpy
from mathutils import Matrix, Vector

def load_object(object_path: str) -> None:
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

        import_usdz(bpy.context, filepath=object_path, materials=True, animations=True)
        return None

    # load from existing import functions
    import_function = IMPORT_FUNCTIONS[file_extension]

    if file_extension == "blend":
        import_function(directory=object_path, link=False)
    elif file_extension in {"glb", "gltf"}:
        import_function(filepath=object_path, merge_vertices=True)
    else:
        import_function(filepath=object_path)

def delete_invisible_objects() -> None:
    """Deletes all invisible objects in the scene.

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

def get_hierarchy_bbox(obj):
    """Calculate the bounding box of an object and its children."""
    # Ensure the object's matrix_world is updated
    bpy.context.view_layer.update()
    
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

def remove_small_geometry(obj, min_vertex_count: int = 10) -> bpy.types.Object:
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
    bpy.context.view_layer.objects.active = obj
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
    for ob in bpy.context.selected_objects:
        # Re-select the object to make it active
        bpy.context.view_layer.objects.active = ob
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

def normalize_object_scale( obj: bpy.types.Object, scale_factor: float = 1.0) -> bpy.types.Object:
    """Scales the object by a factor.

    Args:
        obj (bpy.types.Object): The object to scale.
        scale_factor (float, optional): The factor to scale the object by. Defaults to 1.0.

    Returns:
        None
    """
    
    # Get the bounding box of the object and its children
    bbox_min, bbox_max = get_hierarchy_bbox(obj)
    
    # Calculate the scale of the bounding box and scale the object if necessary
    bbox_dimensions = [bbox_max[i] - bbox_min[i] for i in range(3)]
    max_dimension = max(bbox_dimensions)
    scale = scale_factor / max_dimension
    obj.scale = (scale, scale, scale)
    return obj


def get_meshes_in_hierarchy(obj):
        meshes = []
        if obj.type == 'MESH':
            meshes.append(obj)
        
        new_meshes = []
        for child in obj.children:
            new_meshes += get_meshes_in_hierarchy(child)
        return meshes + new_meshes


def apply_and_remove_armatures():
    # Ensure context is correct
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')

    # Iterate over all objects in the scene
    for obj in bpy.data.objects:
        # Check if the object is a mesh with an armature modifier
        if obj.type == 'MESH':
            for modifier in obj.modifiers:
                if modifier.type == 'ARMATURE' and modifier.object is not None:
                    # Select and make the mesh active
                    bpy.context.view_layer.objects.active = obj
                    obj.select_set(True)

                    # Apply the armature modifier
                    bpy.ops.object.modifier_apply(modifier=modifier.name)

                    # Deselect everything to clean up for the next iteration
                    bpy.ops.object.select_all(action='DESELECT')



def apply_all_modifiers(obj):
    # traverse the hierarchy and apply all modifiers
    def recurse(obj):
        bpy.context.view_layer.objects.active = obj
        if obj.modifiers:
            for modifier in obj.modifiers:
                bpy.ops.object.modifier_apply(modifier=modifier.name)
    for child in obj.children:
        recurse(child)
        recurse(obj)


def optimize_meshes_in_hierarchy(obj):
        if obj.type == 'MESH':
            # go into edit mode
            # select the mesh
            bpy.context.view_layer.objects.active = obj

            # go to edit mode
            bpy.ops.object.mode_set(mode='EDIT')
            
            # select all verts
            bpy.ops.mesh.select_all(action='SELECT')
            
            bpy.ops.mesh.remove_doubles(threshold=0.0001)
            angle_limit = 0.000174533 * 10
            
            # go to lines mode
            bpy.ops.mesh.select_mode(type="EDGE")
            
            # deselect all
            bpy.ops.mesh.select_all(action='DESELECT')
            
            # select all edges
            bpy.ops.mesh.select_all(action='SELECT')
            
            # bpy.ops.mesh.dissolve_limited(angle_limit=angle_limit, use_dissolve_boundaries=True, delimit={'NORMAL', 'MATERIAL', 'SEAM', 'SHARP', 'UV'})
            
            # set all materials to be double sided
            for slot in obj.material_slots:
                slot.material.use_backface_culling = False
                if slot.material.blend_method == 'BLEND':
                    slot.material.blend_method = 'HASHED'
            
            # return to object mode
            bpy.ops.object.mode_set(mode='OBJECT')
        
        for child in obj.children:
            optimize_meshes_in_hierarchy(child)


def remove_loose_meshes(obj, min_vertex_count: int = 6):
    meshes = get_meshes_in_hierarchy(obj)
    
    # Check if there is only one mesh object
    if len(meshes) == 1:
        # Set the mesh object as active and enter edit mode
        bpy.context.view_layer.objects.active = meshes[0]
        bpy.ops.object.mode_set(mode='EDIT')
        
        # select all
        bpy.ops.mesh.select_all(action='SELECT')
        
        # Separate the disconnected geometry into individual mesh objects
        bpy.ops.mesh.separate(type='LOOSE')
        
        bpy.ops.object.mode_set(mode='OBJECT')
    
    meshes = get_meshes_in_hierarchy(obj)
        
    # Remove meshes with less than 12 vertices
    meshes_to_remove = []
    for mesh in meshes:
        if len(mesh.data.vertices) < min_vertex_count:
            meshes_to_remove.append(mesh)

    for mesh in meshes_to_remove:
        meshes.remove(mesh)
        bpy.data.objects.remove(mesh, do_unlink=True)
    
    meshes = get_meshes_in_hierarchy(obj)

    # # Join the remaining meshes back together
    if len(meshes) > 1:
        # Set the last selected mesh as active
        bpy.context.view_layer.objects.active = meshes[-1]
        
        # Select all the meshes
        for mesh in meshes:
            mesh.select_set(True)
        
        # Join the selected meshes
        bpy.ops.object.join()
        


def join_objects_in_hierarchy(object: list) -> bpy.types.Object:
    """Joins a list of objects into a single object.
    
    
    Args:
        object (list): List of objects to join.
        context (context): Blender context.
        
    Returns:
        None
    """
    meshes = get_meshes_in_hierarchy(object)

    # Select and activate meshes
    bpy.ops.object.select_all(action='DESELECT')
    for mesh in meshes:
        mesh.select_set(True)

    # Set the last selected mesh as active and check if it's valid for mode setting
    if meshes:
        bpy.context.view_layer.objects.active = meshes[0]
        if bpy.context.view_layer.objects.active is not None and bpy.context.view_layer.objects.active.type == 'MESH':
            # Use Context.temp_override() to create a temporary context override
            with bpy.context.temp_override(active_object=bpy.context.view_layer.objects.active, selected_objects=meshes):
                # Set the object mode to 'OBJECT' using the operator with the temporary context override
                bpy.ops.object.mode_set(mode='OBJECT')
                
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
        
def set_pivot_to_bottom(obj):
    """Set the pivot of the object to the center of mass, and the Z-coordinate to the bottom of the bounding box.

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
    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='BOUNDS')
    obj.location.z =  center_of_mass.z - bbox_min.z
    obj.location.y = 0
    obj.location.x = 0
    
    bpy.context.scene.cursor.location = (0, 0, 0)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

def unparent_keep_transform(obj):
    """Unparents an object but keeps its transform.

    Args:
        obj (bpy.types.Object): The object to unparent.

    Returns:
        None
    """
    # clear the parent object, but keep the transform
    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

def delete_all_empties():
    """Deletes all empty objects in the scene.

    Returns:
        None
    """    
    for obj in bpy.data.objects:
        if obj.type == 'EMPTY':
            # if the object is hidden from selection, ignore
            if obj.hide_select:
                continue
            bpy.data.objects.remove(obj, do_unlink=True)
            
def lock_all_objects():
    """
    Locks all objects in the scene from selection and returns a list of these objects.
    """
    locked_objects = []
    for obj in bpy.context.scene.objects:
        obj.hide_select = True
        locked_objects.append(obj)
    return locked_objects

def unlock_objects(objects):
    """
    Unlocks a given list of objects for selection.
    
    Args:
    objects (list): A list of Blender objects to be unlocked.
    """
    for obj in objects:
        obj.hide_select = False
