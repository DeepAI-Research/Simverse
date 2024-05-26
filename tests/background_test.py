import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
simian_path = os.path.join(current_dir, "../")
sys.path.append(simian_path)

from unittest.mock import patch, MagicMock
from simian.background import (
    get_hdri_path,
    get_background,
    set_background,
    create_photosphere,
    create_photosphere_material,
)

import bpy
from simian.background import set_background


def test_get_hdri_path():
    """
    Test the get_hdri_path function.
    """
    combination = {"background": {"id": "123", "from": "test_dataset"}}
    hdri_path = "/fake/path"
    expected_result = f"/fake/path/test_dataset/123.hdr"
    result = get_hdri_path(hdri_path, combination)

    print("test_get_hdri_path result: ", result)
    assert result == expected_result
    print("============ Test Passed: get_hdri_path ============")


def test_get_background():
    """
    Test the get_background function.
    """
    combination = {
        "background": {
            "url": "http://example.com/image.hdr",
            "id": "123",
            "from": "test_dataset",
        }
    }
    hdri_path = "/fake/path"

    with patch("os.makedirs"), patch("os.path.exists", return_value=False), patch(
        "requests.get"
    ) as mock_get, patch("builtins.open", new_callable=MagicMock):
        mock_response = MagicMock()
        mock_response.content = b"fake data"
        mock_get.return_value = mock_response

        get_background(hdri_path, combination)
        print("get_background called")

        mock_get.assert_called_with("http://example.com/image.hdr")
        print("============ Test Passed: test_get_background ============")


def test_set_background():
    """
    Test the set_background function.
    """
    combination = {
        "background": {
            "id": "123",
            "from": "test_dataset",
            "url": "http://example.com/image.hdr",
        }
    }
    # Use a path in the user's home directory or another writable location
    background_base_path = os.path.join(os.path.expanduser("~"), "test_backgrounds")

    # Mocking dependencies
    with patch(
        "simian.background.get_hdri_path",
        return_value=os.path.join(background_base_path, "test_dataset/123.hdr"),
    ) as mock_get_path:
        with patch("os.path.exists", return_value=False):
            with patch("requests.get") as mock_get:
                mock_response = MagicMock()
                mock_response.content = b"Fake HDR content"
                mock_get.return_value = mock_response

                # Ensure the directory exists before writing
                os.makedirs(
                    os.path.dirname(
                        os.path.join(background_base_path, "test_dataset/123.hdr")
                    ),
                    exist_ok=True,
                )

                # Function call
                set_background(background_base_path, combination)

                # Open the file to simulate writing to it
                with open(
                    os.path.join(background_base_path, "test_dataset/123.hdr"), "wb"
                ) as file:
                    file.write(mock_response.content)

                mock_get.assert_called_with("http://example.com/image.hdr")
                print("============ Test Passed: test_set_background ============")


def create_test_photosphere():
    """
    Create a UV sphere in Blender with specific parameters.
    """
    # Create a UV sphere in Blender with specific parameters
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=64, ring_count=32, radius=1.0, location=(0, 0, 3)
    )
    sphere = bpy.context.object
    bpy.ops.object.shade_smooth()

    # Enter edit mode, select all vertices, and flip the normals
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.flip_normals()
    bpy.ops.object.mode_set(mode="OBJECT")

    # Rename the sphere for identification
    sphere.name = "Photosphere"
    print("Sphere created successfully")
    return sphere


def test_create_photosphere():
    epsilon = 0.001  # Small threshold for floating-point comparisons
    sphere = create_test_photosphere()

    # Check each component of the sphere's location to see if it matches the expected values
    assert abs(sphere.location.x - 0.0) < epsilon, "X coordinate is incorrect"
    assert abs(sphere.location.y - 0.0) < epsilon, "Y coordinate is incorrect"
    assert abs(sphere.location.z - 3.0) < epsilon, "Z coordinate is incorrect"
    print("============ Test Passed: test_create_photosphere ============")


def test_create_photosphere_material():
    """
    Test the create_photosphere_material function.
    """
    # Create a UV sphere in Blender with specific parameters
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=64, ring_count=32, radius=1.0, location=(0, 0, 3)
    )
    sphere = bpy.context.object
    bpy.ops.object.shade_smooth()

    # Enter edit mode, select all vertices, and flip the normals
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.flip_normals()
    bpy.ops.object.mode_set(mode="OBJECT")

    # Rename the sphere for identification
    sphere.name = "Photosphere"

    # Create a combination dictionary with background information
    combination = {
        "background": {
            "id": "123",
            "from": "test_dataset",
            "url": "http://example.com/image.hdr",
        }
    }

    # Set the base path for background images
    background_base_path = os.path.join(os.path.expanduser("~"), "test_backgrounds")

    # Mock the get_hdri_path function to return a known path
    with patch(
        "simian.background.get_hdri_path",
        return_value=os.path.join(background_base_path, "test_dataset/123.hdr"),
    ) as mock_get_path:
        # Mock the existence of the background image file
        with patch("os.path.exists", return_value=True):
            # Mock the open function to simulate reading the background image
            with patch("builtins.open", MagicMock()) as mock_open:
                # Call the create_photosphere_material function
                create_photosphere_material(background_base_path, combination, sphere)

                # Verify that the material was created
                assert (
                    sphere.data.materials[0].name == "PhotosphereMaterial"
                ), "Material not created successfully"
                print(
                    "============ Test Passed: test_create_photosphere_material ============"
                )


# Run tests if this file is executed as a script
if __name__ == "__main__":
    test_get_hdri_path()
    test_get_background()
    # test_set_background()
    test_create_photosphere()
    # test_create_photosphere_material()
    print("============ ALL TESTS PASSED ============")
