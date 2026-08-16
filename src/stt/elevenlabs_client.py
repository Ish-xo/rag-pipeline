import os
import aiohttp
from .base import BaseSTTClient

class ElevenLabsSTTClient(BaseSTTClient):
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.url = "https://api.elevenlabs.io/v1/speech-to-text"

    async def transcribe(self, audio_bytes: bytes, **kwargs) -> str:
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY is not set.")
            
        async with aiohttp.ClientSession() as session:
            data = aiohttp.FormData()
            data.add_field('file', audio_bytes, filename='audio.wav', content_type='audio/wav')
            data.add_field('model_id', kwargs.get('model_id', 'scribe_v1')) # or scribe_v2 based on availability
            
            headers = {
                "xi-api-key": self.api_key
            }
            
            try:
                async with session.post(self.url, data=data, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("text", "")
                    else:
                        error_msg = await response.text()
                        raise Exception(f"ElevenLabs STT Error {response.status}: {error_msg}")
            except Exception as e:
                raise Exception(f"ElevenLabs STT failed: {str(e)}")
