import csv
import re
import os

source_folder = r'C:\Users\slimm\Desktop\WahapediaExport\Source Files'
output_folder = os.path.join(source_folder, 'Cleaned_CSVs')

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

def clean_text(text):
    if not text: return ""
    # Strip HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove non-ASCII/Problematic characters
    return text.encode('ascii', 'ignore').decode('ascii')

print(f"Starting batch clean in: {source_folder}")

for filename in os.listdir(source_folder):
    if filename.endswith('.csv'):
        print(f"Processing: {filename}...")
        
        input_path = os.path.join(source_folder, filename)
        output_path = os.path.join(output_folder, filename)
        
        with open(input_path, 'r', encoding='latin1') as infile:
            reader = list(csv.reader(infile))
            if not reader:
                continue
            
            # Determine expected column count from the header
            header = reader[0]
            expected_count = len(header)
            
            cleaned_rows = []
            for i, row in enumerate(reader):
                # Clean every cell in the row
                row = [clean_text(cell) for cell in row]
                
                # Fix rows with too many commas
                if len(row) > expected_count:
                    # Keep the first (expected_count - 1) columns as they are
                    # Merge all remaining columns into the last one
                    fixed_row = row[:expected_count-1]
                    overflow = " ".join(row[expected_count-1:])
                    fixed_row.append(overflow)
                    row = fixed_row
                
                # Fill rows with too few columns (prevents MySQL mapping errors)
                elif len(row) < expected_count:
                    row.extend([""] * (expected_count - len(row)))
                
                cleaned_rows.append(row)

        with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
            writer = csv.writer(outfile)
            writer.writerows(cleaned_rows)

print(f"\nDone! All rows preserved. Files located in: {output_folder}")