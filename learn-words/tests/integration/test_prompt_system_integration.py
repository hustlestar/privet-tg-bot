"""Integration tests for the YAML-based prompt management system."""

import pytest
from unittest.mock import patch

from src.prompt_manager import PromptManager
from src.translation.translator import TranslationService


class TestPromptSystemIntegration:
    """Integration tests for prompt system functionality."""

    @pytest.mark.integration
    def test_prompt_manager_initialization(self, temp_prompts_file):
        """Test that prompt manager initializes correctly."""
        prompt_manager = PromptManager(temp_prompts_file)

        prompt_types = prompt_manager.list_prompt_types()
        assert len(prompt_types) > 0
        assert "language_detection" in prompt_types
        assert "translation" in prompt_types

        # Test OpenAI configuration
        openai_config = prompt_manager.get_openai_config("translation")
        assert openai_config.get("model") is not None
        assert openai_config.get("temperature") is not None

        # Test stop words
        stop_words = prompt_manager.get_stop_words()
        assert len(stop_words) > 0

    @pytest.mark.integration
    def test_prompt_template_rendering(self, temp_prompts_file):
        """Test that prompt templates render correctly with variables."""
        prompt_manager = PromptManager(temp_prompts_file)

        # Test language detection prompt
        system_prompt = prompt_manager.get_system_prompt("language_detection")
        assert system_prompt is not None
        assert len(system_prompt) > 0

        user_prompt = prompt_manager.get_user_prompt("language_detection", text="hello world")
        assert user_prompt is not None
        assert "hello world" in user_prompt

    @pytest.mark.integration
    def test_openai_configuration_per_prompt_type(self, temp_prompts_file):
        """Test that different prompt types have correct OpenAI configurations."""
        prompt_manager = PromptManager(temp_prompts_file)

        lang_config = prompt_manager.get_openai_config("language_detection")
        trans_config = prompt_manager.get_openai_config("translation")

        assert lang_config["model"] is not None
        assert trans_config["model"] is not None
        assert "temperature" in lang_config
        assert "temperature" in trans_config

    @pytest.mark.integration
    @pytest.mark.slow
    async def test_translation_with_yaml_prompts(self, real_test_database, mock_openai_client, temp_prompts_file):
        """Test that translation works with YAML-based prompts."""
        # Create prompt manager and translator
        prompt_manager = PromptManager(temp_prompts_file)
        translator = TranslationService()
        translator.client = mock_openai_client
        translator.prompt_manager = prompt_manager

        with patch("src.translator.db", real_test_database):
            # Test translation
            result = await translator.translate_word_enhanced("test", "english", "spanish", "spanish", "english")

            assert result is not None
            assert result.word == "test"
            assert result.from_language == "english"
            assert result.to_language == "spanish"

            # Verify OpenAI was called with YAML-based prompts
            mock_openai_client.chat.completions.create.assert_called()

    @pytest.mark.integration
    @pytest.mark.slow
    async def test_smart_translation_with_yaml_prompts(self, real_test_database, mock_openai_client, temp_prompts_file):
        """Test that smart translation works with YAML-based prompts."""
        # Create prompt manager and translator
        prompt_manager = PromptManager(temp_prompts_file)
        translator = TranslationService()
        translator.client = mock_openai_client
        translator.prompt_manager = prompt_manager

        with patch("src.translator.db", real_test_database):
            # Test smart translation
            translation_data, detection_result = await translator.smart_translate_word("test", "spanish", "english")

            if translation_data:
                assert translation_data.word == "test"

            # Should have detection result
            assert detection_result is not None

    @pytest.mark.integration
    def test_prompt_system_error_handling(self, temp_prompts_file):
        """Test that prompt system handles errors gracefully."""
        prompt_manager = PromptManager(temp_prompts_file)

        # Test with invalid prompt type
        with pytest.raises(ValueError):
            prompt_manager.get_system_prompt("nonexistent_prompt_type")

        # Test with missing template variables
        with pytest.raises(KeyError):
            prompt_manager.get_user_prompt(
                "language_detection",
                # Missing required 'text' variable
            )

    @pytest.mark.integration
    def test_yaml_configuration_completeness(self, temp_prompts_file):
        """Test that YAML configuration has all required sections."""
        prompt_manager = PromptManager(temp_prompts_file)

        # Test that all expected prompt types exist
        expected_types = [
            "language_detection",
            "translation",
            "word_normalization",
            "sentence_parsing",
        ]
        available_types = prompt_manager.list_prompt_types()

        for expected_type in expected_types:
            assert expected_type in available_types, f"Missing prompt type: {expected_type}"

        # Test that each prompt type has system prompts
        for prompt_type in expected_types:
            system_prompt = prompt_manager.get_system_prompt(prompt_type)
            assert system_prompt is not None and len(system_prompt) > 0

    @pytest.mark.integration
    def test_prompt_manager_caching(self, temp_prompts_file):
        """Test that prompt manager properly caches loaded data."""
        prompt_manager = PromptManager(temp_prompts_file)

        # First call should load from file
        config1 = prompt_manager.get_openai_config("translation")

        # Second call should use cached data
        config2 = prompt_manager.get_openai_config("translation")

        # Should be the same object (cached)
        assert config1 is config2

    @pytest.mark.integration
    def test_prompt_variable_substitution(self, temp_prompts_file):
        """Test that prompt variables are properly substituted."""
        prompt_manager = PromptManager(temp_prompts_file)

        # Test translation prompt with variables
        user_prompt = prompt_manager.get_user_prompt("translation", word="hello", from_language="english", to_language="spanish")

        assert "hello" in user_prompt
        assert "english" in user_prompt.lower()
        assert "spanish" in user_prompt.lower()

    @pytest.mark.integration
    def test_fallback_configuration(self, temp_prompts_file):
        """Test that fallback configuration works correctly."""
        prompt_manager = PromptManager(temp_prompts_file)

        # Test stop words from fallback section
        stop_words = prompt_manager.get_stop_words()
        assert isinstance(stop_words, list)
        assert len(stop_words) > 0
        assert "the" in stop_words
        assert "a" in stop_words
