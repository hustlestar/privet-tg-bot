"""Handler for processing voice messages in Telegram."""

import logging
import tempfile
import os
import json
import asyncio
from typing import Optional
from io import BytesIO

from telegram import Update, Voice
from telegram.ext import ContextTypes
from telegram.error import TimedOut, BadRequest

from telegram_bot_template.core.database import DatabaseManager
from telegram_bot_template.dao.user_dao import UserDAO
from telegram_bot_template.dao.conversation_message_dao import ConversationMessageDAO
from telegram_bot_template.services.audio_service import AudioService
from telegram_bot_template.services.rag_service import RAGService
from telegram_bot_template.services.conversation_manager import ConversationManager
from telegram_bot_template.services.nlp_service import NLPService
from telegram_bot_template.config.settings import BotConfig
from telegram_bot_template.core.locale_manager import LocaleManager
from telegram_bot_template.core.ai_provider import OpenRouterProvider

logger = logging.getLogger(__name__)


class VoiceHandler:
    """Handles voice message processing and responses with full AI companion features."""

    def __init__(
        self,
        database_manager: DatabaseManager,
        audio_service: AudioService,
        config: BotConfig,
        locale_manager: LocaleManager,
        ai_provider: Optional[OpenRouterProvider] = None,
    ):
        """Initialize the voice handler with all services.
        
        Args:
            database_manager: Database connection manager
            audio_service: Service for STT and TTS operations
            config: Bot configuration
            locale_manager: Locale manager for translations
            ai_provider: AI provider for LLM calls
        """
        self.db = database_manager
        self.audio_service = audio_service
        self.config = config
        self.locale_manager = locale_manager
        self.user_dao = UserDAO(database_manager.pool)
        self.message_dao = ConversationMessageDAO(database_manager.pool)
        
        # Initialize advanced services
        self.nlp_service = NLPService()
        # Use OpenAI embeddings with proper dimension
        self.rag_service = RAGService(
            database_pool=database_manager.pool,
            openai_api_key=config.openai_api_key,
            embedding_model="text-embedding-3-small",
            embedding_dimension=1536  # OpenAI's text-embedding-3-small dimension
        )
        self.conversation_manager = ConversationManager(
            database_manager=database_manager,
            rag_service=self.rag_service,
            ai_provider=ai_provider,
            config=config,
        )

    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Process an incoming voice message.
        
        Args:
            update: The Telegram update object
            context: The callback context
        """
        message = update.message
        if not message or not message.voice:
            return

        voice = message.voice
        user_id = message.from_user.id
        
        try:
            # Send typing action to show bot is processing
            await context.bot.send_chat_action(
                chat_id=message.chat_id,
                action="typing"
            )
            
            # Ensure user exists in database
            user = await self.user_dao.get_user(user_id)
            if not user:
                await self.user_dao.create_user(
                    user_id=user_id,
                    username=message.from_user.username or str(user_id),
                    language=message.from_user.language_code or self.config.default_language,
                )
                logger.info(f"Created new user: {user_id}")
            
            # Download voice file with retry logic
            max_retries = 3
            retry_delay = 2
            voice_bytes = None
            
            for attempt in range(max_retries):
                try:
                    # Increase timeout for file download
                    voice_file = await context.bot.get_file(
                        voice.file_id,
                        read_timeout=30,
                        write_timeout=30
                    )
                    voice_bytes = BytesIO()
                    await voice_file.download_to_memory(voice_bytes)
                    voice_bytes.seek(0)
                    break
                except TimedOut as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"Attempt {attempt + 1} timed out downloading voice: {e}. Retrying...")
                        await asyncio.sleep(retry_delay)
                    else:
                        logger.error(f"Failed to download voice after {max_retries} attempts")
                        raise
            
            if not voice_bytes:
                await message.reply_text(
                    "❌ Failed to download your voice message. "
                    "Please try again with a shorter message."
                )
                return
            
            # Save to temporary file for processing
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".ogg"
            ) as tmp_file:
                tmp_file.write(voice_bytes.read())
                tmp_file_path = tmp_file.name
            
            try:
                # Transcribe the voice message
                transcribed_text = await self.audio_service.transcribe_voice(tmp_file_path)
                
                if not transcribed_text:
                    await message.reply_text(
                        "🎤 Sorry, I couldn't transcribe your voice message. "
                        "Please try again or check if the audio is clear."
                    )
                    return
                
                # Analyze emotion and sentiment
                emotion_analysis = await self.nlp_service.analyze_emotion(transcribed_text)
                
                # Store the message in database
                raw_message_data = {
                    "message_id": message.message_id,
                    "chat_id": message.chat_id,
                    "voice_duration": voice.duration,
                    "voice_file_id": voice.file_id,
                }
                
                stored_message = await self.message_dao.create_message(
                    user_id=user_id,
                    message_text=None,  # No text message, only voice
                    transcribed_text=transcribed_text,
                    sentiment_score=emotion_analysis.sentiment_score,
                    raw_telegram_message=raw_message_data,
                )
                
                logger.info(
                    f"Stored voice message {stored_message['id']} "
                    f"for user {user_id}: {transcribed_text[:50]}... "
                    f"Emotion: {emotion_analysis.primary_emotion.value}"
                )
                
                # Process message through conversation manager for intelligent response
                ai_response = await self.conversation_manager.process_message(
                    user_id=user_id,
                    message_text=transcribed_text,
                    sentiment_score=emotion_analysis.sentiment_score,
                    is_voice=True,
                )
                
                # Send text response first (for quick feedback)
                await message.reply_text(ai_response)
                
                # Generate emotionally-aware voice response
                audio_response = await self.audio_service.text_to_speech(
                    text=ai_response,
                    emotion=emotion_analysis.voice_tone_suggestion,
                    intensity=emotion_analysis.intensity,
                )
                
                if audio_response:
                    # Try to send voice response with fallback
                    try:
                        await message.reply_voice(
                            voice=audio_response,
                            caption="🎙️ Voice response",
                            read_timeout=30,
                            write_timeout=30
                        )
                        logger.info(f"Sent voice response to user {user_id}")
                    except BadRequest as e:
                        if "Voice_messages_forbidden" in str(e):
                            logger.warning(
                                f"Voice messages forbidden for user {user_id}. "
                                "Falling back to text-only response."
                            )
                            # The text response was already sent above
                        else:
                            raise
                    except TimedOut:
                        logger.warning(
                            f"Timeout sending voice to user {user_id}. "
                            "User already received text response."
                        )
                else:
                    logger.warning(f"Could not generate voice response for user {user_id}")
                
            finally:
                # Clean up temporary file
                if os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)
                    
        except Exception as e:
            logger.error(f"Error processing voice message: {e}", exc_info=True)
            await message.reply_text(
                "❌ Sorry, I encountered an error processing your voice message. "
                "Please try again later."
            )