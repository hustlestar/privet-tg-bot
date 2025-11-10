"""Service for handling audio processing, including STT and TTS."""

import logging
from typing import Optional

from openai import AsyncOpenAI

from telegram_bot_template.config.settings import BotConfig
from telegram_bot_template.services.tts.factory import TTSFactory
from telegram_bot_template.services.tts.base import BaseTTSProvider

logger = logging.getLogger(__name__)


class AudioService:
    """Manages Speech-to-Text and Text-to-Speech operations."""

    def __init__(self, config: BotConfig):
        """
        Initializes the AudioService with API clients.

        Args:
            config: The bot's configuration object.
        """
        self.config = config
        self.openai_client: Optional[AsyncOpenAI] = None
        self.tts_provider: Optional[BaseTTSProvider] = None

        # Initialize STT (Speech-to-Text)
        if config.openai_api_key:
            self.openai_client = AsyncOpenAI(api_key=config.openai_api_key)
            logger.info("OpenAI client initialized for STT.")

        # Initialize TTS (Text-to-Speech) with selected provider
        try:
            # Determine API key based on provider
            api_key = None
            if config.tts_provider == "elevenlabs":
                api_key = config.elevenlabs_api_key
            elif config.tts_provider == "openai":
                api_key = config.openai_api_key
            elif config.tts_provider == "google":
                api_key = config.google_tts_api_key
            elif config.tts_provider == "amazon":
                api_key = config.amazon_polly_api_key
            
            if api_key or config.tts_provider == "openai":  # OpenAI can use env var
                self.tts_provider = TTSFactory.from_env(
                    provider_name=config.tts_provider,
                    api_key=api_key,
                    voice_id=config.tts_voice,
                    language=config.tts_language,
                    model=config.tts_model,
                )
                logger.info(f"TTS provider '{config.tts_provider}' initialized.")
            else:
                logger.warning(f"No API key configured for TTS provider '{config.tts_provider}'")
        except Exception as e:
            logger.error(f"Failed to initialize TTS provider: {e}")
            self.tts_provider = None

    async def transcribe_voice(self, voice_file_path: str) -> Optional[str]:
        """
        Transcribes an audio file using OpenAI's Whisper model.

        Args:
            voice_file_path: The path to the audio file to transcribe.

        Returns:
            The transcribed text, or None if an error occurs.
        """
        if not self.openai_client:
            logger.warning("OpenAI client not available for transcription.")
            return None

        try:
            with open(voice_file_path, "rb") as audio_file:
                transcription = await self.openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                )
            logger.info("Successfully transcribed audio.")
            return transcription.text
        except Exception as e:
            logger.error(f"Error during audio transcription: {e}", exc_info=True)
            return None

    async def text_to_speech(
        self, 
        text: str,
        emotion: Optional[str] = None,
        intensity: Optional[float] = None,
        voice: Optional[str] = None,
    ) -> Optional[bytes]:
        """
        Converts text to speech using the configured TTS provider.

        Args:
            text: The text to synthesize.
            emotion: Optional emotion/tone (e.g., "cheerful", "calm", "excited")
            intensity: Optional intensity level (0.0 to 1.0)
            voice: Optional voice override

        Returns:
            The audio data as bytes, or None if an error occurs.
        """
        if not self.tts_provider:
            logger.warning("TTS provider not available.")
            return None

        try:
            # Use the abstract TTS provider
            audio_bytes = await self.tts_provider.synthesize(
                text=text,
                voice=voice,
                emotion=emotion,
                intensity=intensity,
            )
            
            if audio_bytes:
                logger.info(f"Successfully generated audio with {self.config.tts_provider} provider")
            return audio_bytes
        except Exception as e:
            logger.error(f"Error during text-to-speech generation: {e}", exc_info=True)
            return None
    
    async def list_available_voices(self) -> dict:
        """List available voices from the current TTS provider.
        
        Returns:
            Dictionary of available voices
        """
        if not self.tts_provider:
            return {"error": "No TTS provider configured"}
        
        try:
            return await self.tts_provider.list_voices()
        except Exception as e:
            logger.error(f"Error listing voices: {e}")
            return {"error": str(e)}
    
    def get_tts_provider_info(self) -> dict:
        """Get information about the current TTS provider.
        
        Returns:
            Dictionary with provider information
        """
        if not self.tts_provider:
            return {
                "provider": "none",
                "configured": False,
            }
        
        return {
            "provider": self.config.tts_provider,
            "configured": True,
            "voice": self.config.tts_voice,
            "language": self.config.tts_language,
            "model": self.config.tts_model,
            "supported_languages": self.tts_provider.get_supported_languages(),
        }
