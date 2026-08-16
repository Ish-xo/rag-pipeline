import os
import aiohttp
import base64
from .base import BaseTTSClient

class SarvamTTSClient(BaseTTSClient):
    def __init__(self):
        self.api_key = os.getenv("SARVAM_API_KEY")
        self.url = "https://api.sarvam.ai/text-to-speech"
        
    async def synthesize(self, text: str, output_path: str = None, **kwargs) -> bytes:
        if not self.api_key:
            raise ValueError("SARVAM_API_KEY is not set.")
            
        payload = {
            "inputs": [text],
            "target_language_code": kwargs.get("language_code", "hi-IN"),
            "speaker": kwargs.get("speaker", "meera"),
            "pitch": kwargs.get("pitch", 0),
            "pace": kwargs.get("pace", 1.0),
            "loudness": kwargs.get("loudness", 1.5),
            "speech_sample_rate": kwargs.get("speech_sample_rate", 24000), # typically 24000 for good quality
            "enable_preprocessing": True,
            "model": kwargs.get("model", "bulbul:v1") # or bulbul:v3 if available
        }
        
        headers = {
            "api-subscription-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(self.url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        audios = result.get("audios", [])
                        if not audios:
                            raise Exception("No audio returned from Sarvam TTS")
                        
                        audio_bytes = base64.b64decode(audios[0])
                        
                        if output_path:
                            with open(output_path, "wb") as f:
                                f.write(audio_bytes)
                                
                        return audio_bytes
                    else:
                        error_msg = await response.text()
                        raise Exception(f"Sarvam API Error {response.status}: {error_msg}")
            except Exception as e:
                raise Exception(f"Sarvam TTS failed: {str(e)}")
