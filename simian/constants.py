from typing import Callable, Dict
import bpy

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
