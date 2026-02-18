import json

# Your file paths
input_path = r"C:\Users\slimm\Desktop\WahapediaExport\OPR Data Export\data.json"
output_path = r"C:\Users\slimm\Desktop\WahapediaExport\OPR Data Export\data_pretty.json"

try:
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    with open(output_path, 'w', encoding='utf-8') as f:
        # indent=4 creates the human-readable format
        json.dump(data, f, indent=4, sort_keys=True)
    
    print(f"Success! Pretty file saved to: {output_path}")
except Exception as e:
    print(f"Error: {e}")
