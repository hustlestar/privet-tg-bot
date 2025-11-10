import logging
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple, Callable

import asyncpg

from src.dao.database_migration_manager import DatabaseMigrationManager
from .dao.data_loader_dao import DataLoaderDao
from .dao.notification_dao import NotificationDao
from .dao.training_dao import TrainingDao
from .dao.user_dao import UserDao
from .dao.word_dao import WordDao
from src.dao.models import (
    User,
    Word,
    UserWordStats,
    TrainingAttempt,
    ResponseMode,
    TranslationData,
    ExplanationLanguage,
)
from .utils import async_timer

logger = logging.getLogger(__name__)


class Database:
    """Database manager for the Learn Words bot."""

    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self.migration_manager = DatabaseMigrationManager()
        self.user_dao: Optional[UserDao] = None
        self.word_dao: Optional[WordDao] = None
        self.data_loader_dao: Optional[DataLoaderDao] = None
        self.training_dao: Optional[TrainingDao] = None
        self.notification_dao: Optional[NotificationDao] = None

    async def connect(self):
        self.pool = await self.migration_manager.connect()
        self.user_dao = UserDao(self.pool)
        self.word_dao = WordDao(self.pool)
        self.data_loader_dao = DataLoaderDao(self.pool)
        self.training_dao = TrainingDao(self.pool)
        self.notification_dao = NotificationDao(self.pool)

    async def close(self):
        """Close database connection pool."""
        if self.pool:
            await self.pool.close()

    async def create_user(self, user: User, callback: Optional[Callable[[], None]] = None) -> None:
        await self.user_dao.create_user(user, callback)

    async def get_user(self, user_id: int) -> Optional[User]:
        return await self.user_dao.get_user(user_id)

    async def get_user_word_stats(self, user_id: int, word_id: int) -> Optional[UserWordStats]:
        return await self.user_dao.get_user_word_stats(user_id, word_id)

    async def update_user(self, user: User) -> None:
        return await self.user_dao.update_user(user)

    async def update_user_response_mode(self, user_id: int, mode: ResponseMode) -> None:
        return await self.user_dao.update_user_response_mode(user_id, mode)

    async def update_user_explanation_language(self, user_id: int, explanation_language: ExplanationLanguage) -> None:
        return await self.user_dao.update_user_explanation_language(user_id, explanation_language)

    async def update_user_interface_language(self, user_id: int, interface_language: str) -> None:
        return await self.user_dao.update_user_interface_language(user_id, interface_language)

    async def update_user_learning_language(self, user_id: int, learning_language: str) -> None:
        return await self.user_dao.update_user_learning_language(user_id, learning_language)

    # Word operations
    async def get_word(
        self,
        word: str,
        from_lang: str,
        to_lang: str,
        native_language: Optional[str] = None,
    ) -> Optional[Word]:
        return await self.word_dao.get_word(word, from_lang, to_lang, native_language)

    async def save_word(self, translation_data: TranslationData) -> int:
        return await self.word_dao.save_word(translation_data)

    # User vocabulary operations
    async def add_word_to_user_vocabulary(self, user_id: int, word_id: int) -> None:
        return await self.word_dao.add_word_to_user_vocabulary(user_id, word_id)

    async def hide_word_for_user(self, user_id: int, word_id: int) -> bool:
        return await self.word_dao.hide_word_for_user(user_id, word_id)

    async def get_user_vocabulary_count(self, user_id: int) -> int:
        return await self.word_dao.get_user_vocabulary_count(user_id)

    async def get_user_vocabulary_with_stats(self, user_id: int, limit: int = 20, offset: int = 0, sort_recent: bool = True) -> List[Dict[str, Any]]:
        return await self.word_dao.get_user_vocabulary_with_stats(user_id, limit, offset, sort_recent)

    async def mark_word_as_known(
        self,
        user_id: int,
        word: str,
        from_lang: str,
        to_lang: str,
        native_language: Optional[str] = None,
    ) -> bool:
        return await self.word_dao.mark_word_as_known(user_id, word, from_lang, to_lang, native_language)

    async def mark_word_as_known_by_id(self, user_id: int, word_id: int) -> bool:
        return await self.word_dao.mark_word_as_known_by_id(user_id, word_id)

    # Training operations
    async def get_word_for_training(self, user_id: int) -> Optional[Tuple[Word, UserWordStats]]:
        return await self.training_dao.get_word_for_training(user_id)

    async def get_words_by_ids_for_user(self, user_id: int, word_ids: List[int]) -> List[Tuple[Word, UserWordStats]]:
        return await self.training_dao.get_words_by_ids_for_user(user_id, word_ids)

    async def get_word_by_id_for_user(self, user_id: int, word_id: int) -> Optional[Tuple[Word, UserWordStats]]:
        return await self.training_dao.get_word_by_id_for_user(user_id, word_id)

    async def get_random_translations_for_distractors(
        self, user_id: int, exclude_word_id: int, to_language: str, count: int = 3
    ) -> List[str]:
        return await self.training_dao.get_random_translations_for_distractors(
            user_id, exclude_word_id, to_language, count
        )

    async def get_random_words_for_synonym_distractors(
        self,
        user_id: int,
        exclude_word_id: int,
        from_language: str,
        learning_language: str,
        count: int = 3,
        exclude_words: Optional[List[str]] = None,
    ) -> List[Word]:
        return await self.training_dao.get_random_words_for_synonym_distractors(
            user_id,
            exclude_word_id,
            from_language,
            learning_language,
            count,
            exclude_words,
        )

    async def record_training_attempt(self, attempt: TrainingAttempt, is_review_session: bool = False) -> int:
        return await self.training_dao.record_training_attempt(attempt, is_review_session)

    async def update_training_attempt_to_correct(self, attempt_id: int, previous_repetition_level: int) -> bool:
        return await self.training_dao.update_training_attempt_to_correct(attempt_id, previous_repetition_level)

    async def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        return await self.user_dao.get_user_stats(user_id)

    # Word fetching operations for database population
    async def get_words_by_language(self, language: str) -> List[Dict[str, Any]]:
        return await self.data_loader_dao.get_words_by_language(language)

    async def get_words_by_languages(self, languages: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        return await self.data_loader_dao.get_words_by_languages(languages)

    async def get_language_word_counts(self) -> Dict[str, int]:
        return await self.data_loader_dao.get_language_word_counts()

    async def get_available_languages(self) -> List[str]:
        return await self.data_loader_dao.get_available_languages()

    async def get_database_word_statistics(self) -> Dict[str, Any]:
        return await self.data_loader_dao.get_database_word_statistics()

    async def get_due_words_for_user(self, user_id: int, exclude_word_ids: Optional[List[int]] = None) -> List[Dict[str, Any]]:
        return await self.notification_dao.get_due_words_for_user(user_id, exclude_word_ids)

    async def get_pending_notification_word_ids(self, user_id: int) -> List[int]:
        return await self.notification_dao.get_pending_notification_word_ids(user_id)

    async def get_todays_notification_count(self, user_id: int, notification_type: str) -> int:
        return await self.notification_dao.get_todays_notification_count(user_id, notification_type)

    async def create_due_word_notification(self, user_id: int, word_ids: List[int]) -> int:
        return await self.notification_dao.create_due_word_notification(user_id, word_ids)

    async def get_due_word_notification(self, notification_id: int) -> Optional[Dict[str, Any]]:
        return await self.notification_dao.get_due_word_notification(notification_id)

    async def delete_due_word_notification(self, notification_id: int) -> None:
        return await self.notification_dao.delete_due_word_notification(notification_id)

    @async_timer
    async def batch_update_word_repetition_status(self, user_id: int, word_ids: List[int]) -> None:
        return await self.notification_dao.batch_update_word_repetition_status(user_id, word_ids)

    async def get_users_for_notification(self, notification_time: datetime.time, default_notification_time) -> List[int]:
        return await self.notification_dao.get_users_for_notification(notification_time, default_notification_time)

    async def get_all_users(self) -> List[User]:
        return await self.user_dao.get_all_users()

    async def log_notification(self, user_id: int, notification_type: str) -> int:
        return await self.notification_dao.log_notification(user_id, notification_type)

    async def mark_notification_as_responded(self, notification_id: int) -> None:
        return await self.notification_dao.mark_notification_as_responded(notification_id)

    async def mark_notification_as_replaced(self, notification_id: int) -> None:
        return await self.notification_dao.mark_notification_as_replaced(notification_id)

    async def has_sent_notification_for_hour(self, user_id: int, notification_type: str, hour: int) -> bool:
        return await self.notification_dao.has_sent_notification_for_hour(user_id, notification_type, hour)

    async def delete_old_due_word_notifications(self, interval_hours) -> int:
        return await self.notification_dao.delete_old_due_word_notifications(interval_hours)

    async def get_unanswered_review_notification(self, user_id: int) -> Optional[Dict[str, Any]]:
        return await self.notification_dao.get_unanswered_review_notification(user_id)

    async def update_notification_message_id(self, notification_id: int, message_id: int) -> None:
        return await self.notification_dao.update_notification_message_id(notification_id, message_id)

    async def get_word_details(self, word_id: int) -> Optional[Dict[str, Any]]:
        word = await self.word_dao.get_word_by_id(word_id)
        if word:
            return {
                "word": word.word,
                "short_translation": word.short_translation
            }
        return None

    async def mark_user_as_blocked(self, user_id: int) -> None:
        return await self.user_dao.mark_user_as_blocked(user_id)

    async def update_telegram_handle(self, user_id: int, telegram_handle: str) -> None:
        return await self.user_dao.update_telegram_handle(user_id, telegram_handle)


# Global database instance
db = Database()
