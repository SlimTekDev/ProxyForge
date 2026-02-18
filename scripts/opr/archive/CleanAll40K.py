import pandas as pd
import re
import os

# Updated to your specific path
source_folder = r'C:\Users\slimm\Desktop\WahapediaExport\Source Files'
output_folder = os.path.join(source_folder, 'Cleaned_CSVs')

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

def clean_data(text):
    if not isinstance(text, str): return text
    # Strip HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove non-ASCII/Problematic characters
    return text.encode('ascii', 'ignore').decode('ascii')

print(f"Starting batch clean in: {source_folder}")

for filename in os.listdir(source_folder):
    if filename.endswith('.csv'):
        print(f"Processing: {filename}...")
        
        file_path = os.path.join(source_folder, filename)
        
        # low_memory=False helps with mixed data types in large files
        try:
            # Added on_bad_lines to skip rows with too many commas
            df = pd.read_csv(file_path, encoding='latin1', low_memory=False, on_bad_lines='warn')
        except Exception as e:
            print(f"Skipping {filename} due to error: {e}")
            continue
        
        # Clean every cell
        df_cleaned = df.map(clean_data)
        
        output_path = os.path.join(output_folder, filename)
        df_cleaned.to_csv(output_path, index=False, encoding='utf-8')

print(f"\nDone! All cleaned files are in: {output_folder}")