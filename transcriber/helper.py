from pydub import AudioSegment
import os 
import asyncio
from concurrent.futures import ThreadPoolExecutor

from functools import partial

class StereoToMonoConverter:
    def __init__(self, file_path):
        self.file_path = file_path
        self.audio = AudioSegment.from_file(self.file_path)

    def split_stereo_to_mono(self):
        left_channel, right_channel = self.audio.split_to_mono()
        return left_channel, right_channel

    async def export_channels(self, left_channel_path, right_channel_path):
        loop = asyncio.get_event_loop()
        left_channel, right_channel = self.split_stereo_to_mono()
        _, left_ext = os.path.splitext(left_channel_path)
        format = left_ext[1:]
        await loop.run_in_executor(None, partial(left_channel.export, left_channel_path, format=format))
        await loop.run_in_executor(None, partial(right_channel.export, right_channel_path, format=format))