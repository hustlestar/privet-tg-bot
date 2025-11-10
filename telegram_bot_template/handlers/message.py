"""Message handler for the Telegram bot template."""

import logging
import os
from typing import Optional

from telegram import Update
from telegram.ext import ContextTypes

from telegram_bot_template.core.ai_provider import OpenRouterProvider
from telegram_bot_template.dao.user_dao import UserDAO
from telegram_bot_template.core.keyboard_manager import KeyboardManager
from telegram_bot_template.core.locale_manager import LocaleManager
from telegram_bot_template.services.audio_service import AudioService

logger = logging.getLogger(__name__)


class MessageHandler:
    """Handles text messages from users."""

    def __init__(
        self,
        locale_manager: LocaleManager,
        keyboard_manager: KeyboardManager,
        user_dao: UserDAO,
        ai_provider: Optional[OpenRouterProvider],
        audio_service: Optional[AudioService],
        config,
    ):
        self.locale_manager = locale_manager
        self.keyboard_manager = keyboard_manager
        self.user_dao = user_dao
        self.ai_provider = ai_provider
        self.audio_service = audio_service
        self.config = config

    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle incoming text messages."""
        user = update.effective_user
        message = update.message

        if not user or not message or not message.text:
            return

        try:
            # Ensure user exists in database
            user_data = await self.user_dao.ensure_user(user_id=user.id, username=user.username, language=self.config.default_language)

            user_language = user_data.get("language", self.config.default_language)
            user_message = message.text.strip()

            logger.info(f"User {user.id} (@{user.username}) sent: {user_message[:100]}...")

            # Check if AI is available
            if self.ai_provider and self.ai_provider.is_available():
                await self._handle_ai_message(update, user_message, user_language, user.id)
            else:
                await self._handle_simple_echo(update, user_message, user_language)

        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await message.reply_text(self.locale_manager.get("error_occurred", user_language))

    async def _handle_ai_message(self, update: Update, user_message: str, user_language: str, user_id: int) -> None:
        """Handle message with AI response."""
        message = update.message

        try:
            # Send "processing" message
            processing_msg = await message.reply_text(self.locale_manager.get("processing", user_language), do_quote=True)

            # Get AI response
            system_prompt = self._get_system_prompt(user_language)
            ai_response = await self.ai_provider.get_response(message=user_message, user_id=user_id, system_prompt=system_prompt)

            # Delete processing message
            await processing_msg.delete()

            # Send AI response
            await message.reply_text(ai_response, do_quote=True, parse_mode="Markdown")

            logger.info(f"AI response sent to user {user_id}")

        except Exception as e:
            logger.error(f"Error getting AI response: {e}")

            # Try to delete processing message
            try:
                await processing_msg.delete()
            except:
                pass

            # Send error message
            await message.reply_text(self.locale_manager.get("ai_not_available", user_language), do_quote=True)

    async def _handle_simple_echo(self, update: Update, user_message: str, user_language: str) -> None:
        """Handle message with simple echo response."""
        message = update.message

        try:
            # Simple echo response
            echo_response = f"You said: {user_message}"

            # Add main menu keyboard
            keyboard = self.keyboard_manager.get_main_menu_keyboard(user_language)

            await message.reply_text(echo_response, reply_markup=keyboard, do_quote=True)

        except Exception as e:
            logger.error(f"Error in echo response: {e}")
            await message.reply_text(self.locale_manager.get("error_occurred", user_language))

    def _get_system_prompt(self, language: str) -> str:
        """Get system prompt based on user language."""
        prompts = {
            "en": "You are a helpful assistant. Respond in a friendly and informative way in English.",
            "ru": "Ты полезный помощник. Отвечай дружелюбно и информативно на русском языке.",
            "es": "Eres un asistente útil. Responde de manera amigable e informativa en español.",
        }

        return prompts.get(language, prompts["en"])

    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle photo messages."""
        user = update.effective_user
        message = update.message

        if not user or not message:
            return

        try:
            user_language = await self.user_dao.get_user_language(user.id)

            # Simple response for photos
            await message.reply_text("📸 I received your photo! Unfortunately, I can't process images yet.", do_quote=True)

            logger.info(f"User {user.id} sent a photo")

        except Exception as e:
            logger.error(f"Error handling photo: {e}")

    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle document messages."""
        user = update.effective_user
        message = update.message

        if not user or not message:
            return

        try:
            user_language = await self.user_dao.get_user_language(user.id)

            # Simple response for documents
            await message.reply_text("📄 I received your document! Unfortunately, I can't process files yet.", do_quote=True)

            logger.info(f"User {user.id} sent a document")

        except Exception as e:
            logger.error(f"Error handling document: {e}")

    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle voice messages."""
        user = update.effective_user
        message = update.message

        if not user or not message:
            return

        try:
            user_language = await self.user_dao.get_user_language(user.id)
            if not self.audio_service:
                await message.reply_text("Audio processing is not available.", do_quote=True)
                return

            # 1. Download the voice message
            voice_file = await message.voice.get_file()
            os.makedirs("/tmp/voices", exist_ok=True)
            voice_file_path = f"/tmp/voices/{voice_file.file_id}.ogg"
            await voice_file.download_to_drive(voice_file_path)

            # 2. Transcribe the voice message
            transcribed_text = await self.audio_service.transcribe_voice(voice_file_path)

            if not transcribed_text:
                await message.reply_text("Sorry, I could not understand the audio.", do_quote=True)
                return

            # 3. Echo the transcribed text
            await message.reply_text(f"You said: \"{transcribed_text}\"", do_quote=True)

            # 4. Get a response (for now, just a simple echo)
            response_text = f"I heard you say: {transcribed_text}"

            # 5. Synthesize the response back to voice
            audio_bytes = await self.audio_service.text_to_speech(response_text)

            if audio_bytes:
                await message.reply_voice(voice=audio_bytes, do_quote=True)
            else:
                await message.reply_text("Sorry, I could not generate a voice response.", do_quote=True)

            logger.info(f"User {user.id} sent a voice message, transcribed as: {transcribed_text}")

        except Exception as e:
            logger.error(f"Error handling voice: {e}", exc_info=True)
            await message.reply_text("Sorry, an error occurred while processing your voice message.")

    async def handle_sticker(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle sticker messages."""
        user = update.effective_user
        message = update.message

        if not user or not message:
            return

        try:
            user_language = await self.user_dao.get_user_language(user.id)

            # Fun response for stickers
            sticker_responses = ["😄 Nice sticker!", "🎉 I love stickers!", "😊 That's a cool sticker!", "👍 Great choice!"]

            import random

            response = random.choice(sticker_responses)

            await message.reply_text(response, do_quote=True)

            logger.info(f"User {user.id} sent a sticker")

        except Exception as e:
            logger.error(f"Error handling sticker: {e}")

    async def handle_location(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle location messages."""
        user = update.effective_user
        message = update.message

        if not user or not message:
            return

        try:
            user_language = await self.user_dao.get_user_language(user.id)
            location = message.location

            response = f"📍 Thanks for sharing your location!\n"
            response += f"Latitude: {location.latitude}\n"
            response += f"Longitude: {location.longitude}"

            await message.reply_text(response, do_quote=True)

            logger.info(f"User {user.id} sent location: {location.latitude}, {location.longitude}")

        except Exception as e:
            logger.error(f"Error handling location: {e}")

    async def handle_contact(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle contact messages."""
        user = update.effective_user
        message = update.message

        if not user or not message:
            return

        try:
            user_language = await self.user_dao.get_user_language(user.id)
            contact = message.contact

            response = f"👤 Thanks for sharing the contact!\n"
            response += f"Name: {contact.first_name}"
            if contact.last_name:
                response += f" {contact.last_name}"
            if contact.phone_number:
                response += f"\nPhone: {contact.phone_number}"

            await message.reply_text(response, do_quote=True)

            logger.info(f"User {user.id} sent contact: {contact.first_name}")

        except Exception as e:
            logger.error(f"Error handling contact: {e}")
