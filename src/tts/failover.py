import logging
from .base import BaseTTSClient
from .edge_tts_client import EdgeTTSClient
from .sarvam_tts_client import SarvamTTSClient
from .elevenlabs_client import ElevenLabsTTSClient

logger = logging.getLogger(__name__)

class FailoverTTSClient(BaseTTSClient):
    def __init__(self):
        self.primary = EdgeTTSClient()
        self.backup = SarvamTTSClient()
        self.tertiary = ElevenLabsTTSClient()
        
    async def synthesize(self, text: str, output_path: str = None, **kwargs) -> bytes:
        try:
            logger.info("Attempting TTS with primary (Edge-TTS)...")
            return await self.primary.synthesize(text, output_path, **kwargs)
        except Exception as e:
            logger.warning(f"Primary TTS (Edge-TTS) failed: {e}. Falling back to Sarvam...")
            try:
                return await self.backup.synthesize(text, output_path, **kwargs)
            except Exception as backup_e:
                logger.warning(f"Backup TTS (Sarvam) failed: {backup_e}. Falling back to ElevenLabs...")
                try:
                    return await self.tertiary.synthesize(text, output_path, **kwargs)
                except Exception as tertiary_e:
                    logger.error(f"All TTS clients failed. Last error: {tertiary_e}")
                    raise Exception("All TTS clients failed.")
