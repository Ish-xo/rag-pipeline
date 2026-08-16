import os
import aiohttp
from .base import BaseSTTClient

class SarvamSTTClient(BaseSTTClient):
    def __init__(self):
        self.api_key = os.getenv("SARVAM_API_KEY")
        self.url = "https://api.sarvam.ai/speech-to-text-translate"

    async def transcribe(self, audio_bytes: bytes, **kwargs) -> str:
        if not self.api_key:
            raise ValueError("SARVAM_API_KEY is not set.")
            
        async with aiohttp.ClientSession() as session:
            data = aiohttp.FormData()
            data.add_field('file', audio_bytes, filename='audio.wav', content_type='audio/wav')
            
            # Additional params for saaras:v3
            model = kwargs.get("model", "saaras:v3")
            data.add_field('model', model)
            
            # Optional parameters
            if "prompt" in kwargs:
                data.add_field('prompt', kwargs['prompt'])
            if "language_code" in kwargs:
                data.add_field('language_code', kwargs['language_code'])
            
            headers = {
                "api-subscription-key": self.api_key
            }
            
            try:
                async with session.post(self.url, data=data, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("transcript", "")
                    else:
                        error_msg = await response.text()
                        raise Exception(f"Sarvam API Error {response.status}: {error_msg}")
            except Exception as e:
                raise Exception(f"Sarvam STT failed: {str(e)}")
