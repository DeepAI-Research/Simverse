import os
import bpy
from unittest.mock import patch, MagicMock
import pytest
from simian.background import get_background_path, get_background, set_background, create_photosphere, create_photosphere_material

def test_get_background_path():
    combination = {
        "background": {
            "id": "123",
            "from": "test_dataset"
        }
    }
    background_path = "/fake/path"
    expected_result = f"/fake/path/test_dataset/123.hdr"
    result = get_background_path(background_path, combination)
    assert result == expected_result, "Background path is not correct."

def test_get_background():
    combination = {
        "background": {
            "url": "http://example.com/image.hdr",
            "id": "123",
            "from": "test_dataset"
        }
    }
    background_path = "/fake/path"

    # Mock os.makedirs and os.path.exists
    with patch('os.makedirs'), patch('os.path.exists', return_value=False), \
         patch('requests.get') as mock_get, patch('builtins.open', new_callable=MagicMock):
        mock_response = MagicMock()
        mock_response.content = b'fake data'
        mock_get.return_value = mock_response
        get_background(background_path, combination)
        mock_get.assert_called_with("http://example.com/image.hdr")

def test_set_background():
    combination = {
        "background": {
            "id": "123",
            "from": "test_dataset",
            "url": "http://example.com/image.hdr"
        }
    }
    background_path = "/fake/path"

    # Mock get_background and Blender specific functions
    with patch('background.get_background'), \
         patch('background.get_background_path', return_value="/fake/path/test_dataset/123.hdr"), \
         patch.object(bpy.data, 'images', create=True) as mock_images, \
         patch('bpy.context'):
        set_background(background_path, combination)
        mock_images.load.assert_called_with("/fake/path/test_dataset/123.hdr")

def test_create_photosphere():
    background_path = "/fake/path"
    combination = {
        "background": {
            "id": "123",
            "from": "test_dataset"
        }
    }

    # Mock Blender functions and create_photosphere_material
    with patch('bpy.ops.mesh.primitive_uv_sphere_add'), \
         patch('bpy.ops.object.shade_smooth'), \
         patch('bpy.ops.object.mode_set'), \
         patch('bpy.ops.mesh.select_all'), \
         patch('bpy.ops.mesh.flip_normals'), \
         patch('bpy.context', create=True) as mock_context, \
         patch('background.create_photosphere_material') as mock_create_material:
        mock_context.object = MagicMock()
        sphere = create_photosphere(background_path, combination)
        mock_create_material.assert_called_once()
        assert sphere.name == "Photosphere"

def test_create_photosphere_material():
    sphere = MagicMock()
    background_path = "/fake/path"
    combination = {
        "background": {
            "id": "123",
            "from": "test_dataset"
        }
    }

    # Mock Blender material and image loading
    with patch.object(bpy.data, 'materials', create=True) as mock_materials, \
         patch.object(bpy.data.images, 'load', return_value=MagicMock()) as mock_load, \
         patch('background.get_background_path', return_value="/fake/path/test_dataset/123.hdr"):
        create_photosphere_material(background_path, combination, sphere)
        mock_materials.new.assert_called_with(name="PhotosphereMaterial")
        mock_load.assert_called_with("/fake/path/test_dataset/123.hdr")

# Run tests if this file is executed as a script
if __name__ == "__main__":
    pytest.main()
