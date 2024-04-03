from helper import StereoToMonoConverter
import os
import json
import subprocess
import asyncio
import aiofiles

class AudioHandler:

    async def process_channel(self, audio_file, actor):
        # Run the transcription process
        command = ["insanely-fast-whisper", "--file-name", audio_file, "--device-id", "mps", "--language", "fr"]
        await asyncio.create_subprocess_exec(*command)
        # Read the output JSON
        async with aiofiles.open('output.json', 'r') as file:
            data = json.loads(await file.read())

        # Add the 'actor' field to each chunk
        for chunk in data['chunks']:
            chunk['actor'] = actor

        return data['chunks']

    async def get_transcription(self, audio_path):
        # Extract the extension from the audio_path
        _, audio_extension = os.path.splitext(audio_path)
        
        # Ensure the extension starts with a dot
        if not audio_extension.startswith('.'):
            audio_extension = '.' + audio_extension

        channelSplitter = StereoToMonoConverter(audio_path)
        left_channel_filename = "left_channel" + audio_extension
        right_channel_filename = "right_channel" + audio_extension
        await channelSplitter.export_channels(left_channel_filename, right_channel_filename)

        left_chunks, right_chunks = await asyncio.gather(
            self.process_channel(left_channel_filename, 'agent'),
            self.process_channel(right_channel_filename, 'client')
        )

        # Merge and sort the chunks
        merged_chunks = left_chunks + right_chunks
        sorted_chunks = sorted(merged_chunks, key=lambda x: x['timestamp'][0])

        # Create and output the final JSON object
        final_json = {'conversation': sorted_chunks}
        print(json.dumps(final_json, indent=4))

# Example usage
audio_handler = AudioHandler()
asyncio.run(audio_handler.get_transcription("stereo.wav"))