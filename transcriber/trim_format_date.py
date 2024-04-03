import json
import math

# Read the JSON file
with open('output123_merged.json', 'r') as file:
    data = json.load(file)

# Assuming 'data' is a dictionary with a 'chunks' key that contains the entries
entries = data['chunks']

# Modify the data
for entry in entries:
    entry['text'] = entry['text'].strip()  # Trim the text
    # Adjust start timestamp to the nearest second
    entry['start'] = int(math.floor(entry['timestamp'][0])) if entry['timestamp'][0] % 1 < 0.5 else int(math.ceil(entry['timestamp'][0]))
    # Adjust end timestamp to the nearest second
    entry['end'] = int(math.floor(entry['timestamp'][1])) if entry['timestamp'][1] % 1 < 0.5 else int(math.ceil(entry['timestamp'][1]))
    # Remove the 'timestamp' field
    del entry['timestamp']

# Write the modified data back to the file
with open('result.json', 'w') as file:
    json.dump(data, file, ensure_ascii=False,indent=4)