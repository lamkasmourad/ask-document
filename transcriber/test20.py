import json

# Load the contents of the two files
with open('output3.json', 'r') as file:
    data3 = json.load(file)

with open('output4.json', 'r') as file:
    data4 = json.load(file)

# Combine the chunks from both files
combined_chunks = data3['chunks'] + data4['chunks']

# Sort the combined chunks by the starting timestamp
sorted_chunks = sorted(combined_chunks, key=lambda x: x['timestamp'][0])

# Create the final JSON structure
output123 = {'chunks': sorted_chunks}

# Write the combined data to output123.json
with open('output123.json', 'w') as file:
    json.dump(output123, file, indent=4)