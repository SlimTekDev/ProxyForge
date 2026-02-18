import pandas as pd
import re
import os

# 1. Setup paths
source_folder = r'C:\Users\slimm\Desktop\WahapediaExport\Source Files'
output_folder = os.path.join(source_folder, 'Cleaned_CSVs')

# Create output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

def clean_data(text):
    if not isinstance(text, str): return text
    # Strip HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove non-ASCII/Problematic characters
    return text.encode('ascii', 'ignore').decode('ascii')

# 2. Process every CSV in the folder
print(f"Starting batch clean in: {source_folder}")

for filename in os.listdir(source_folder):
    if filename.endswith('.csv'):
        print(f"Processing: {filename}...")
        
        # Load file
        file_path = os.path.join(source_folder, filename)
        df = pd.read_csv(file_path, encoding='latin1')
        
        # Apply cleaning logic element-wise
        # .map() is used for pandas 2.1+; use .applymap() if on an older version
        df_cleaned = df.map(clean_data)
        
        # Save to the new subfolder as clean UTF-8
        output_path = os.path.join(output_folder, filename)
        df_cleaned.to_csv(output_path, index=False, encoding='utf-8')

print(f"\nDone! All cleaned files are in: {output_folder}")