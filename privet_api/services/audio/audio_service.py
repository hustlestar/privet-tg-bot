"""Service for handling audio processing, including STT and TTS."""

import logging
from typing import Optional, Dict, Any
from pathlib import Path

from openai import AsyncOpenAI

from .tts_factory import TTSFactory
from .tts_base import BaseTTSProvider

logger = logging.getLogger(__name__)


class AudioService:
    """Manages Speech-to-Text and Text-to-Speech operations."""

    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        tts_provider: str = "openai",
        tts_api_key: Optional[str] = None,
        tts_voice: str = "nova",
        tts_language: str = "en",
        tts_model: Optional[str] = None,
    ):
        """
        Initializes the AudioService with API clients.

        Args:
            openai_api_key: OpenAI API key for STT
            tts_provider: TTS provider name (openai, elevenlabs, google, amazon)
            tts_api_key: API key for TTS provider
            tts_voice: Voice ID for TTS
            tts_language: Language for TTS
            tts_model: Model for TTS (provider-specific)
        """
        self.openai_client: Optional[AsyncOpenAI] = None
        self.tts_provider_instance: Optional[BaseTTSProvider] = None
        self.tts_provider_name = tts_provider
        self.tts_voice = tts_voice
        self.tts_language = tts_language
        self.tts_model = tts_model

        # Initialize STT (Speech-to-Text)
        if openai_api_key:
            self.openai_client = AsyncOpenAI(api_key=openai_api_key)
            logger.info("OpenAI client initialized for STT.")
        else:
            # Try to get from environment
            try:
                self.openai_client = AsyncOpenAI()
                logger.info("OpenAI client initialized from environment for STT.")
            except Exception as e:
                logger.warning(f"Could not initialize OpenAI client: {e}")

        # Initialize TTS (Text-to-Speech) with selected provider
        try:
            # Use OpenAI key for OpenAI TTS if not separately provided
            if tts_provider == "openai" and not tts_api_key:
                tts_api_key = openai_api_key
            
            if tts_api_key or tts_provider == "openai":  # OpenAI can use env var
                self.tts_provider_instance = TTSFactory.create_provider(
                    provider_name=tts_provider,
                    api_key=tts_api_key,
                    voice_id=tts_voice,
                    language=tts_language,
                    model=tts_model,
                )
                logger.info(f"TTS provider '{tts_provider}' initialized.")
            else:
                logger.warning(f"No API key configured for TTS provider '{tts_provider}'")
        except Exception as e:
            logger.error(f"Failed to initialize TTS provider: {e}")
            self.tts_provider_instance = None

    async def transcribe_voice(
        self, 
        voice_file: bytes,
        filename: str = "audio.ogg"
    ) -> Optional[str]:
        """
        Transcribes audio data using OpenAI's Whisper model.

        Args:
            voice_file: Audio file data as bytes
            filename: Name of the file for format detection

        Returns:
            The transcribed text, or None if an error occurs.
        """
        if not self.openai_client:
            logger.warning("OpenAI client not available for transcription.")
            return None

        try:
            # Create a file-like object from bytes
            transcription = await self.openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=(filename, voice_file),
            )
            logger.info("Successfully transcribed audio.")
            return transcription.text
        except Exception as e:
            logger.error(f"Error during audio transcription: {e}", exc_info=True)
            return None

    async def transcribe_voice_file(self, voice_file_path: str) -> Optional[str]:
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
        if not self.tts_provider_instance:
            logger.warning("TTS provider not available.")
            return None

        try:
            # Use the abstract TTS provider
            audio_bytes = await self.tts_provider_instance.synthesize(
                text=text,
                voice=voice,
                emotion=emotion,
                intensity=intensity,
            )
            
            if audio_bytes:
                logger.info(f"Successfully generated audio with {self.tts_provider_name} provider")
            return audio_bytes
        except Exception as e:
            logger.error(f"Error during text-to-speech generation: {e}", exc_info=True)
            return None
    
    async def list_available_voices(self) -> Dict[str, Any]:
        """List available voices from the current TTS provider.
        
        Returns:
            Dictionary of available voices
        """
        if not self.tts_provider_instance:
            return {"error": "No TTS provider configured"}
        
        try:
            return await self.tts_provider_instance.list_voices()
        except Exception as e:
            logger.error(f"Error listing voices: {e}")
            return {"error": str(e)}
    
    def get_tts_provider_info(self) -> Dict[str, Any]:
        """Get information about the current TTS provider.
        
        Returns:
            Dictionary with provider information
        """
        if not self.tts_provider_instance:
            return {
                "provider": "none",
                "configured": False,
            }
        
        return {
            "provider": self.tts_provider_name,
            "configured": True,
            "voice": self.tts_voice,
            "language": self.tts_language,
            "model": self.tts_model,
            "supported_languages": self.tts_provider_instance.get_supported_languages(),
        }

    async def process_voice_message(
        self,
        voice_data: bytes,
        filename: str = "voice.ogg",
        response_emotion: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Process a voice message: transcribe and prepare for response.
        
        Args:
            voice_data: Voice message data
            filename: Original filename
            response_emotion: Emotion for response TTS
            
        Returns:
            Dictionary with transcription and processing info
        """
        try:
            # Transcribe the voice message
            transcription = await self.transcribe_voice(voice_data, filename)
            
            if not transcription:
                return {
                    "success": False,
                    "error": "Failed to transcribe audio"
                }
            
            return {
                "success": True,
                "transcription": transcription,
                "filename": filename,
                "response_emotion": response_emotion,
                "tts_available": self.tts_provider_instance is not None
            }
            
        except Exception as e:
            logger.error(f"Error processing voice message: {e}")
            return {
                "success": False,
                "error": str(e)
            }