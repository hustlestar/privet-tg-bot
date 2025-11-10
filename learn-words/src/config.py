"""Configuration settings for the Learn Words bot."""

import os
from dataclasses import dataclass
from typing import List, Optional

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class Config:
    """Application configuration."""

    # Required fields (no defaults)
    telegram_token: str
    database_url: str

    # Optional fields (with defaults)
    default_notification_time: str = "16:00"
    openrouter_api_key: str = "mock"
    openrouter_model: str = "openai/gpt-3.5-turbo"
    max_training_words_per_session: int = 10
    default_response_mode: str = "medium"

    inactivity_notification_days: int = 10
    inactivity_notification_time: str = "12:00"
    repetition_notification_interval_minutes: int = 30
    cleanup_old_notifications_interval_hours: int = 24

    # Language configuration
    supported_interface_languages: List[str] = None
    supported_learning_languages: List[str] = None

    @classmethod
    def from_env(cls) -> "Config":
        """Create config from environment variables."""
        telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        database_url = os.getenv("DATABASE_URL")

        if not telegram_token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
        if not database_url:
            raise ValueError("DATABASE_URL environment variable is required")

        # Parse language lists from environment
        interface_langs = os.getenv("SUPPORTED_INTERFACE_LANGUAGES", "english,spanish,russian,polish")
        learning_langs = os.getenv(
            "SUPPORTED_LEARNING_LANGUAGES",
            "english,spanish,french,german,italian,portuguese,russian,polish",
        )

        return cls(
            telegram_token=telegram_token,
            database_url=database_url,
            openrouter_api_key=os.getenv("OPENROUTER_API_KEY", "mock"),
            openrouter_model=os.getenv("OPENROUTER_MODEL", "openai/gpt-3.5-turbo"),
            max_training_words_per_session=int(os.getenv("MAX_TRAINING_WORDS", "10")),
            default_response_mode=os.getenv("DEFAULT_RESPONSE_MODE", "medium"),
            inactivity_notification_days=int(os.getenv("INACTIVITY_NOTIFICATION_DAYS", "10")),
            inactivity_notification_time=os.getenv("INACTIVITY_NOTIFICATION_TIME", "12:00"),
            repetition_notification_interval_minutes=int(os.getenv("REPETITION_NOTIFICATION_INTERVAL_MINUTES", 30)),
            cleanup_old_notifications_interval_hours=int(os.getenv("CLEANUP_OLD_NOTIFICATIONS_INTERVAL_HOURS", 24)),
            supported_interface_languages=[lang.strip() for lang in interface_langs.split(",")],
            supported_learning_languages=[lang.strip() for lang in learning_langs.split(",")],
        )


# Global config instance - initialized lazily to avoid import issues
config = None


def get_config() -> Config:
    """Get the global config instance, creating it if necessary."""
    global config
    if config is None:
        config = Config.from_env()
    return config
