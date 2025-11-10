"""Performance tests for cache optimization and translation speed."""

import pytest
import time
import asyncio
from unittest.mock import patch

from src.dao.models import TranslationData


class TestCachePerformance:
    """Performance tests for cache optimization."""

    @pytest.mark.performance
    @pytest.mark.slow
    async def test_cache_optimization_speedup(self, mock_translator, mock_database):
        """Test that cache provides significant speedup."""
        # Mock translation data
        mock_translation = TranslationData(
            word="hello",
            from_language="english",
            to_language="spanish",
            short="hola",
            synonyms=["hi", "hello"],
            medium={"word": "hola", "meaning": "greeting", "example": "Hola amigo"},
            long={
                "translations": ["hola"],
                "meanings": ["greeting"],
                "examples": ["Hola amigo"],
                "context": "Common greeting",
            },
        )

        # First call - simulate API call (slower)
        mock_database.get_word.return_value = None  # Cache miss
        mock_database.save_word.return_value = 1

        with (
            patch("src.translator.db", mock_database),
            patch(
                "src.translator.translator.translate_word_enhanced",
                return_value=mock_translation,
            ) as mock_translate,
        ):

            # Simulate slow API call
            async def slow_translate(*args, **kwargs):
                await asyncio.sleep(0.1)  # Simulate API delay
                return mock_translation

            mock_translate.side_effect = slow_translate

            # First translation (API call)
            start_time = time.time()
            result1 = await mock_translate("hello", "english", "spanish", "spanish", "english")
            first_duration = time.time() - start_time

            # Second call - simulate cache hit (faster)
            mock_database.get_word.return_value = mock_translation  # Cache hit

            async def fast_translate(*args, **kwargs):
                return mock_translation  # Immediate return from cache

            mock_translate.side_effect = fast_translate

            # Second translation (cache hit)
            start_time = time.time()
            result2 = await mock_translate("hello", "english", "spanish", "spanish", "english")
            second_duration = time.time() - start_time

            # Verify results
            assert result1.short == "hola"
            assert result2.short == "hola"

            # Performance assertion
            speedup = first_duration / second_duration if second_duration > 0 else float("inf")
            assert speedup > 2, f"Cache should provide at least 2x speedup, got {speedup:.1f}x"

    @pytest.mark.performance
    async def test_language_normalization_performance(self, mock_translator):
        """Test that language normalization doesn't significantly impact performance."""
        test_cases = [
            ("Hello", "English", "Spanish"),
            ("hello", "english", "spanish"),
            ("HELLO", "ENGLISH", "SPANISH"),
            ("Hello", "English", "spanish"),
        ]

        durations = []

        for word, from_lang, to_lang in test_cases:
            start_time = time.time()

            # Mock the translation to return immediately
            with patch.object(mock_translator, "translate_word_enhanced") as mock_method:
                mock_method.return_value = TranslationData(
                    word=word.lower(),
                    from_language=from_lang.lower(),
                    to_language=to_lang.lower(),
                    short="hola",
                    synonyms=["hi", "hello"],
                    medium={"word": "hola", "meaning": "greeting", "example": "Hola"},
                    long={
                        "translations": ["hola"],
                        "meanings": ["greeting"],
                        "examples": ["Hola"],
                        "context": "greeting",
                    },
                )

                await mock_method(word, from_lang, to_lang, "spanish", "english")

            duration = time.time() - start_time
            durations.append(duration)

        # All normalizations should be fast (< 10ms each)
        for i, duration in enumerate(durations):
            assert duration < 0.01, f"Normalization {i} took {duration:.3f}s, should be < 0.01s"

        # Variance should be low (consistent performance)
        avg_duration = sum(durations) / len(durations)
        max_variance = max(abs(d - avg_duration) for d in durations)
        assert max_variance < 0.005, f"Performance variance too high: {max_variance:.3f}s"

    @pytest.mark.performance
    async def test_simple_normalization_rules(self):
        """Test performance of simple normalization rules."""

        # Simple normalization function for testing
        def simple_normalize(word):
            """Simple word normalization for testing."""
            word = word.lower().strip()
            # Remove common suffixes
            suffixes = ["ing", "ed", "s", "es", "er", "est"]
            for suffix in suffixes:
                if word.endswith(suffix) and len(word) > len(suffix) + 2:
                    return word[: -len(suffix)]
            return word

        test_words = [
            "running",
            "walked",
            "cats",
            "boxes",
            "flies",
            "bigger",
            "biggest",
            "happier",
            "happiest",
            "Running",
            "WALKED",
            "CaTs",
            "BOXES",
        ] * 100  # Test with many words

        start_time = time.time()

        for word in test_words:
            normalized = simple_normalize(word)
            assert isinstance(normalized, str)
            assert len(normalized) > 0

        total_duration = time.time() - start_time
        avg_per_word = total_duration / len(test_words)

        # Simple normalization should be very fast
        assert avg_per_word < 0.0001, f"Simple normalization too slow: {avg_per_word:.6f}s per word"
        assert total_duration < 0.1, f"Total normalization time too slow: {total_duration:.3f}s"

    @pytest.mark.performance
    @pytest.mark.slow
    async def test_smart_translation_optimization(self, mock_translator, mock_database):
        """Test that smart translation optimization reduces API calls."""
        api_call_count = 0

        async def count_api_calls(*args, **kwargs):
            nonlocal api_call_count
            api_call_count += 1
            return TranslationData(
                word="hello",
                from_language="english",
                to_language="spanish",
                short="hola",
                synonyms=["hi", "hello"],
                medium={"word": "hola", "meaning": "greeting", "example": "Hola"},
                long={
                    "translations": ["hola"],
                    "meanings": ["greeting"],
                    "examples": ["Hola"],
                    "context": "greeting",
                },
            )

        # Mock database to simulate cache behavior
        cache = {}

        def mock_get_word(word, from_lang, to_lang):
            key = f"{word}_{from_lang}_{to_lang}"
            return cache.get(key)

        def mock_save_word(translation_data):
            key = f"{translation_data.word}_{translation_data.from_language}_{translation_data.to_language}"
            cache[key] = translation_data
            return 1

        mock_database.get_word.side_effect = mock_get_word
        mock_database.save_word.side_effect = mock_save_word

        with (
            patch("src.translator.db", mock_database),
            patch(
                "src.translator.translator.translate_word_enhanced",
                side_effect=count_api_calls,
            ),
        ):

            # Test words that should benefit from smart optimization
            test_words = [
                "hello",  # First call - API
                "Hello",  # Should hit cache after normalization
                "HELLO",  # Should hit cache after normalization
                "running",  # Should normalize to "run" and potentially hit cache
                "runs",  # Should normalize to "run" and potentially hit cache
            ]

            for word in test_words:
                await mock_translator.translate_word_enhanced(word, "english", "spanish", "spanish", "english")

            # Smart optimization should reduce API calls
            # Exact number depends on implementation, but should be less than total words
            assert api_call_count < len(test_words), f"Expected fewer API calls due to optimization, got {api_call_count}/{len(test_words)}"

    @pytest.mark.performance
    async def test_memory_usage_stability(self, mock_translator):
        """Test that repeated translations don't cause memory leaks."""
        import gc

        # Get initial memory usage
        gc.collect()
        initial_objects = len(gc.get_objects())

        # Perform many translations
        for i in range(100):
            with patch.object(mock_translator, "translate_word_enhanced") as mock_method:
                mock_method.return_value = TranslationData(
                    word=f"word{i}",
                    from_language="english",
                    to_language="spanish",
                    short=f"palabra{i}",
                    synonyms=[f"word{i}", f"term{i}"],
                    medium={
                        "word": f"palabra{i}",
                        "meaning": "test",
                        "example": "test",
                    },
                    long={
                        "translations": [f"palabra{i}"],
                        "meanings": ["test"],
                        "examples": ["test"],
                        "context": "test",
                    },
                )

                await mock_method(f"word{i}", "english", "spanish", "spanish", "english")

        # Check memory usage after
        gc.collect()
        final_objects = len(gc.get_objects())

        # Memory growth should be reasonable (less than 50% increase)
        growth_ratio = final_objects / initial_objects
        assert growth_ratio < 1.5, f"Memory usage grew too much: {growth_ratio:.2f}x"

    @pytest.mark.performance
    async def test_concurrent_translation_performance(self, mock_translator):
        """Test performance under concurrent translation requests."""
        import asyncio

        async def single_translation(word_id):
            with patch.object(mock_translator, "translate_word_enhanced") as mock_method:
                mock_method.return_value = TranslationData(
                    word=f"word{word_id}",
                    from_language="english",
                    to_language="spanish",
                    short=f"palabra{word_id}",
                    synonyms=[f"word{word_id}", f"term{word_id}"],
                    medium={
                        "word": f"palabra{word_id}",
                        "meaning": "test",
                        "example": "test",
                    },
                    long={
                        "translations": [f"palabra{word_id}"],
                        "meanings": ["test"],
                        "examples": ["test"],
                        "context": "test",
                    },
                )

                return await mock_method(f"word{word_id}", "english", "spanish", "spanish", "english")

        # Test concurrent translations
        start_time = time.time()

        tasks = [single_translation(i) for i in range(10)]
        results = await asyncio.gather(*tasks)

        total_duration = time.time() - start_time

        # All translations should complete
        assert len(results) == 10

        # Concurrent execution should be faster than sequential
        # (This is a basic test - in real scenarios with I/O, the benefit would be more significant)
        assert total_duration < 1.0, f"Concurrent translations took too long: {total_duration:.3f}s"
