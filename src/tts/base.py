from abc import ABC, abstractmethod

class BaseTTSClient(ABC):
    @abstractmethod
    async def synthesize(self, text: str, output_path: str = None, **kwargs) -> bytes:
        """Synthesize text to audio bytes."""
        pass
