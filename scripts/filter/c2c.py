# import json

# def create_finetuning_data(input_file, output_file):
#     # Read the input JSON file
#     with open(input_file, 'r') as f:
#         data = json.load(f)

#     # Create input-output pairs for fine-tuning
#     finetuning_data = []
#     for combination in data['combinations']:
#         caption = combination.get('caption', '')
#         if caption:
#             finetuning_data.append({
#                 "input": caption,
#                 "output": json.dumps(combination)  # Convert the entire combination to a JSON string
#             })

#     # Write the fine-tuning data to the output JSONL file
#     with open(output_file, 'w') as f:
#         for item in finetuning_data:
#             json.dump(item, f)
#             f.write('\n')

#     print(f"Fine-tuning data has been written to {output_file}")

# # Usage
# input_file = './combinations.json'
# output_file = 'finetune_data.jsonl'
# create_finetuning_data(input_file, output_file)


import json
import jsonlines

def create_finetuning_data(input_file, output_file):
    # Read the input JSON file
    with open(input_file, 'r') as f:
        data = json.load(f)

    # Create input-output pairs for fine-tuning
    finetuning_data = []
    if 'combinations' in data:
        for combination in data['combinations']:
            caption = combination.get('caption', '')
            if caption:
                finetuning_data.append({
                    "input": caption,
                    "output": json.dumps(combination)  # Convert the entire combination to a JSON string
                })

    # Write the fine-tuning data to the output JSONL file
    with jsonlines.open(output_file, 'w') as writer:
        writer.write_all(finetuning_data)

    print(f"Fine-tuning data has been written to {output_file}")

# Usage
input_file = './combinations.json'
output_file = 'finetune_data.jsonl'
create_finetuning_data(input_file, output_file)
