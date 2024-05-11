import bpy
from typing import Any


def setup_compositor_for_black_and_white(context: bpy.types.Context) -> None:
    """
    Sets up the compositor for a black and white effect using Blender's Eevee engine.
    Assumes that the context provided is valid and that the scene uses Eevee.

    Args:
        context (bpy.types.Context): The Blender context.

    Returns:
        None
    """
    # Ensure the use of nodes in the scene's compositing.
    scene = context.scene
    scene.use_nodes = True
    tree = scene.node_tree

    # Create necessary nodes
    render_layers = tree.nodes.new(type="CompositorNodeRLayers")
    hue_sat = tree.nodes.new(type="CompositorNodeHueSat")
    composite = tree.nodes.new(
        type="CompositorNodeComposite"
    )  # Ensure there's a composite node

    # Position nodes
    render_layers.location = (-300, 0)
    hue_sat.location = (100, 0)
    composite.location = (300, 0)

    # Configure Hue Sat node for desaturation
    hue_sat.inputs["Saturation"].default_value = (
        0  # Reduce saturation to zero to get grayscale
    )
    # increase contrast
    hue_sat.inputs["Value"].default_value = 2.0

    # Link nodes
    links = tree.links
    links.new(render_layers.outputs["Image"], hue_sat.inputs["Image"])
    links.new(
        hue_sat.outputs["Image"], composite.inputs["Image"]
    )  # Direct output to the composite node


def setup_compositor_for_cel_shading(context: bpy.types.Context) -> None:
    """
    Sets up the compositor for a cel shading effect using Blender's Eevee engine.
    The node setup is based on the theory of using normal and diffuse passes to create
    a stylized, non-photorealistic look with subtle transitions between shadows and highlights.
    Assumes the context provided is valid and that the scene uses Eevee.

    Args:
        context (bpy.types.Context): The Blender context.

    Returns:
        None
    """
    # Ensure the use of nodes in the scene's compositing
    scene: bpy.types.Scene = context.scene
    scene.use_nodes = True
    tree: bpy.types.NodeTree = scene.node_tree

    # Create necessary nodes for compositing
    # Render Layers Node: Provides access to the render passes
    # Normal Node: Converts the normal pass into a usable format
    # Color Ramp Nodes: Control the shading and highlight areas
    # Mix RGB Nodes: Combine the shading and highlight with the diffuse color
    # Composite Node: The final output node
    render_layers: Any = tree.nodes.new(type="CompositorNodeRLayers")
    normal_node: Any = tree.nodes.new(type="CompositorNodeNormal")
    color_ramp_shadow: Any = tree.nodes.new(type="CompositorNodeValToRGB")
    color_ramp_highlight: Any = tree.nodes.new(type="CompositorNodeValToRGB")
    mix_rgb_shadow: Any = tree.nodes.new(type="CompositorNodeMixRGB")
    mix_rgb_highlight: Any = tree.nodes.new(type="CompositorNodeMixRGB")
    alpha_over: Any = tree.nodes.new(
        type="CompositorNodeAlphaOver"
    )  # Add an Alpha Over node
    composite: Any = tree.nodes.new(type="CompositorNodeComposite")

    # Configure Mix RGB nodes
    # Multiply blend mode for shadows to darken the diffuse color slightly
    # Overlay blend mode for highlights to create subtle bright highlights
    # Reference: https://docs.blender.org/manual/en/latest/compositing/types/color/mix.html
    mix_rgb_shadow.blend_type = "MULTIPLY"
    mix_rgb_highlight.blend_type = "OVERLAY"
    mix_rgb_shadow.use_clamp = True
    mix_rgb_highlight.use_clamp = True

    # Configure Shadow Color Ramp
    color_ramp_shadow.color_ramp.interpolation = "EASE"
    color_ramp_shadow.color_ramp.elements[0].position = 0.5
    color_ramp_shadow.color_ramp.elements[1].position = 0.8
    color_ramp_shadow.color_ramp.elements[0].color = (0.5, 0.5, 0.5, 1)  # Mid Gray
    color_ramp_shadow.color_ramp.elements[1].color = (1, 1, 1, 1)  # White

    # Configure Highlight Color Ramp
    color_ramp_highlight.color_ramp.interpolation = "EASE"
    color_ramp_highlight.color_ramp.elements[0].position = 0.8
    color_ramp_highlight.color_ramp.elements[1].position = 0.95
    color_ramp_highlight.color_ramp.elements[0].color = (0, 0, 0, 1)  # Black
    color_ramp_highlight.color_ramp.elements[1].color = (1, 1, 1, 1)  # White

    # Adjust the Mix RGB nodes
    mix_rgb_shadow.blend_type = "MULTIPLY"
    mix_rgb_shadow.inputs[0].default_value = 1.0  # Reduce the shadow intensity

    mix_rgb_highlight.blend_type = (
        "SCREEN"  # Change to 'SCREEN' for better highlight blending
    )
    mix_rgb_highlight.inputs[0].default_value = 0.5  # Reduce the highlight intensity

    # Link nodes
    links: Any = tree.links
    # Connect Normal pass to Normal node for shading information
    links.new(render_layers.outputs["Normal"], normal_node.inputs["Normal"])
    # Connect Normal node to Shadow Color Ramp for shadow intensity control
    links.new(normal_node.outputs["Dot"], color_ramp_shadow.inputs["Fac"])
    # Connect Normal node to Highlight Color Ramp for highlight intensity control
    links.new(normal_node.outputs["Dot"], color_ramp_highlight.inputs["Fac"])
    # Connect Shadow Color Ramp to Mix RGB Shadow node for shadow color blending
    links.new(color_ramp_shadow.outputs["Image"], mix_rgb_shadow.inputs[2])
    # Connect Diffuse pass to Mix RGB Shadow node as the base color
    links.new(render_layers.outputs["Image"], mix_rgb_shadow.inputs[1])
    # Connect Mix RGB Shadow to Mix RGB Highlight for combining shadows with the base color
    links.new(mix_rgb_shadow.outputs["Image"], mix_rgb_highlight.inputs[1])
    # Connect Highlight Color Ramp to Mix RGB Highlight for adding highlights
    links.new(color_ramp_highlight.outputs["Image"], mix_rgb_highlight.inputs[2])
    # Connect Mix RGB Highlight to Composite node for final output
    links.new(
        mix_rgb_highlight.outputs["Image"], alpha_over.inputs[2]
    )  # Plug the cel-shaded result into the foreground input of Alpha Over
    links.new(
        render_layers.outputs["Env"], alpha_over.inputs[1]
    )  # Plug the environment pass into the background input of Alpha Over
    links.new(
        alpha_over.outputs["Image"], composite.inputs["Image"]
    )  # Plug the Alpha Over output into the Composite node


def setup_compositor_for_depth(context: bpy.types.Context) -> None:
    """
    Sets up the compositor for rendering a depth map using Blender's Eevee engine.
    Assumes that the context provided is valid and that the scene uses Eevee.

    Args:
        context (bpy.types.Context): The Blender context.

    Returns:
        None
    """
    # Ensure the use of nodes in the scene's compositing.
    scene: bpy.types.Scene = context.scene
    scene.use_nodes = True
    tree: bpy.types.NodeTree = scene.node_tree
    # Create necessary nodes
    render_layers: Any = tree.nodes.new(type="CompositorNodeRLayers")
    normalize: Any = tree.nodes.new(type="CompositorNodeNormalize")
    composite: Any = tree.nodes.new(
        type="CompositorNodeComposite"
    )  # Ensure there's a composite node

    # Position nodes
    render_layers.location = (-300, 0)
    normalize.location = (0, 0)
    composite.location = (300, 0)

    # Enable the Depth pass in the View Layer properties
    view_layer: bpy.types.ViewLayer = context.view_layer
    view_layer.use_pass_z = True

    # Link nodes
    links: Any = tree.links
    links.new(render_layers.outputs["Depth"], normalize.inputs["Value"])
    links.new(
        normalize.outputs["Value"], composite.inputs["Image"]
    )  # Direct output to the composite node


effects = {
    "black_and_white": setup_compositor_for_black_and_white,
    "cel_shading": setup_compositor_for_cel_shading,
    "depth": setup_compositor_for_depth,
}


def enable_effect(context: bpy.types.Context, effect_name: str) -> None:
    """
    Enables the cel shading effect in the compositor.

    Args:
        context (bpy.types.Context): The Blender context.
        effect_name (str): The name of the effect to enable.

    Returns:
        None
    """
    # Make sure compositor use is turned on
    context.scene.render.use_compositing = True
    context.scene.use_nodes = True
    tree: bpy.types.NodeTree = context.scene.node_tree

    # Clear existing nodes
    for node in tree.nodes:
        tree.nodes.remove(node)

    # Enable Normal Pass and Diffuse Pass
    # These passes provide the necessary information for shading and color
    # Reference: https://docs.blender.org/manual/en/latest/render/layers/passes.html
    view_layer: bpy.types.ViewLayer = context.view_layer
    view_layer.use_pass_normal = True
    view_layer.use_pass_diffuse_color = True
    view_layer.use_pass_environment = True  # Enable the environment pass
    view_layer.use_pass_z = True

    # get the function for the effect
    effect_function: Any = effects.get(effect_name)

    # Set up the nodes for cel shading
    effect_function(context)
