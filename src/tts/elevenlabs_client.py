import os
import aiohttp
from .base import BaseTTSClient

class ElevenLabsTTSClient(BaseTTSClient):
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        
    async def synthesize(self, text: str, output_path: str = None, **kwargs) -> bytes:
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY is not set.")
            
        voice_id = kwargs.get("voice_id", "pNInz6obbfDQGcgMyIGb") # Default voice (Adam)
        model_id = kwargs.get("model_id", "eleven_multilingual_v2")
        
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "text": text,
            "model_id": model_id,
            "voice_settings": {
                "stability": kwargs.get("stability", 0.5),
                "similarity_boost": kwargs.get("similarity_boost", 0.75)
            }
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        audio_bytes = await response.read()
                        
                        if output_path:
                            with open(output_path, "wb") as f:
                                f.write(audio_bytes)
                                
                        return audio_bytes
                    else:
                        error_msg = await response.text()
                        raise Exception(f"ElevenLabs TTS Error {response.status}: {error_msg}")
            except Exception as e:
                raise Exception(f"ElevenLabs TTS failed: {str(e)}")
