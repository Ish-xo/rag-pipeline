import edge_tts
from .base import BaseTTSClient

class EdgeTTSClient(BaseTTSClient):
    def __init__(self, voice="en-US-AriaNeural"): 
        self.voice = voice

    async def synthesize(self, text: str, output_path: str = None, **kwargs) -> bytes:
        voice = kwargs.get("voice", self.voice)
        communicate = edge_tts.Communicate(text, voice)
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
                
        if output_path:
            with open(output_path, "wb") as f:
                f.write(audio_data)
                
        return audio_data
