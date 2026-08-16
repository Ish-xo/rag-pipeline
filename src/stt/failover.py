import logging
from .base import BaseSTTClient
from .sarvam_client import SarvamSTTClient
from .elevenlabs_client import ElevenLabsSTTClient

logger = logging.getLogger(__name__)

class FailoverSTTClient(BaseSTTClient):
    def __init__(self):
        self.primary = SarvamSTTClient()
        self.backup = ElevenLabsSTTClient()
        
    async def transcribe(self, audio_bytes: bytes, **kwargs) -> str:
        try:
            logger.info("Attempting STT with primary (Sarvam)...")
            return await self.primary.transcribe(audio_bytes, **kwargs)
        except Exception as e:
            logger.warning(f"Primary STT (Sarvam) failed: {e}. Falling back to ElevenLabs...")
            try:
                return await self.backup.transcribe(audio_bytes, **kwargs)
            except Exception as backup_e:
                logger.error(f"Backup STT (ElevenLabs) also failed: {backup_e}")
                raise Exception("Both primary and backup STT clients failed.")
