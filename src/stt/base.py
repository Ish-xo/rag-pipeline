from abc import ABC, abstractmethod

class BaseSTTClient(ABC):
    @abstractmethod
    async def transcribe(self, audio_bytes: bytes, **kwargs) -> str:
        """Transcribe audio to text."""
        pass
