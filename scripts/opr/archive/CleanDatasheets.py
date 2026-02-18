import pandas as pd
import re

# Load file with latin1 to avoid initial encoding crashes
df = pd.read_csv(r'C:\Users\slimm\Desktop\WahapediaExport\Datasheets.csv', encoding='latin1')

def clean_data(text):
    if not isinstance(text, str): return text
    # Strip HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove non-ASCII/Problematic characters
    return text.encode('ascii', 'ignore').decode('ascii')

# USE .map() instead of .applymap()
df_cleaned = df.map(clean_data)

# Save as clean UTF-8
df_cleaned.to_csv(r'C:\Users\slimm\Desktop\WahapediaExport\Datasheets_Clean.csv', index=False, encoding='utf-8')
print("Cleaned file created successfully!")