"""Prompt management system for OpenAI API calls."""

import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from string import Template

logger = logging.getLogger(__name__)


class PromptManager:
    """Manages prompts and OpenAI configuration from YAML file."""

    def __init__(self, config_path: str = "prompts.yaml"):
        """Initialize the prompt manager with configuration file."""
        # Make path relative to this file's directory
        self.config_path = Path(__file__).parent / config_path
        self.config = self._load_config()

        # Extract main sections
        self.prompts = self.config.get("prompts", {})
        self.openai_config = self.config.get("openai", {})
        self.fallback_config = self.config.get("fallback", {})

        logger.info(f"PromptManager initialized with {len(self.prompts)} prompt templates")

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, "r", encoding="utf-8") as file:
                config = yaml.safe_load(file)
                logger.debug(f"Loaded prompt configuration from {self.config_path}")
                return config
        except FileNotFoundError:
            logger.error(f"Prompt configuration file not found: {self.config_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML configuration: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading prompt configuration: {e}")
            raise

    def get_system_prompt(self, prompt_type: str) -> str:
        """Get system prompt for a specific prompt type."""
        if prompt_type not in self.prompts:
            raise ValueError(f"Unknown prompt type: {prompt_type}")

        return self.prompts[prompt_type].get("system", "")

    def get_user_prompt(self, prompt_type: str, **kwargs) -> str:
        """Get user prompt with variable substitution."""
        if prompt_type not in self.prompts:
            raise ValueError(f"Unknown prompt type: {prompt_type}")

        template_str = self.prompts[prompt_type].get("user_template", "")
        if not template_str:
            raise ValueError(f"No user template found for prompt type: {prompt_type}")

        try:
            # Use string formatting for variable substitution
            return template_str.format(**kwargs)
        except KeyError as e:
            logger.error(f"Missing required variable {e} for prompt type {prompt_type}")
            raise ValueError(f"Missing required variable {e} for prompt type {prompt_type}")
        except Exception as e:
            logger.error(f"Error formatting prompt template for {prompt_type}: {e}")
            raise ValueError(f"Error formatting prompt template: {e}")

    def get_fallback_config(self, config_type: str) -> Any:
        """Get fallback configuration."""
        return self.fallback_config.get(config_type, [])

    def get_stop_words(self) -> list[str]:
        """Get stop words for sentence parsing fallback."""
        return self.get_fallback_config("stop_words")

    def reload_config(self) -> None:
        """Reload configuration from file."""
        logger.info("Reloading prompt configuration")
        self.config = self._load_config()
        self.prompts = self.config.get("prompts", {})
        self.openai_config = self.config.get("openai", {})
        self.fallback_config = self.config.get("fallback", {})
        logger.info(f"Configuration reloaded with {len(self.prompts)} prompt templates")

    def validate_prompt_type(self, prompt_type: str) -> bool:
        """Validate if prompt type exists."""
        return prompt_type in self.prompts

    def list_prompt_types(self) -> list[str]:
        """List all available prompt types."""
        return list(self.prompts.keys())


# Global prompt manager instance
prompt_manager = PromptManager()
