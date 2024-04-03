import json

# Define the input and output file names
input_file_name = 'output2.json'
output_file_name = 'output4.json'

# Load the JSON data from the input file
with open(input_file_name, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Function to remove duplicates and add actor
def remove_duplicates_and_add_actor(chunks):
    seen = set()
    new_chunks = []
    for chunk in chunks:
        # Convert the list to a tuple for the 'timestamp' key
        chunk['timestamp'] = tuple(chunk['timestamp'])
        # Create a tuple of the dictionary items to be able to add to a set
        chunk_tuple = tuple(chunk.items())
        if chunk_tuple not in seen:
            seen.add(chunk_tuple)
            # Convert the timestamp back to a list for JSON serialization
            chunk['timestamp'] = list(chunk['timestamp'])
            # Add the actor field to the chunk
            chunk['actor'] = 'agent'
            new_chunks.append(chunk)
    return new_chunks

# Remove duplicates from the 'chunks' array and add actor
data['chunks'] = remove_duplicates_and_add_actor(data['chunks'])

# Save the updated JSON data back to the output file
with open(output_file_name, 'w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=4)