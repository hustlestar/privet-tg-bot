"""Vocabulary callback handlers for the Learn Words bot."""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from ..keyboards import get_continue_keyboard
from ..vocabulary_handlers import VocabularyHandler, handle_vocabulary_callback
from ...database import db
from ...local.localization import localization

logger = logging.getLogger(__name__)


async def handle_vocabulary_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle vocabulary-related callbacks."""
    query = update.callback_query
    data = query.data

    if (
        data.startswith(("vocab_page_", "vocab_sort_", "vocab_edit_on_", "vocab_edit_off_"))
        or data == "view_vocabulary"
    ):
        await handle_vocabulary_callback(update, context)
    elif data.startswith("delete_word_"):
        await handle_delete_word(update, context)


async def handle_delete_word(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle deleting a word from user's vocabulary during training or from the vocabulary list."""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    user = await db.get_user(user_id)
    interface_lang = user.interface_language if user else "english"

    parts = query.data.split("_")
    source = parts[2]

    if source == "train":
        # Deletion from a training session
        word_id = int(parts[3])
        success = await db.hide_word_for_user(user_id, word_id)
        if success:
            word_info = await db.word_dao.get_word_by_id(word_id)
            word_text = f"<b>{word_info.word}</b>" if word_info else "The word"
            success_text = localization.get_text(interface_lang, "word_hidden_success").format(word=word_text)
            await context.bot.send_message(
                chat_id=query.message.chat_id, text=success_text, parse_mode="HTML"
            )
            
            # Mark the word in the training message
            keyboard = get_continue_keyboard(is_correct=False, interface_lang=interface_lang, word=word_id)
            await query.edit_message_text(f"⚠️ {query.message.text} ⚠️", reply_markup=keyboard)
        else:
            error_text = localization.get_text(interface_lang, "word_hidden_error")
            await query.edit_message_text(f"❌ {error_text}")

    elif source == "vocab":
        # Deletion from the vocabulary edit mode
        word_id = int(parts[3])
        page = int(parts[4])
        sort_recent = parts[5] == "True"

        # Fetch word details for the confirmation message before deleting
        word_info = await db.word_dao.get_word_by_id(word_id)
        
        success = await db.hide_word_for_user(user_id, word_id)

        if success and word_info:
            # Send a confirmation message
            word_text = f"<b>{word_info.word}</b>"
            success_text = localization.get_text(interface_lang, "word_hidden_success").format(
                word=word_text
            )
            await context.bot.send_message(
                chat_id=query.message.chat_id, text=success_text, parse_mode="HTML"
            )
           
            # Refresh the vocabulary view
            await VocabularyHandler.show_vocabulary(
                update, context, page=page, sort_recent=sort_recent, edit_mode=True
            )
        else:
            # If deletion fails, just show the vocabulary again without changes
            error_text = localization.get_text(interface_lang, "word_hidden_error")
            await context.bot.send_message(chat_id=query.message.chat_id, text=error_text)
            await VocabularyHandler.show_vocabulary(
                update, context, page=page, sort_recent=sort_recent, edit_mode=True
            )
    elif source == "translate":
        word_id = int(parts[3])
        success = await db.hide_word_for_user(user_id, word_id)
        if success:
            word_info = await db.word_dao.get_word_by_id(word_id)
            word_text = f"<b>{word_info.word}</b>" if word_info else "The word"
            success_text = localization.get_text(interface_lang, "word_hidden_success").format(word=word_text)
            await context.bot.send_message(
                chat_id=query.message.chat_id, text=success_text, parse_mode="HTML"
            )

            await query.edit_message_text(f"⚠️ {query.message.text} ⚠️", reply_markup=None)
        else:
            error_text = localization.get_text(interface_lang, "word_hidden_error")
            await query.edit_message_text(f"❌ {error_text}")
