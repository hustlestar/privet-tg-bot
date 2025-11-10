"""Unit tests for database operations using real test database."""

import pytest

from src.dao.models import (
    User,
    ResponseMode,
    ExplanationLanguage,
    TranslationData,
    TrainingAttempt,
    TrainingType,
)


class TestDatabase:
    """Test database operations with real database."""

    @pytest.mark.integration
    async def test_create_and_get_user(self, real_test_database, test_user):
        """Test creating and retrieving a user."""
        db = real_test_database

        # Create user
        await db.create_user(test_user)

        # Retrieve user
        retrieved_user = await db.get_user(test_user.user_id)

        assert retrieved_user is not None
        assert retrieved_user.user_id == test_user.user_id
        assert retrieved_user.native_language == test_user.native_language
        assert retrieved_user.learning_language == test_user.learning_language
        assert retrieved_user.response_mode == test_user.response_mode
        assert retrieved_user.explanation_language == test_user.explanation_language

    @pytest.mark.integration
    async def test_get_user_not_found(self, real_test_database):
        """Test getting a non-existent user."""
        db = real_test_database

        result = await db.get_user(99999)

        assert result is None

    @pytest.mark.integration
    async def test_update_user(self, real_test_database, test_user):
        """Test updating an existing user."""
        db = real_test_database

        # Create user first
        await db.create_user(test_user)

        # Update user
        test_user.response_mode = ResponseMode.LONG
        test_user.explanation_language = ExplanationLanguage.LEARNING
        await db.update_user(test_user)

        # Verify update
        updated_user = await db.get_user(test_user.user_id)
        assert updated_user.response_mode == ResponseMode.LONG
        assert updated_user.explanation_language == ExplanationLanguage.LEARNING

    @pytest.mark.integration
    async def test_update_user_response_mode(self, real_test_database, test_user):
        """Test updating user's response mode."""
        db = real_test_database

        # Create user first
        await db.create_user(test_user)

        # Update response mode
        await db.update_user_response_mode(test_user.user_id, ResponseMode.SHORT)

        # Verify update
        updated_user = await db.get_user(test_user.user_id)
        assert updated_user.response_mode == ResponseMode.SHORT

    @pytest.mark.integration
    async def test_save_and_get_word(self, real_test_database, sample_translation_data):
        """Test saving and retrieving a word translation."""
        db = real_test_database

        # Save word
        word_id = await db.save_word(sample_translation_data)
        assert word_id is not None

        # Retrieve word
        retrieved_word = await db.get_word(
            sample_translation_data.word,
            sample_translation_data.from_language,
            sample_translation_data.to_language,
        )

        assert retrieved_word is not None
        assert retrieved_word.word == sample_translation_data.word
        assert retrieved_word.short_translation == sample_translation_data.short
        assert retrieved_word.medium_data == sample_translation_data.medium
        assert retrieved_word.long_data == sample_translation_data.long

    @pytest.mark.integration
    async def test_get_word_not_found(self, real_test_database):
        """Test getting a non-existent word."""
        db = real_test_database

        result = await db.get_word("nonexistent", "english", "spanish")

        assert result is None

    @pytest.mark.integration
    async def test_user_vocabulary_operations(self, real_test_database, test_user, sample_translation_data):
        """Test user vocabulary operations."""
        db = real_test_database

        # Create user and word
        await db.create_user(test_user)
        word_id = await db.save_word(sample_translation_data)

        # Add word to user vocabulary
        await db.add_word_to_user_vocabulary(test_user.user_id, word_id)

        # Check vocabulary count
        count = await db.get_user_vocabulary_count(test_user.user_id)
        assert count == 1

        # Mark word as known
        result = await db.mark_word_as_known(
            test_user.user_id,
            sample_translation_data.word,
            sample_translation_data.from_language,
            sample_translation_data.to_language,
        )
        assert result is True

    @pytest.mark.integration
    async def test_mark_word_as_known_not_found(self, real_test_database, test_user):
        """Test marking a non-existent word as known."""
        db = real_test_database

        # Create user first
        await db.create_user(test_user)

        result = await db.mark_word_as_known(test_user.user_id, "nonexistent", "english", "spanish")
        assert result is False

    @pytest.mark.integration
    async def test_training_operations(self, real_test_database, test_user, sample_translation_data):
        """Test training-related operations."""
        db = real_test_database

        # Create user and word
        await db.create_user(test_user)
        word_id = await db.save_word(sample_translation_data)
        await db.add_word_to_user_vocabulary(test_user.user_id, word_id)

        # Record training attempt
        attempt = TrainingAttempt(
            user_id=test_user.user_id,
            word_id=word_id,
            training_type=TrainingType.DIRECT_TRANSLATION,
            is_correct=True,
        )
        await db.record_training_attempt(attempt)

        # Get user stats
        stats = await db.get_user_stats(test_user.user_id)
        assert stats["total_words"] == 1
        assert stats["total_attempts"] == 1
        assert stats["total_correct"] == 1

    @pytest.mark.integration
    async def test_get_random_words_for_distractors(self, real_test_database, test_user):
        """Test getting random words for distractors."""
        db = real_test_database

        # Create user and multiple words
        await db.create_user(test_user)

        words = [
            TranslationData(
                word="hello",
                from_language="english",
                to_language="spanish",
                short="hola",
                synonyms=[],
                medium={},
                long={},
            ),
            TranslationData(
                word="goodbye",
                from_language="english",
                to_language="spanish",
                short="adiós",
                synonyms=[],
                medium={},
                long={},
            ),
            TranslationData(
                word="thanks",
                from_language="english",
                to_language="spanish",
                short="gracias",
                synonyms=[],
                medium={},
                long={},
            ),
        ]

        word_ids = []
        for word_data in words:
            word_id = await db.save_word(word_data)
            await db.add_word_to_user_vocabulary(test_user.user_id, word_id)
            word_ids.append(word_id)

        # Get distractors (exclude first word)
        distractors = await db.get_random_words_for_distractors(test_user.user_id, word_ids[0], 2)

        assert len(distractors) <= 2
        assert "hola" not in distractors  # Should exclude the target word

    @pytest.mark.integration
    async def test_language_normalization(self, real_test_database):
        """Test that language normalization is applied correctly."""
        db = real_test_database

        # Create user with mixed case languages
        user = User(
            user_id=54321,
            learning_language="English",
            interface_language="English",
            response_mode=ResponseMode.MEDIUM,
            explanation_language=ExplanationLanguage.NATIVE,
        )

        await db.create_user(user)

        # Retrieve and verify normalization
        retrieved_user = await db.get_user(user.user_id)
        assert retrieved_user.native_language == "spanish"
        assert retrieved_user.learning_language == "english"

    @pytest.mark.integration
    async def test_word_upsert_behavior(self, real_test_database):
        """Test that saving the same word twice updates rather than creates duplicate."""
        db = real_test_database

        translation_data = TranslationData(
            word="test",
            from_language="english",
            to_language="spanish",
            short="prueba",
            synonyms=["exam"],
            medium={"word": "prueba", "meaning": "test"},
            long={"translations": ["prueba"], "context": "testing"},
        )

        # Save word first time
        word_id1 = await db.save_word(translation_data)

        # Modify and save again
        translation_data.short = "examen"
        word_id2 = await db.save_word(translation_data)

        # Should be the same word ID (upsert behavior)
        assert word_id1 == word_id2

        # Verify the update
        retrieved_word = await db.get_word("test", "english", "spanish")
        assert retrieved_word.short_translation == "examen"

    @pytest.mark.integration
    async def test_user_upsert_behavior(self, real_test_database):
        """Test that creating the same user twice updates rather than creates duplicate."""
        db = real_test_database

        user = User(
            user_id=11111,
            learning_language="english",
            interface_language="English",
            response_mode=ResponseMode.SHORT,
            explanation_language=ExplanationLanguage.NATIVE,
        )

        # Create user first time
        await db.create_user(user)

        # Modify and create again
        user.response_mode = ResponseMode.LONG
        await db.create_user(user)

        # Verify the update
        retrieved_user = await db.get_user(user.user_id)
        assert retrieved_user.response_mode == ResponseMode.LONG

    @pytest.mark.integration
    async def test_vocabulary_stats_with_multiple_words(self, real_test_database, test_user):
        """Test vocabulary statistics with multiple words and training attempts."""
        db = real_test_database

        # Create user
        await db.create_user(test_user)

        # Create multiple words
        words_data = [
            ("hello", "hola"),
            ("goodbye", "adiós"),
            ("please", "por favor"),
        ]

        word_ids = []
        for word, translation in words_data:
            translation_data = TranslationData(
                word=word,
                from_language="english",
                to_language="spanish",
                short=translation,
                synonyms=[],
                medium={},
                long={},
            )
            word_id = await db.save_word(translation_data)
            await db.add_word_to_user_vocabulary(test_user.user_id, word_id)
            word_ids.append(word_id)

        # Record some training attempts
        attempts = [
            (word_ids[0], True),  # hello - correct
            (word_ids[0], False),  # hello - incorrect
            (word_ids[1], True),  # goodbye - correct
            (word_ids[2], True),  # please - correct
        ]

        for word_id, is_correct in attempts:
            attempt = TrainingAttempt(
                user_id=test_user.user_id,
                word_id=word_id,
                training_type=TrainingType.MULTIPLE_CHOICE,
                is_correct=is_correct,
            )
            await db.record_training_attempt(attempt)

        # Get stats
        stats = await db.get_user_stats(test_user.user_id)

        assert stats["total_words"] == 3
        assert stats["total_attempts"] == 4
        assert stats["total_correct"] == 3
