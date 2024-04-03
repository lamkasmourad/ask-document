import json
from itertools import groupby

# Load the JSON data from the file
with open('output2.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Function to remove duplicates
def remove_duplicates(chunks):
    seen = set()
    new_chunks = []
    for chunk in chunks:
        # Convert the list to a tuple for the 'timestamp' key
        chunk['timestamp'] = tuple(chunk['timestamp'])
        chunk_tuple = tuple(chunk.items())
        if chunk_tuple not in seen:
            seen.add(chunk_tuple)
            chunk['timestamp'] = list(chunk['timestamp'])
            new_chunks.append(chunk)
    return new_chunks

# Remove duplicates from the 'chunks' array
data['chunks'] = remove_duplicates(data['chunks'])

# Add actor and sort by the first timestamp
for chunk in data['chunks']:
    chunk['actor'] = 'agent'
data['chunks'].sort(key=lambda x: x['timestamp'][0])

# Function to concatenate text to form sentences based on timestamp and actor
def concatenate_sentences(chunks):
    sentences = []
    current_sentence = ''
    current_actor = None
    current_end_time = None

    for key, group in groupby(chunks, lambda x: x['actor']):
        for item in group:
            if current_actor is None or current_actor != item['actor'] or item['timestamp'][0] > current_end_time:
                if current_sentence:
                    sentences.append({'actor': current_actor, 'text': current_sentence.strip()})
                current_sentence = item['text']
                current_actor = item['actor']
                current_end_time = item['timestamp'][1]
            else:
                current_sentence += ' ' + item['text']
                current_end_time = max(current_end_time, item['timestamp'][1])

    # Add the last sentence if it exists
    if current_sentence:
        sentences.append({'actor': current_actor, 'text': current_sentence.strip()})

    return sentences

# Concatenate the text to form sentences
conversation = concatenate_sentences(data['chunks'])

# Save the result to output6.json
with open('output6.json', 'w', encoding='utf-8') as file:
    json.dump(conversation, file, ensure_ascii=False, indent=4)