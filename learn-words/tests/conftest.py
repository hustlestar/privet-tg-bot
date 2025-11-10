"""Shared pytest fixtures and configuration for Learn Words tests."""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import os
import tempfile
import subprocess
import time
from pathlib import Path

# Add src to path for imports
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.config import Config
from src.database import Database
from src.dao.models import User, ResponseMode, ExplanationLanguage, TranslationData
from src.translation.translator import TranslationService
from src.prompt_manager import PromptManager


# Test database configuration
TEST_DB_URL = "postgresql://test_user:test_password@localhost:5433/learn_words_test"


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "performance: marks tests as performance tests")
    config.addinivalue_line("markers", "slow: marks tests as slow running")


@pytest.fixture(scope="session")
def docker_compose_file():
    """Return the docker-compose file for tests."""
    return Path(__file__).parent.parent / "docker-compose.test.yml"


@pytest.fixture(scope="session")
def test_database_container(docker_compose_file):
    """Start test database container and ensure it's ready."""
    # Start the test database
    subprocess.run(
        ["docker-compose", "-f", str(docker_compose_file), "up", "-d", "test-postgres"],
        check=True,
        capture_output=True,
    )

    # Wait for database to be ready
    max_retries = 30
    for i in range(max_retries):
        try:
            result = subprocess.run(
                [
                    "docker",
                    "exec",
                    "learn-words-test-db",
                    "pg_isready",
                    "-U",
                    "test_user",
                    "-d",
                    "learn_words_test",
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                break
        except subprocess.CalledProcessError:
            pass

        if i == max_retries - 1:
            raise RuntimeError("Test database failed to start")

        time.sleep(1)

    yield

    # Cleanup: stop the container
    subprocess.run(
        ["docker-compose", "-f", str(docker_compose_file), "down", "-v"],
        capture_output=True,
    )


@pytest_asyncio.fixture
async def real_test_database(test_database_container):
    """Provide a real test database instance with clean state for each test."""

    # Create a fresh database instance
    db = Database()

    # Override the database URL for testing
    original_config = None
    with patch("src.database.get_config") as mock_get_config:
        mock_config = Config(
            telegram_token="test_token",
            openai_api_key="test_openai_key",
            database_url=TEST_DB_URL,
        )
        mock_get_config.return_value = mock_config

        # Connect to test database
        await db.connect()

    # Clean up any existing test data
    async with db.pool.acquire() as conn:
        await conn.execute("TRUNCATE TABLE training_attempts, user_word_stats, words, users RESTART IDENTITY CASCADE")

    yield db

    # Cleanup
    if db.pool:
        await db.close()


@pytest.fixture
def mock_config() -> Config:
    """Provide a mock configuration for testing."""
    return Config(
        telegram_token="test_token",
        openai_api_key="test_openai_key",
        database_url=TEST_DB_URL,
    )


@pytest.fixture
def test_user() -> User:
    """Provide a test user for testing."""
    return User(
        user_id=12345,
        learning_language="english",
        interface_language="English",
        response_mode=ResponseMode.MEDIUM,
        explanation_language=ExplanationLanguage.NATIVE,
    )


@pytest.fixture
def another_test_user() -> User:
    """Provide another test user for testing."""
    return User(
        user_id=67890,
        learning_language="spanish",
        interface_language="English",
        response_mode=ResponseMode.SHORT,
        explanation_language=ExplanationLanguage.LEARNING,
    )


@pytest.fixture
def sample_translation_data() -> TranslationData:
    """Provide sample translation data for testing."""
    return TranslationData(
        word="hello",
        from_language="english",
        to_language="spanish",
        short="hola",
        synonyms=["hi", "hello"],
        medium={"word": "hola", "meaning": "greeting", "example": "Hola, ¿cómo estás?"},
        long={
            "translations": ["hello", "hi"],
            "meanings": ["greeting", "salutation"],
            "examples": ["Hola amigo", "Hola, buenos días"],
            "context": "Common Spanish greeting",
        },
    )


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    mock_client = AsyncMock()

    # Mock chat completion response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = (
        '{"short": "hola", "medium": {"word": "hola", "meaning": "greeting", "example": "Hola, ¿cómo estás?"}, "long": {"translations": ["hello", "hi"], "meanings": ["greeting", "salutation"], "examples": ["Hola amigo", "Hola, buenos días"], "context": "Common Spanish greeting"}}'
    )

    mock_client.chat.completions.create.return_value = mock_response
    return mock_client


@pytest.fixture
def mock_database():
    """Mock database for testing (for unit tests that don't need real DB)."""
    mock_db = AsyncMock(spec=Database)

    # Create a proper async context manager mock for pool.acquire()
    mock_conn = AsyncMock()
    mock_acquire = AsyncMock()
    mock_acquire.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_acquire.__aexit__ = AsyncMock(return_value=None)

    mock_pool = AsyncMock()
    mock_pool.acquire.return_value = mock_acquire
    mock_pool.close = AsyncMock()

    # Set up the database mock
    mock_db.pool = mock_pool
    mock_db.connect.return_value = None
    mock_db.close.return_value = None
    mock_db.get_user.return_value = None
    mock_db.create_user.return_value = None
    mock_db.update_user.return_value = None
    mock_db.get_word.return_value = None
    mock_db.save_word.return_value = 1
    mock_db.add_word_to_user_vocabulary.return_value = None

    return mock_db


@pytest.fixture
def mock_translator(mock_openai_client, sample_translation_data):
    """Mock translator for testing."""
    mock_trans = AsyncMock(spec=TranslationService)

    mock_trans.translate_word_enhanced.return_value = sample_translation_data
    mock_trans.smart_translate_word.return_value = (
        sample_translation_data,
        {"explanation": "Found in cache"},
    )
    mock_trans.parse_sentence_to_words.return_value = ["hello", "world"]
    mock_trans.translate_word.return_value = sample_translation_data

    return mock_trans


@pytest.fixture
def mock_prompt_manager():
    """Mock prompt manager for testing."""
    mock_pm = MagicMock(spec=PromptManager)

    mock_pm.get_system_prompt.return_value = "You are a helpful translation assistant."
    mock_pm.get_user_prompt.return_value = "Translate 'hello' from English to Spanish."
    mock_pm.get_openai_config.return_value = {
        "model": "gpt-4o-mini",
        "temperature": 0.3,
        "max_tokens": 1000,
        "response_format": {"type": "json_object"},
    }
    mock_pm.get_stop_words.return_value = ["the", "a", "an"]
    mock_pm.list_prompt_types.return_value = [
        "translation",
        "language_detection",
        "word_normalization",
        "sentence_parsing",
    ]

    return mock_pm


@pytest_asyncio.fixture
async def test_database():
    """Legacy fixture for backward compatibility - use real_test_database instead."""
    # Set environment variable for tests that check for it
    os.environ["TEST_DATABASE_URL"] = TEST_DB_URL

    # This fixture now just sets the environment variable
    # Tests should use real_test_database for actual database access
    yield None


@pytest.fixture
def temp_prompts_file():
    """Create a temporary prompts.yaml file for testing."""
    prompts_content = """
openai:
  model: "gpt-4o-mini"
  response_format:
    type: "json_object"
  temperature:
    translation: 0.3
    language_detection: 0.1
    word_normalization: 0.1
    sentence_parsing: 0.2

prompts:
  translation:
    system: "You are a helpful translation assistant."
    user_template: "Translate '{word}' from {from_language} to {to_language}."

  language_detection:
    system: "You are a language detection expert."
    user_template: "Detect the language of: {text}"
    
  word_normalization:
    system: "You are a word normalization expert."
    user_template: "Normalize these words in {language}: {words_list}"
    
  sentence_parsing:
    system: "You are a sentence parsing expert."
    user_template: "Parse this sentence into words: {sentence}"

fallback:
  stop_words: ["the", "a", "an", "and", "or", "but"]
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(prompts_content)
        temp_file = f.name

    yield temp_file

    # Cleanup
    os.unlink(temp_file)


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Set up test environment variables."""
    monkeypatch.setenv("TELEGRAM_TOKEN", "test_token")
    monkeypatch.setenv("OPENAI_API_KEY", "test_openai_key")
    monkeypatch.setenv("DATABASE_URL", TEST_DB_URL)
    monkeypatch.setenv("TEST_DATABASE_URL", TEST_DB_URL)


# Markers for different test types
pytestmark = [
    pytest.mark.asyncio,
]
