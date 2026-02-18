import pandas as pd
import re
import os

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

print(f"Starting pipe-delimited batch clean in: {source_folder}")

for filename in os.listdir(source_folder):
    if filename.endswith('.csv'):
        print(f"Processing: {filename}...")
        file_path = os.path.join(source_folder, filename)
        
        try:
            # Read with pipe separator and handle mixed types
            df = pd.read_csv(file_path, sep='|', encoding='latin1', low_memory=False)
            
            # Apply cleaning
            df_cleaned = df.map(clean_data)
            
            # SAVE FIX: Explicitly set sep to pipe and encoding to utf-8
            output_path = os.path.join(output_folder, filename)
            df_cleaned.to_csv(output_path, sep='|', index=False, encoding='utf-8')
            
        except Exception as e:
            print(f"Error on {filename}: {e}")

print(f"\nDone! Cleaned files (Pipes preserved) are in: {output_folder}")