"""Text-to-Speech service providers."""

from .base import TTSProvider, TTSConfig
from .elevenlabs_provider import ElevenLabsProvider
from .google_provider import GoogleTTSProvider
from .openai_provider import OpenAITTSProvider
from .amazon_provider import AmazonPollyProvider

__all__ = [
    'TTSProvider',
    'TTSConfig',
    'ElevenLabsProvider',
    'GoogleTTSProvider', 
    'OpenAITTSProvider',
    'AmazonPollyProvider',
]