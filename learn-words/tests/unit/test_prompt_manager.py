"""Unit tests for the prompt manager module."""

import pytest
from unittest.mock import patch, mock_open, MagicMock
import tempfile
import os

from src.prompt_manager import PromptManager


class TestPromptManager:
    """Unit tests for PromptManager class."""

    @pytest.mark.unit
    def test_prompt_manager_initialization(self, temp_prompts_file):
        """Test prompt manager initialization with valid YAML file."""
        with patch("src.prompt_manager.Path") as mock_path:
            mock_path.return_value.exists.return_value = True

            with patch("builtins.open", mock_open(read_data=open(temp_prompts_file).read())):
                pm = PromptManager(temp_prompts_file)

                assert pm.prompts is not None
                assert pm.openai_config is not None
                assert "translation" in pm.prompts
                assert "language_detection" in pm.prompts

    @pytest.mark.unit
    def test_prompt_manager_missing_file(self):
        """Test prompt manager with missing YAML file."""
        with patch("builtins.open", side_effect=FileNotFoundError("File not found")):
            with pytest.raises(FileNotFoundError):
                PromptManager("nonexistent.yaml")

    @pytest.mark.unit
    def test_get_system_prompt(self, temp_prompts_file):
        """Test getting system prompts."""
        with patch("src.prompt_manager.Path") as mock_path:
            mock_path.return_value.exists.return_value = True

            with patch("builtins.open", mock_open(read_data=open(temp_prompts_file).read())):
                pm = PromptManager(temp_prompts_file)

                system_prompt = pm.get_system_prompt("translation")
                assert system_prompt == "You are a helpful translation assistant."

                # Test non-existent prompt type
                with pytest.raises(ValueError):
                    pm.get_system_prompt("nonexistent")

    @pytest.mark.unit
    def test_get_user_prompt_with_template(self, temp_prompts_file):
        """Test getting user prompts with template variables."""
        with patch("src.prompt_manager.Path") as mock_path:
            mock_path.return_value.exists.return_value = True

            with patch("builtins.open", mock_open(read_data=open(temp_prompts_file).read())):
                pm = PromptManager(temp_prompts_file)

                user_prompt = pm.get_user_prompt(
                    "translation",
                    word="hello",
                    from_language="English",
                    to_language="Spanish",
                )

                assert "hello" in user_prompt
                assert "English" in user_prompt
                assert "Spanish" in user_prompt

    @pytest.mark.unit
    def test_get_openai_config(self, temp_prompts_file):
        """Test getting OpenAI configuration."""
        with patch("src.prompt_manager.Path") as mock_path:
            mock_path.return_value.exists.return_value = True

            with patch("builtins.open", mock_open(read_data=open(temp_prompts_file).read())):
                pm = PromptManager(temp_prompts_file)

                # Test prompt-specific config
                config = pm.get_openai_config("translation")
                assert config["temperature"] == 0.3
                assert config["response_format"]["type"] == "json_object"

                # Test fallback to global config
                config = pm.get_openai_config("language_detection")
                assert config["temperature"] == 0.1
                assert config["model"] == "gpt-4o-mini"

    @pytest.mark.unit
    def test_get_stop_words(self, temp_prompts_file):
        """Test getting stop words."""
        with patch("src.prompt_manager.Path") as mock_path:
            mock_path.return_value.exists.return_value = True

            with patch("builtins.open", mock_open(read_data=open(temp_prompts_file).read())):
                pm = PromptManager(temp_prompts_file)

                stop_words = pm.get_stop_words()
                assert "the" in stop_words
                assert "a" in stop_words
                assert isinstance(stop_words, list)

    @pytest.mark.unit
    def test_list_prompt_types(self, temp_prompts_file):
        """Test listing available prompt types."""
        with patch("src.prompt_manager.Path") as mock_path:
            mock_path.return_value.exists.return_value = True

            with patch("builtins.open", mock_open(read_data=open(temp_prompts_file).read())):
                pm = PromptManager(temp_prompts_file)

                prompt_types = pm.list_prompt_types()
                assert "translation" in prompt_types
                assert "language_detection" in prompt_types
                assert isinstance(prompt_types, list)

    @pytest.mark.unit
    def test_template_rendering_edge_cases(self, temp_prompts_file):
        """Test template rendering with edge cases."""
        with patch("src.prompt_manager.Path") as mock_path:
            mock_path.return_value.exists.return_value = True

            with patch("builtins.open", mock_open(read_data=open(temp_prompts_file).read())):
                pm = PromptManager(temp_prompts_file)

                # Test with missing template variables - should raise ValueError
                with pytest.raises(ValueError):
                    pm.get_user_prompt("translation", word="hello")

                # Test with extra variables
                user_prompt = pm.get_user_prompt(
                    "translation",
                    word="hello",
                    from_language="English",
                    to_language="Spanish",
                    extra_var="ignored",
                )
                assert "hello" in user_prompt

    @pytest.mark.unit
    def test_invalid_yaml_content(self):
        """Test prompt manager with invalid YAML content."""
        invalid_yaml = "invalid: yaml: content: ["

        with patch("src.prompt_manager.Path") as mock_path:
            mock_path.return_value.exists.return_value = True

            with patch("builtins.open", mock_open(read_data=invalid_yaml)):
                with pytest.raises(Exception):  # Should raise YAML parsing error
                    PromptManager("invalid.yaml")

    @pytest.mark.unit
    def test_missing_required_sections(self):
        """Test prompt manager with missing required sections."""
        minimal_yaml = """
openai:
  model: "gpt-4o-mini"
# Missing prompts section
"""

        with patch("src.prompt_manager.Path") as mock_path:
            mock_path.return_value.exists.return_value = True

            with patch("builtins.open", mock_open(read_data=minimal_yaml)):
                pm = PromptManager("minimal.yaml")

                # Should handle missing sections gracefully
                assert pm.openai_config is not None
                # prompts might be None or empty dict
                prompt_types = pm.list_prompt_types()
                assert isinstance(prompt_types, list)

    @pytest.mark.unit
    def test_config_inheritance(self, temp_prompts_file):
        """Test that prompt-specific config inherits from global config."""
        with patch("src.prompt_manager.Path") as mock_path:
            mock_path.return_value.exists.return_value = True

            with patch("builtins.open", mock_open(read_data=open(temp_prompts_file).read())):
                pm = PromptManager(temp_prompts_file)

                # translation has specific temperature but should inherit model
                config = pm.get_openai_config("translation")
                assert config["temperature"] == 0.3  # Specific
                assert config["model"] == "gpt-4o-mini"  # Inherited

                # language_detection only has specific temperature
                config = pm.get_openai_config("language_detection")
                assert config["temperature"] == 0.1  # Specific
                assert config["model"] == "gpt-4o-mini"  # Inherited
