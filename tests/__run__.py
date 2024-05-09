import os
import subprocess
import sys

# TODO: Run all tests in /tests
# If all tests run and the output exits with code 0, then the tests have passed
# If there is an error, then the tests have failed
# First, find all files in /tests that end with _test.py
files = os.listdir("tests")
test_files = [file for file in files if file.endswith("_test.py")]

# Check if we are on Darwin (macOS)
os_type = os.uname().sysname.lower()
if os_type == "darwin":
    blender_command = "/Applications/Blender.app/Contents/MacOS/Blender"
else:
    blender_command = "blender"

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