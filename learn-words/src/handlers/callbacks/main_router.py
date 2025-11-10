"""Main callback query router for the Learn Words bot."""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from .language_callbacks import handle_language_callbacks
from .menu_callbacks import handle_menu_callbacks
from .sentence_callbacks import handle_sentence_callbacks
from .settings_callbacks import handle_settings_callbacks
from .training_callbacks import handle_training_callbacks
from .translation_callbacks import handle_translation_callbacks
from .vocabulary_callbacks import handle_vocabulary_callbacks
from .notification_callbacks import (
    handle_confirm_repetition,
    handle_start_review,
    handle_notification_settings,
    handle_set_notification_time,
    handle_remove_notification_time,
    handle_set_timezone,
)
from ..command_handlers import explanation_command_callback

logger = logging.getLogger(__name__)


async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Main callback query router that dispatches to appropriate handlers."""
    query = update.callback_query
    await query.answer()

    data = query.data

    try:
        # Language selection callbacks
        if data.startswith(("native_lang_", "learning_lang_")):
            await handle_language_callbacks(update, context)
            return

        # Menu and navigation callbacks
        if data in ("main_menu", "cancel_selection"):
            await handle_menu_callbacks(update, context)
            return

        if data == "settings_notifications_settings":
            await handle_notification_settings(query, context)
            return

        # Settings callbacks
        if data.startswith(
            (
                "mode_",
                "set_mode_",
                "set_explanation_",
                "settings_",
                "set_interface_lang_",
                "set_learning_lang_",
            )
        ):
            await handle_settings_callbacks(update, context)
            return

        # Training callbacks
        if data.startswith(("answer_", "known_", "mark_correct", "idk_")) or data in (
            "train_start",
            "train_continue",
            "train_stop",
        ):
            await handle_training_callbacks(update, context)
            return

        # Translation direction callbacks
        if data.startswith("translate_") and "_to_" in data:
            await handle_translation_callbacks(update, context)
            return

        # Sentence parsing callbacks
        if data.startswith(("parse_sentence_", "add_word_", "sentence_word_", "sentence_done_")) or data in (
            "finish_sentence_selection",
            "cancel_selection",
        ):
            await handle_sentence_callbacks(update, context)
            return

        # Vocabulary callbacks
        if (
            data.startswith(("vocab_page_", "vocab_sort_", "delete_word_", "vocab_edit_"))
            or data == "view_vocabulary"
        ):
            await handle_vocabulary_callbacks(update, context)
            return

        # Command callbacks (stats, settings, explanation)
        if data in ("show_stats", "show_settings"):
            await handle_menu_callbacks(update, context)
            return

        if data == "explanation_command":
            await explanation_command_callback(query, context)
            return

        # Notification callbacks
        if data.startswith("confirm_repetition_"):
            await handle_confirm_repetition(update, context)
            return

        if data.startswith("set_notification_time_"):
            await handle_set_notification_time(query, context)
            return

        if data.startswith("start_review_"):
            await handle_start_review(update, context)
            return

        if data.startswith("remove_notification_time_"):
            await handle_remove_notification_time(query, context)
            return

        if data.startswith("set_timezone_"):
            await handle_set_timezone(query, context)
            return

        # Unknown callback
        logger.warning(f"Unknown callback data: {data}")
        await query.edit_message_text("Unknown action. Please try again.")

    except Exception as e:
        logger.error(f"Error handling callback query {data}: {e}")
        await query.edit_message_text("An error occurred. Please try again.")
