import multiprocessing
import os
import subprocess
from unittest.mock import patch, MagicMock
import pytest
import pandas as pd
from batch import render_objects, get_combination_objects

def test_get_combination_objects():
    # Setup the expected DataFrame
    expected_df = pd.DataFrame({'id': [1, 2], 'name': ['Object1', 'Object2']})
    
    # Mock pd.read_json to return a specific DataFrame
    with patch('pandas.read_json', return_value=expected_df):
        df = get_combination_objects()
        pd.testing.assert_frame_equal(df, expected_df)

def test_render_objects():
    # Mock subprocess.run to avoid actual execution
    with patch('subprocess.run') as mock_run, \
         patch('os.makedirs'), \
         patch('os.path.exists', return_value=True), \
         patch('os.path.dirname', return_value='/fake/dir'), \
         patch('os.path.realpath', return_value='/fake/dir'), \
         patch.object(multiprocessing, 'cpu_count', return_value=4):
        # Call the function
        render_objects(
            download_dir='/fake/download',
            processes=12,
            save_repo_format='zip',
            render_timeout=3000,
            gpu_devices=[0, 1],
            width=1920,
            height=1080,
            start_index=0,
            end_index=2,
            start_frame=1,
            end_frame=25
        )
        
        # Assertions to check if subprocess.run was called correctly
        assert mock_run.called
        # Check the call arguments to ensure the correct command is constructed
        args, kwargs = mock_run.call_args
        command = args[0][1]  # This depends on how the command is structured in your actual function
        assert '1920' in command
        assert '1080' in command
        assert '--combination_index 0' in command
        assert '--start_frame 1' in command
        assert '--end_frame 25' in command
        assert '--output_dir /fake/dir/../renders' in command
        assert '--background_path /fake/dir/../backgrounds' in command


def test_render_objects_missing_blender():
    # Test FileNotFoundError when Blender is not found
    with patch('os.path.exists', return_value=False):
        with pytest.raises(FileNotFoundError):
            render_objects()


# Run tests if this file is executed as a script
if __name__ == "__main__":
    pytest.main()
