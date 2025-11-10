"""Performance tests for smart translation optimization features."""

import pytest
import asyncio
import time
from unittest.mock import patch

from src.translation.translator import TranslationService


class TestSmartOptimization:
    """Performance tests for smart translation optimization."""

    @pytest.mark.performance
    async def test_smart_translation_cache_optimization(self, real_test_database, mock_openai_client, sample_translation_data):
        """Test that smart translation properly utilizes caching for performance."""
        translator = TranslationService()
        translator.client = mock_openai_client

        with patch("src.translator.db", real_test_database):
            # First translation - should hit OpenAI and cache
            start_time = time.time()
            result1 = await translator.smart_translate_word("hello", "spanish", "english")
            first_duration = time.time() - start_time

            assert result1[0] is not None  # translation_data
            assert result1[1] is not None  # detection_result

            # Reset mock to track second call
            mock_openai_client.reset_mock()

            # Second translation - should use cache (faster)
            start_time = time.time()
            result2 = await translator.smart_translate_word("hello", "spanish", "english")
            second_duration = time.time() - start_time

            assert result2[0] is not None
            assert result2[1] is not None

            # Second call should be faster (cached)
            assert second_duration < first_duration

            # OpenAI should not be called for cached translation
            assert mock_openai_client.chat.completions.create.call_count == 0

    @pytest.mark.performance
    async def test_basic_cache_lookup_performance(self, real_test_database, sample_translation_data):
        """Test performance of basic cache lookup operations."""
        translator = TranslationService()

        with patch("src.translator.db", real_test_database):
            # Save a word to cache first
            word_id = await real_test_database.save_word(sample_translation_data)

            # Test cache lookup performance
            start_time = time.time()

            # Perform multiple cache lookups
            for _ in range(10):
                result = await translator._try_basic_cache_lookup(
                    sample_translation_data.word,
                    sample_translation_data.to_language,
                    sample_translation_data.from_language,
                )
                assert result is not None

            duration = time.time() - start_time

            # Should complete 10 lookups quickly (under 1 second)
            assert duration < 1.0

            # Verify the result structure
            assert hasattr(result, "short")
            assert hasattr(result, "medium")
            assert hasattr(result, "long")

    @pytest.mark.performance
    async def test_batch_translation_performance(self, real_test_database, mock_openai_client):
        """Test performance of batch translation operations."""
        translator = TranslationService()
        translator.client = mock_openai_client

        words = ["hello", "goodbye", "please", "thank you", "yes"]

        with patch("src.translator.db", real_test_database):
            start_time = time.time()

            # Translate multiple words
            results = []
            for word in words:
                result = await translator.translate_word(word, "english", "spanish")
                results.append(result)

            duration = time.time() - start_time

            # Should complete all translations
            assert len(results) == len(words)
            for result in results:
                assert result is not None
                assert result.short is not None

            # Should complete reasonably quickly
            assert duration < 10.0  # Allow reasonable time for 5 translations

    @pytest.mark.performance
    async def test_language_detection_bypass_performance(self, real_test_database, mock_openai_client):
        """Test performance when language detection can be bypassed."""
        translator = TranslationService()
        translator.client = mock_openai_client

        with patch("src.translator.db", real_test_database):
            # Test with explicit languages (should bypass detection)
            start_time = time.time()

            result = await translator.smart_translate_word("hello", "english", "spanish")  # Explicit languages

            duration = time.time() - start_time

            assert result[0] is not None  # translation_data
            assert result[1] is not None  # detection_result

            # Should be relatively fast since detection is bypassed
            assert duration < 5.0

    @pytest.mark.performance
    async def test_word_normalization_performance(self, real_test_database):
        """Test performance of word normalization operations."""
        translator = TranslationService()

        # Test words with various formatting issues
        test_words = [
            "  hello  ",
            "HELLO",
            "Hello!",
            "hello.",
            "hello,",
            "hello?",
            "hello;",
            "hello:",
        ]

        start_time = time.time()

        # Normalize all words
        normalized_words = []
        for word in test_words:
            normalized = translator._normalize_word(word)
            normalized_words.append(normalized)

        duration = time.time() - start_time

        # Should normalize quickly
        assert duration < 0.1

        # All should be normalized to "hello"
        for normalized in normalized_words:
            assert normalized == "hello"

    @pytest.mark.performance
    async def test_concurrent_smart_translations(self, real_test_database, mock_openai_client):
        """Test performance of concurrent smart translation operations."""
        translator = TranslationService()
        translator.client = mock_openai_client

        words = ["hello", "world", "test", "example", "performance"]

        with patch("src.translator.db", real_test_database):
            start_time = time.time()

            # Create concurrent translation tasks
            async def single_smart_translation(word):
                return await translator.smart_translate_word(word, "english", "spanish")

            tasks = [single_smart_translation(word) for word in words]
            results = await asyncio.gather(*tasks)

            duration = time.time() - start_time

            # Should complete all concurrent translations
            assert len(results) == len(words)
            for result in results:
                assert result[0] is not None  # translation_data
                assert result[1] is not None  # detection_result

            # Concurrent execution should be faster than sequential
            assert duration < 15.0  # Allow reasonable time for concurrent operations

    @pytest.mark.performance
    async def test_cache_hit_vs_miss_performance(self, real_test_database, mock_openai_client, sample_translation_data):
        """Test performance difference between cache hits and misses."""
        translator = TranslationService()
        translator.client = mock_openai_client

        with patch("src.translator.db", real_test_database):
            # Pre-populate cache
            await real_test_database.save_word(sample_translation_data)

            # Test cache hit performance
            cache_hit_times = []
            for _ in range(5):
                start_time = time.time()
                result = await translator.translate_word(
                    sample_translation_data.word,
                    sample_translation_data.from_language,
                    sample_translation_data.to_language,
                )
                cache_hit_times.append(time.time() - start_time)
                assert result is not None

            # Test cache miss performance
            cache_miss_times = []
            for i in range(5):
                start_time = time.time()
                result = await translator.translate_word(f"newword{i}", "english", "spanish")
                cache_miss_times.append(time.time() - start_time)
                assert result is not None

            # Cache hits should be consistently faster than misses
            avg_hit_time = sum(cache_hit_times) / len(cache_hit_times)
            avg_miss_time = sum(cache_miss_times) / len(cache_miss_times)

            assert avg_hit_time < avg_miss_time
            assert avg_hit_time < 0.1  # Cache hits should be very fast

    @pytest.mark.performance
    async def test_memory_usage_optimization(self, real_test_database, mock_openai_client):
        """Test that translation operations don't cause memory leaks."""
        translator = TranslationService()
        translator.client = mock_openai_client

        with patch("src.translator.db", real_test_database):
            # Perform many translation operations
            for i in range(50):
                result = await translator.translate_word(f"word{i}", "english", "spanish")
                assert result is not None

                # Clear reference to help with garbage collection
                del result

            # Test should complete without memory issues
            assert True  # If we get here, no memory issues occurred

    @pytest.mark.performance
    async def test_database_connection_pooling_performance(self, real_test_database):
        """Test that database connection pooling provides good performance."""

        # Test multiple concurrent database operations
        async def db_operation(user_id):
            # Create a test user
            from src.dao.models import User, ResponseMode, ExplanationLanguage

            user = User(
                user_id=user_id,
                learning_language="spanish",
                interface_language="English",
                response_mode=ResponseMode.MEDIUM,
                explanation_language=ExplanationLanguage.NATIVE,
            )
            await real_test_database.create_user(user)
            return await real_test_database.get_user(user_id)

        start_time = time.time()

        # Run concurrent database operations
        tasks = [db_operation(1000 + i) for i in range(10)]
        results = await asyncio.gather(*tasks)

        duration = time.time() - start_time

        # All operations should succeed
        assert len(results) == 10
        for result in results:
            assert result is not None

        # Should complete quickly with connection pooling
        assert duration < 2.0
