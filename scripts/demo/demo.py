import os
import json
import random
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

def load_combinations(file_path: str):
    logger.debug(f"Loading combinations from file: {file_path}")
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except Exception as e:
        logger.error(f"Failed to load combinations from file: {file_path} with error: {str(e)}")
        return None

def extract_random_indices(data, count=5):
    logger.debug(f"Extracting {count} random indices from data")
    combinations = data["combinations"]
    total_count = len(combinations)
    random_indices = random.sample(range(total_count), count)
    extracted_combinations = [combinations[i] for i in random_indices]
    return extracted_combinations

def save_to_file(data, file_path: str):
    try:
        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)
        logger.info(f"Saved extracted combinations to {file_path}")
    except Exception as e:
        logger.error(f"Failed to save combinations to file: {file_path} with error: {str(e)}")

if __name__ == "__main__":
    # Path to the combinations file
    combinations_file_path = "combinations.json"
    
    # Load combinations from the file
    if os.path.exists(combinations_file_path):
        data = load_combinations(combinations_file_path)
        if data:
            extracted_combinations = extract_random_indices(data)
            output_path = "demo.json"
            save_to_file({"combinations": extracted_combinations}, output_path)
        else:
            logger.error(f"Failed to load data from {combinations_file_path}")
    else:
        logger.error(f"{combinations_file_path} file not found")
