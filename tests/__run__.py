import os
import subprocess
import sys

files = os.listdir("tests")
test_files = [file for file in files if file.endswith("_test.py")]

# Append Simian to sys.path before importing from package
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))

from simian.utils import get_blender_path
blender_command = get_blender_path()

# Flag to track if any test has failed
test_failed = False

for test_file in test_files:
    print(f"Running tests in {test_file}...")
    cmd = [blender_command, "--background", "--python", f"tests/{test_file}"]
    
    # Run the test file and capture the output
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Check if there are any errors in the output
    if "FAILED" in result.stdout or "ERROR" in result.stdout or "Traceback" in result.stdout:
        print(f"Tests in {test_file} failed!")
        print("Error output:")
        print(result.stdout)
        test_failed = True
    else:
        print(f"Tests in {test_file} passed.")

# Exit with appropriate exit code based on test results
if test_failed:
    print("Some tests failed. Exiting with exit code 1.")
    sys.exit(1)
else:
    print("All tests passed. Exiting with exit code 0.")
    sys.exit(0)