"""Language configuration manager for dynamic language support."""

from typing import List, Tuple, Optional
from src.config import get_config
from src.local.localization import LANGUAGE_FLAGS


class LanguageConfigManager:
    """Manages language configuration based on .env settings."""

    def __init__(self):
        self.config = get_config()

        # Language display names mapping
        self.language_display_names = {
            "english": "English",
            "spanish": "Español",
            "french": "Français",
            "german": "Deutsch",
            "italian": "Italiano",
            "portuguese": "Português",
            "russian": "Русский",
            "polish": "Polski",
            "chinese": "中文",
            "japanese": "日本語",
            "korean": "한국어",
            "arabic": "العربية",
            "hindi": "हिन्दी",
        }

    def validate_interface_language(self, lang: str) -> bool:
        """Check if a language is supported for interface."""
        return lang.lower() in self.config.supported_interface_languages

    def validate_learning_language(self, lang: str) -> bool:
        """Check if a language is supported for learning."""
        return lang.lower() in self.config.supported_learning_languages

    def get_interface_keyboard(self) -> List[Tuple[str, str]]:
        """Get interface language selection buttons with flag emojis."""
        keyboard = []
        for lang_code in self.config.supported_interface_languages:
            flag = LANGUAGE_FLAGS.get(lang_code, "🌍")
            display_name = self.language_display_names.get(lang_code, lang_code.title())
            keyboard.append((f"{flag} {display_name}", lang_code))
        return keyboard

    def get_learning_keyboard(self, exclude_native: Optional[str] = None) -> List[Tuple[str, str]]:
        """Get learning language selection buttons with flag emojis, optionally excluding native language."""
        keyboard = []
        for lang_code in self.config.supported_learning_languages:
            # Skip the native language if specified
            if exclude_native and lang_code.lower() == exclude_native.lower():
                continue

            flag = LANGUAGE_FLAGS.get(lang_code, "🌍")
            display_name = self.language_display_names.get(lang_code, lang_code.title())
            keyboard.append((f"{flag} {display_name}", lang_code))
        return keyboard

    def get_all_learning_languages(self) -> List[str]:
        """Get list of all supported learning languages."""
        return self.config.supported_learning_languages.copy()

    def get_all_interface_languages(self) -> List[str]:
        """Get list of all supported interface languages."""
        return self.config.supported_interface_languages.copy()

    def is_language_combination_valid(self, native: str, learning: str) -> bool:
        """Check if a combination of native and learning languages is valid."""
        return self.validate_interface_language(native) and self.validate_learning_language(learning) and native.lower() != learning.lower()

    def get_fallback_native_language(self) -> str:
        """Get a fallback native language if user's stored language is invalid."""
        # Return the first available interface language
        interface_languages = self.get_all_interface_languages()
        return interface_languages[0] if interface_languages else "english"

    def get_fallback_learning_language(self, exclude_native: str = None) -> str:
        """Get a fallback learning language if user's stored language is invalid."""
        available_languages = self.get_all_learning_languages()

        # Find first learning language that's not the native language
        if exclude_native:
            for lang in available_languages:
                if lang.lower() != exclude_native.lower():
                    return lang

        # Return first available learning language
        return available_languages[0] if available_languages else "english"


# Global language configuration manager instance
language_config = LanguageConfigManager()
