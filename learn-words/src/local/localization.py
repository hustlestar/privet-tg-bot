"""Enhanced localization system for the Learn Words bot."""

from typing import List, Tuple

from src.local.lang.english import ENGLISH_LOCALIZED_DATA
from src.local.lang.polish import POLISH_LOCALIZED_DATA
from src.local.lang.russian import RUSSIAN_LOCALIZED_DATA
from src.local.lang.spanish import SPANISH_LOCALIZED_DATA

# Language to flag emoji mapping
LANGUAGE_FLAGS = {
    "english": "🇺🇸",
    "spanish": "🇪🇸",
    "french": "🇫🇷",
    "german": "🇩🇪",
    "italian": "🇮🇹",
    "portuguese": "🇵🇹",
    "russian": "🇷🇺",
    "polish": "🇵🇱",
    "chinese": "🇨🇳",
    "japanese": "🇯🇵",
    "korean": "🇰🇷",
    "arabic": "🇸🇦",
    "hindi": "🇮🇳",
}

# Enhanced localized text for the bot interface
LOCALIZED_TEXT = {
    "english": ENGLISH_LOCALIZED_DATA,
    "spanish": SPANISH_LOCALIZED_DATA,
    "russian": RUSSIAN_LOCALIZED_DATA,
    "polish": POLISH_LOCALIZED_DATA,
}

# Dictionary for remapping English database values to interface language translations
ENGLISH_VALUE_TRANSLATIONS = {
    # Language names
    "english": {
        "english": "English",
        "spanish": "Inglés",
        "russian": "Английский",
        "polish": "Angielski",
    },
    "spanish": {
        "english": "Spanish",
        "spanish": "Español",
        "russian": "Испанский",
        "polish": "Hiszpański",
    },
    "russian": {
        "english": "Russian",
        "spanish": "Ruso",
        "russian": "Русский",
        "polish": "Rosyjski",
    },
    "polish": {
        "english": "Polish",
        "spanish": "Polaco",
        "russian": "Польский",
        "polish": "Polski",
    },
    "french": {
        "english": "French",
        "spanish": "Francés",
        "russian": "Французский",
        "polish": "Francuski",
    },
    "german": {
        "english": "German",
        "spanish": "Alemán",
        "russian": "Немецкий",
        "polish": "Niemiecki",
    },
    # Response modes
    "short": {
        "english": "Short",
        "spanish": "Corto",
        "russian": "Короткий",
        "polish": "Krótki",
    },
    "medium": {
        "english": "Medium",
        "spanish": "Medio",
        "russian": "Средний",
        "polish": "Średni",
    },
    "long": {
        "english": "Long",
        "spanish": "Largo",
        "russian": "Длинный",
        "polish": "Długi",
    },
    # Explanation language modes
    "native": {
        "english": "Native Language",
        "spanish": "Idioma Nativo",
        "russian": "Родной язык",
        "polish": "Język ojczysty",
    },
    "learning": {
        "english": "Learning Language",
        "spanish": "Idioma de Aprendizaje",
        "russian": "Изучаемый язык",
        "polish": "Język nauki",
    },
    "mixed": {
        "english": "Mixed Mode",
        "spanish": "Modo Mixto",
        "russian": "Смешанный режим",
        "polish": "Tryb mieszany",
    },
}


def get_translated_value(english_value: str, interface_language: str) -> str:
    """
    Get translated value for interface display.

    Args:
        english_value: The English value stored in database (lowercase)
        interface_language: The user's interface language code

    Returns:
        The translated value for the interface language, or the original value if not found
    """
    if not english_value or not interface_language:
        return english_value or ""

    english_value_lower = english_value.lower()

    if english_value_lower in ENGLISH_VALUE_TRANSLATIONS:
        translations = ENGLISH_VALUE_TRANSLATIONS[english_value_lower]
        return translations.get(interface_language, english_value)

    return english_value


def get_all_translations(english_value: str) -> dict:
    """
    Get all available translations for an English value.

    Args:
        english_value: The English value stored in database (lowercase)

    Returns:
        Dictionary mapping interface language codes to translations
    """
    english_value_lower = english_value.lower()
    return ENGLISH_VALUE_TRANSLATIONS.get(english_value_lower, {})


class LocalizationManager:
    """Manages localized text for the bot interface."""

    @staticmethod
    def get_text(language: str, key: str, default: str = None, **kwargs) -> str:
        """Get localized text for a specific language and key with formatting."""
        if language in LOCALIZED_TEXT and key in LOCALIZED_TEXT[language]:
            text = LOCALIZED_TEXT[language][key]
        elif key in LOCALIZED_TEXT["english"]:
            text = LOCALIZED_TEXT["english"][key]
        else:
            text = default or key

        # Format with provided kwargs
        if kwargs:
            try:
                return text.format(**kwargs)
            except (KeyError, ValueError):
                return text
        return text

    @staticmethod
    def get_language_buttons() -> List[Tuple[str, str]]:
        """Get language selection buttons with flag emojis."""
        return [
            (f"{LANGUAGE_FLAGS['english']} English", "english"),
            (f"{LANGUAGE_FLAGS['spanish']} Español", "spanish"),
            (f"{LANGUAGE_FLAGS['french']} Français", "french"),
            (f"{LANGUAGE_FLAGS['german']} Deutsch", "german"),
            # (f"{LANGUAGE_FLAGS['italian']} Italiano", "italian"),
            # (f"{LANGUAGE_FLAGS['portuguese']} Português", "portuguese"),
            (f"{LANGUAGE_FLAGS['russian']} Русский", "russian"),
            (f"{LANGUAGE_FLAGS['polish']} Polski", "polish"),
            # (f"{LANGUAGE_FLAGS['chinese']} 中文", "chinese"),
            # (f"{LANGUAGE_FLAGS['japanese']} 日本語", "japanese"),
            # (f"{LANGUAGE_FLAGS['korean']} 한국어", "korean"),
            # (f"{LANGUAGE_FLAGS['arabic']} العربية", "arabic"),
            # (f"{LANGUAGE_FLAGS['hindi']} हिन्दी", "hindi")
        ]

    @staticmethod
    def get_learning_language_options(native_language: str) -> List[Tuple[str, str]]:
        """Get learning language options excluding the native language."""
        all_languages = LocalizationManager.get_language_buttons()

        # Filter out the native language
        return [(display, code) for display, code in all_languages if not display.endswith(native_language)]

    @staticmethod
    def create_multilingual_welcome() -> str:
        """Create welcome message in multiple languages."""
        return (
            f"🌍 <u><b>Welcome to Learn Words!</b></u> {LANGUAGE_FLAGS['english']}"
            f"\n¡Bienvenido! {LANGUAGE_FLAGS['spanish']}"
            f"\nBienvenue! {LANGUAGE_FLAGS['french']}"
            f"\nWillkommen! {LANGUAGE_FLAGS['german']}"
            f"\nДобро пожаловать! {LANGUAGE_FLAGS['russian']}"
            f"\nWitamy! {LANGUAGE_FLAGS['polish']}\n\n"
            f"<b>Please select your native language:</b> {LANGUAGE_FLAGS['english']}\n"
            f"Por favor, selecciona tu idioma nativo: {LANGUAGE_FLAGS['spanish']}\n"
            f"Veuillez sélectionner votre langue maternelle: {LANGUAGE_FLAGS['french']}\n"
            f"Bitte wählen Sie Ihre Muttersprache: {LANGUAGE_FLAGS['german']}\n"
            f"Пожалуйста, выберите ваш родной язык: {LANGUAGE_FLAGS['russian']}\n"
            f"Proszę wybierz swój język ojczysty: {LANGUAGE_FLAGS['polish']}"
        )

    @staticmethod
    def get_flag_for_language(language: str) -> str:
        """Get flag emoji for a language."""
        return LANGUAGE_FLAGS.get(language, "🌍")

    @staticmethod
    def get_translated_value(english_value: str, interface_language: str) -> str:
        """
        Get translated value for interface display using the remapping dictionary.

        Args:
            english_value: The English value stored in database (lowercase)
            interface_language: The user's interface language code

        Returns:
            The translated value for the interface language
        """
        return get_translated_value(english_value, interface_language)

    @staticmethod
    def get_all_value_translations(english_value: str) -> dict:
        """
        Get all available translations for an English value.

        Args:
            english_value: The English value stored in database (lowercase)

        Returns:
            Dictionary mapping interface language codes to translations
        """
        return get_all_translations(english_value)


# Global localization manager instance
localization = LocalizationManager()
