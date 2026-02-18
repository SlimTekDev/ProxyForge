import csv
import re
import os

source_folder = r'C:\Users\slimm\Desktop\WahapediaExport\Source Files'
output_folder = os.path.join(source_folder, 'Cleaned_CSVs')

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

def clean_text(text):
    if not text: return ""
    text = re.sub(r'<[^>]+>', '', text)
    return text.encode('ascii', 'ignore').decode('ascii')

print(f"Starting batch clean in: {source_folder}")

for filename in os.listdir(source_folder):
    if filename.endswith('.csv'):
        print(f"Processing: {filename}...")
        input_path = os.path.join(source_folder, filename)
        output_path = os.path.join(output_folder, filename)
        
        try:
            with open(input_path, 'r', encoding='latin1') as infile:
                reader = list(csv.reader(infile))
                if len(reader) < 1: continue
                
                header = reader[0]
                expected_count = len(header)
                cleaned_rows = []
                
                for row in reader:
                    # Clean every cell
                    row = [clean_text(cell) for cell in row]
                    
                    # Merge extra columns back into the last column
                    if len(row) > expected_count:
                        fixed_row = row[:expected_count-1]
                        overflow = " ".join(row[expected_count-1:])
                        fixed_row.append(overflow)
                        row = fixed_row
                    # Pad short rows
                    elif len(row) < expected_count:
                        row.extend([""] * (expected_count - len(row)))
                    cleaned_rows.append(row)

            with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
                writer = csv.writer(outfile)
                writer.writerows(cleaned_rows)
        except Exception as e:
            print(f"Error processing {filename}: {e}")

print(f"\nDone! Cleaned files are in: {output_folder}")