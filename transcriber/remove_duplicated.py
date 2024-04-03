import json

# Load the JSON data from the file
with open('output123.json', 'r') as file:
    data = json.load(file)

# Initialize a new list to store the merged chunks
merged_chunks = []

# Iterate through the chunks in the data
for chunk in data['chunks']:
    # If the merged_chunks list is not empty and the actor of the current chunk is the same as the last one in the merged list
    if merged_chunks and chunk['actor'] == merged_chunks[-1]['actor']:
        # Append the text of the current chunk to the last one in the merged list
        merged_chunks[-1]['text'] += ' ' + chunk['text'].strip()
        # Update the end timestamp of the last chunk in the merged list to the end timestamp of the current chunk
        merged_chunks[-1]['timestamp'][1] = chunk['timestamp'][1]
    else:
        # If the actor is different or the merged_chunks list is empty, append the chunk as a new entry in the merged list
        merged_chunks.append(chunk)

# Replace the original chunks with the merged chunks
data['chunks'] = merged_chunks

# Save the modified data back to the file
with open('output123_merged.json', 'w') as file:
    json.dump(data, file, indent=4,ensure_ascii=False)

# Print the merged JSON data
print(json.dumps(data, indent=4))