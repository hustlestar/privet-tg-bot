"""Integration tests for the Learn Words Telegram Bot."""

import pytest
from unittest.mock import patch

from src.config import get_config
from src.dao.models import User, Word, ResponseMode, TrainingType
from src.translation.translator import TranslationService
from src.bot import create_application


class TestBotIntegration:
    """Integration tests for bot functionality."""

    @pytest.mark.integration
    async def test_imports(self):
        """Test that all modules can be imported."""
        # All imports should work without errors
        from src.config import get_config
        from src.dao.models import User
        from src.database import db
        from src.translation.translator import TranslationService
        from src.training import training_system
        from src.bot import create_application

        assert get_config is not None
        assert User is not None
        assert db is not None
        assert TranslationService is not None
        assert training_system is not None
        assert create_application is not None

    @pytest.mark.integration
    def test_config_loading(self):
        """Test configuration loading."""
        config = get_config()

        # Check that config object exists
        assert config is not None
        assert hasattr(config, "telegram_token")
        assert hasattr(config, "openai_api_key")
        assert hasattr(config, "database_url")

    @pytest.mark.integration
    @pytest.mark.slow
    async def test_database_connection(self, real_test_database):
        """Test database connection with real database."""
        db = real_test_database

        # Test a simple query
        async with db.pool.acquire() as conn:
            result = await conn.fetchval("SELECT 1")
            assert result == 1

    @pytest.mark.integration
    @pytest.mark.slow
    async def test_openai_connection(self, real_test_database, mock_openai_client):
        """Test OpenAI API connection with mocked client."""
        # Create translator with real database and mocked OpenAI
        translator = TranslationService()
        translator.client = mock_openai_client

        # Patch the global db instance to use our test database
        with patch("src.translator.db", real_test_database):
            result = await translator.translate_word("hello", "English", "Spanish")

            assert result is not None
            assert result.short is not None
            mock_openai_client.chat.completions.create.assert_called_once()

    @pytest.mark.integration
    def test_bot_creation(self):
        """Test bot application creation."""
        app = create_application()

        assert app is not None
        assert hasattr(app, "add_handler")
        assert hasattr(app, "run_polling")

    @pytest.mark.integration
    async def test_user_model_creation(self):
        """Test user model creation and validation."""
        user = User(
            user_id=12345,
            learning_language="english",
            interface_language="English",
            response_mode=ResponseMode.MEDIUM,
        )

        assert user.user_id == 12345
        assert user.learning_language == "english"
        assert user.response_mode == ResponseMode.MEDIUM

    @pytest.mark.integration
    async def test_word_model_creation(self):
        """Test word model creation and validation."""
        word = Word(
            id=1,
            word="hello",
            from_language="english",
            to_language="spanish",
            short_translation="hola",
            medium_data={
                "word": "hola",
                "meaning": "greeting",
                "example": "Hola amigo",
            },
            long_data={
                "translations": ["hola", "saludos"],
                "meanings": ["greeting"],
                "examples": ["Hola amigo"],
                "context": "Common greeting",
            },
        )

        assert word.id == 1
        assert word.word == "hello"
        assert word.short_translation == "hola"
        assert isinstance(word.medium_data, dict)
        assert isinstance(word.long_data, dict)

    @pytest.mark.integration
    @pytest.mark.slow
    async def test_full_translation_workflow(self, real_test_database, mock_openai_client):
        """Test the complete translation workflow."""
        # Create translator with real database and mocked OpenAI
        translator = TranslationService()
        translator.client = mock_openai_client

        # Patch the global db instance to use our test database
        with patch("src.translator.db", real_test_database):
            # Test translation (should not find in cache, then save)
            result = await translator.translate_word_enhanced("hello", "english", "spanish", "spanish", "english")

            assert result is not None
            assert result.word == "hello"
            assert result.from_language == "english"
            assert result.to_language == "spanish"

            # Verify OpenAI was called
            mock_openai_client.chat.completions.create.assert_called_once()

            # Verify word was saved to database
            saved_word = await real_test_database.get_word("hello", "english", "spanish")
            assert saved_word is not None
            assert saved_word.word == "hello"

    @pytest.mark.integration
    async def test_training_type_enum(self):
        """Test training type enumeration."""
        assert TrainingType.DIRECT_TRANSLATION.value == "A"
        assert TrainingType.MULTIPLE_CHOICE.value == "B"
        assert TrainingType.REVERSE_TRANSLATION.value == "C"

        # Test all training types are valid
        for training_type in TrainingType:
            assert training_type.value in ["A", "B", "C"]

    @pytest.mark.integration
    async def test_response_mode_enum(self):
        """Test response mode enumeration."""
        assert ResponseMode.SHORT.value == "short"
        assert ResponseMode.MEDIUM.value == "medium"
        assert ResponseMode.LONG.value == "long"

        # Test all response modes are valid
        for mode in ResponseMode:
            assert mode.value in ["short", "medium", "long"]

    @pytest.mark.integration
    async def test_database_user_operations(self, real_test_database, test_user):
        """Test database user operations integration."""
        db = real_test_database

        # Create user
        await db.create_user(test_user)

        # Retrieve user
        retrieved_user = await db.get_user(test_user.user_id)
        assert retrieved_user is not None
        assert retrieved_user.user_id == test_user.user_id

        # Update user
        test_user.response_mode = ResponseMode.LONG
        await db.update_user(test_user)

        # Verify update
        updated_user = await db.get_user(test_user.user_id)
        assert updated_user.response_mode == ResponseMode.LONG

    @pytest.mark.integration
    async def test_translation_caching(self, real_test_database, mock_openai_client, sample_translation_data):
        """Test that translations are properly cached in the database."""
        translator = TranslationService()
        translator.client = mock_openai_client

        with patch("src.translator.db", real_test_database):
            # First translation - should call OpenAI and cache
            result1 = await translator.translate_word("hello", "english", "spanish")
            assert result1 is not None

            # Reset mock to verify second call doesn't hit OpenAI
            mock_openai_client.reset_mock()

            # Second translation - should use cache
            result2 = await translator.translate_word("hello", "english", "spanish")
            assert result2 is not None
            assert result2.word == result1.word

            # OpenAI should not be called the second time
            mock_openai_client.chat.completions.create.assert_not_called()
