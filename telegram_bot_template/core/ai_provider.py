"""OpenRouter AI provider for the Telegram bot template."""

import logging
from typing import Optional, Dict, Any
import aiohttp
import json
import asyncio

logger = logging.getLogger(__name__)


class OpenRouterProvider:
    """OpenRouter AI provider for chat completions."""

    def __init__(self, api_key: str, model: str = "openai/gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/telegram-bot-template",
            "X-Title": "Telegram Bot Template",
        }

        logger.info(f"OpenRouter provider initialized with model: {model}")

    async def get_completion(self, prompt: str) -> str:
        """Get completion for a prompt (alias for compatibility).
        
        Args:
            prompt: The prompt text
            
        Returns:
            AI response string
        """
        return await self.get_response(prompt)

    async def get_response(self, message: str, user_id: Optional[int] = None, system_prompt: Optional[str] = None) -> str:
        """Get AI response for a user message with retry logic.

        Args:
            message: User's message
            user_id: Optional user ID for tracking
            system_prompt: Optional system prompt to customize behavior

        Returns:
            AI response string
        """
        max_retries = 3
        retry_delay = 2  # Start with 2 seconds
        
        for attempt in range(max_retries):
            try:
                messages = []

                # Add system prompt if provided
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                else:
                    messages.append({"role": "system", "content": "You are a helpful assistant. Respond in a friendly and informative way."})

                # Add user message
                messages.append({"role": "user", "content": message})

                payload = {
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": 1000,
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "frequency_penalty": 0.0,
                    "presence_penalty": 0.0,
                }

                # Increase timeout for retries
                timeout = 30 + (attempt * 10)  # 30s, 40s, 50s
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.base_url}/chat/completions", 
                        headers=self.headers, 
                        json=payload, 
                        timeout=aiohttp.ClientTimeout(total=timeout)
                    ) as response:

                        if response.status == 200:
                            data = await response.json()

                            if "choices" in data and len(data["choices"]) > 0:
                                content = data["choices"][0]["message"]["content"]

                                # Log usage if available
                                if "usage" in data:
                                    usage = data["usage"]
                                    logger.debug(
                                        f"OpenRouter usage - Prompt: {usage.get('prompt_tokens', 0)}, "
                                        f"Completion: {usage.get('completion_tokens', 0)}, "
                                        f"Total: {usage.get('total_tokens', 0)}"
                                    )

                                return content.strip()
                            else:
                                logger.error("No choices in OpenRouter response")
                                return "I'm sorry, I couldn't generate a response."

                        elif response.status == 429:  # Rate limit - worth retrying
                            if attempt < max_retries - 1:
                                wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                                logger.warning(f"Rate limited, retrying in {wait_time}s...")
                                await asyncio.sleep(wait_time)
                                continue
                            else:
                                return "AI service is currently busy. Please try again in a moment."
                                
                        elif response.status >= 500:  # Server error - worth retrying
                            if attempt < max_retries - 1:
                                wait_time = retry_delay * (2 ** attempt)
                                logger.warning(f"Server error {response.status}, retrying in {wait_time}s...")
                                await asyncio.sleep(wait_time)
                                continue
                            else:
                                return "AI service is temporarily unavailable. Please try again later."
                        
                        elif response.status == 401:
                            # Don't retry authentication errors
                            return "AI service authentication failed. Please check the API key."
                        else:
                            error_text = await response.text()
                            logger.error(f"OpenRouter API error {response.status}: {error_text}")
                            return "I'm having trouble processing your request right now."

            except aiohttp.ClientTimeout:
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)
                    logger.warning(f"Request timeout on attempt {attempt + 1}, retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    logger.error(f"OpenRouter request timeout after {max_retries} attempts")
                    return "The AI service is taking too long to respond. Please try again."

            except aiohttp.ClientConnectorError as e:
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)
                    logger.warning(f"Connection error on attempt {attempt + 1}: {e}. Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    logger.error(f"Connection error after {max_retries} attempts: {e}")
                    return "Unable to connect to AI service. Please check your internet connection."

            except Exception as e:
                logger.error(f"OpenRouter error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    continue
                else:
                    return "I encountered an error while processing your message. Please try again."
        
        # Should not reach here, but just in case
        return "I'm having trouble processing your request. Please try again."

    async def get_streaming_response(self, message: str, user_id: Optional[int] = None, system_prompt: Optional[str] = None):
        """Get streaming AI response (generator).

        Args:
            message: User's message
            user_id: Optional user ID for tracking
            system_prompt: Optional system prompt to customize behavior

        Yields:
            Chunks of AI response
        """
        try:
            messages = []

            # Add system prompt if provided
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            else:
                messages.append({"role": "system", "content": "You are a helpful assistant. Respond in a friendly and informative way."})

            # Add user message
            messages.append({"role": "user", "content": message})

            payload = {"model": self.model, "messages": messages, "max_tokens": 1000, "temperature": 0.7, "stream": True}

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions", headers=self.headers, json=payload, timeout=aiohttp.ClientTimeout(total=60)
                ) as response:

                    if response.status == 200:
                        async for line in response.content:
                            line = line.decode("utf-8").strip()

                            if line.startswith("data: "):
                                data_str = line[6:]  # Remove 'data: ' prefix

                                if data_str == "[DONE]":
                                    break

                                try:
                                    data = json.loads(data_str)
                                    if "choices" in data and len(data["choices"]) > 0:
                                        delta = data["choices"][0].get("delta", {})
                                        if "content" in delta:
                                            yield delta["content"]
                                except json.JSONDecodeError:
                                    continue
                    else:
                        error_text = await response.text()
                        logger.error(f"OpenRouter streaming error {response.status}: {error_text}")
                        yield "Error: Unable to get streaming response."

        except Exception as e:
            logger.error(f"OpenRouter streaming error: {e}")
            yield "Error: Streaming response failed."

    async def get_models(self) -> Dict[str, Any]:
        """Get available models from OpenRouter.

        Returns:
            Dictionary with model information
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/models", headers=self.headers, timeout=aiohttp.ClientTimeout(total=10)
                ) as response:

                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        logger.error(f"Failed to get models: {response.status}")
                        return {"error": f"HTTP {response.status}"}

        except Exception as e:
            logger.error(f"Error getting models: {e}")
            return {"error": str(e)}

    def is_available(self) -> bool:
        """Check if the AI provider is properly configured."""
        return bool(self.api_key and self.model)

    def get_model_info(self) -> Dict[str, str]:
        """Get current model information."""
        return {"provider": "OpenRouter", "model": self.model, "base_url": self.base_url}

    async def test_connection(self) -> bool:
        """Test the connection to OpenRouter API.

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            test_message = "Hello"
            response = await self.get_response(test_message)
            return not response.startswith("Error:") and not response.startswith("AI service")

        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False


class MockAIProvider:
    """Mock AI provider for testing without API calls."""

    def __init__(self):
        self.model = "mock-model"
        logger.info("Mock AI provider initialized")

    async def get_response(self, message: str, user_id: Optional[int] = None, system_prompt: Optional[str] = None) -> str:
        """Return a mock response."""
        return f"Mock response to: {message[:50]}{'...' if len(message) > 50 else ''}"

    async def get_streaming_response(self, message: str, user_id: Optional[int] = None, system_prompt: Optional[str] = None):
        """Return a mock streaming response."""
        mock_response = f"Mock streaming response to: {message}"
        for word in mock_response.split():
            yield word + " "

    def is_available(self) -> bool:
        """Mock provider is always available."""
        return True

    def get_model_info(self) -> Dict[str, str]:
        """Get mock model information."""
        return {"provider": "Mock", "model": self.model, "base_url": "mock://localhost"}

    async def test_connection(self) -> bool:
        """Mock connection test always succeeds."""
        return True
