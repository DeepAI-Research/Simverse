import json
import re

def create_finetuning_data(input_file, output_file):
    # Read the input JSON file
    with open(input_file, 'r') as f:
        data = json.load(f)

    # Function to create a brief summary from the caption
    def create_brief_summary(caption):
        # Split the caption and take the first sentence or up to 10 words
        words = caption.split()
        return ' '.join(words[:min(10, len(words))]).rstrip('.') + '...'

    # Create input-output pairs for fine-tuning
    finetuning_data = []
    for caption, combination in data.items():
        brief_summary = create_brief_summary(caption)
        input_prompt = f"Describe this scene: {brief_summary}"
        finetuning_data.append({
            "input": input_prompt,
            "output": caption
        })

    # Write the fine-tuning data to the output JSONL file
    with open(output_file, 'w') as f:
        for item in finetuning_data:
            json.dump(item, f)
            f.write('\n')

    print(f"Fine-tuning data has been written to {output_file}")

# Usage
input_file = 'caption_pairs.json'
output_file = 'finetune_data.jsonl'
create_finetuning_data(input_file, output_file)