"""Translation direction callback handlers for the Learn Words bot."""

import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from src.local.localization import localization
from src.translation.translator import translator
from ..utils import save_word
from ...database import db
from ...explanation_formatter import explanation_formatter

logger = logging.getLogger(__name__)


async def handle_translation_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle translation direction callbacks."""
    query = update.callback_query
    data = query.data

    if data.startswith("translate_") and "_to_" in data:
        # Handle translation direction selection
        parts = data.split("_")
        word = "_".join(parts[1:-2])  # Reconstruct word (may contain underscores)
        direction = parts[-1]  # "learning" or "native"
        await handle_translation_direction(query, context, word, direction)


async def handle_translation_direction(query, context, word: str, direction: str) -> None:
    """Handle translation direction selection for ambiguous words."""
    user_id = query.from_user.id

    try:
        user = await db.get_user(user_id)
        if not user:
            await query.edit_message_text("Please start with /start first!")
            return

        interface_lang = user.interface_language

        if direction == "learning":
            source_lang = user.interface_language
            target_lang = user.learning_language
        elif direction == "native":
            source_lang = user.learning_language
            target_lang = user.interface_language
        else:
            invalid_direction_text = localization.get_text(interface_lang, "invalid_direction")
            await query.edit_message_text(f"❌ {invalid_direction_text}")
            return

        # Get translation
        # Use the learning language as the native_language
        translation_data = await translator.translate_word(word, source_lang, target_lang, user.interface_language)

        if translation_data is None:
            # This shouldn't happen in direction callbacks since direction is already determined
            # But handle it gracefully
            translation_failed_text = localization.get_text(interface_lang, "translation_failed")
            await query.edit_message_text(f"❌ {translation_failed_text}")
            return

        word_id, cached_word = await save_word(
            translation_data,
            translation_data.from_language,
            translation_data.to_language,
            user,
        )

        await db.add_word_to_user_vocabulary(user.user_id, word_id)

        word_dict = {
            "word": cached_word.word,
            "short_translation": cached_word.short_translation,
            "medium_data": cached_word.medium_data,
            "long_data": cached_word.long_data,
            "synonyms_native": cached_word.synonyms_native or [],
            "synonyms_learning": cached_word.synonyms_learning or [],
        }

        direction_info = f"🔄 <b>{source_lang} -> {target_lang}</b>\n\n"
        formatted_response = explanation_formatter.format_explanation(word_dict, user, user.response_mode.value)
        response_text = direction_info + formatted_response

        mark_known_text = localization.get_text(user.interface_language, "mark_as_known")
        keyboard = [
            [InlineKeyboardButton(mark_known_text, callback_data=f"known_{word_id}")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(response_text, reply_markup=reply_markup, parse_mode="HTML")

    except Exception as e:
        logger.error(f"Error handling translation direction: {e}")

        user = await db.get_user(user_id)
        interface_lang = user.interface_language if user else "english"

        error_occurred_text = localization.get_text(interface_lang, "error_occurred")
        await query.edit_message_text(f"❌ {error_occurred_text}")
