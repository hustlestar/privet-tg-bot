"""Vocabulary browsing handlers for the Learn Words bot."""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from collections import defaultdict

from ..database import db
from src.local.localization import localization

logger = logging.getLogger(__name__)

WORDS_PER_PAGE = 20


class VocabularyHandler:
    """Handle vocabulary browsing functionality."""

    @staticmethod
    async def show_vocabulary(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        page: int = 1,
        sort_recent: bool = True,
        edit_mode: bool = False,
    ) -> None:
        """Show user's vocabulary with pagination."""
        try:
            user_id = update.effective_user.id
            user = await db.get_user(user_id)

            if not user:
                await update.callback_query.answer("User not found")
                return

            # Get total word count
            total_words = await db.get_user_vocabulary_count(user_id)

            if total_words == 0:
                # No words in vocabulary
                no_words_text = localization.get_text(user.interface_language, "no_words")
                main_menu_text = localization.get_text(user.interface_language, "main_menu")

                keyboard = [[InlineKeyboardButton(main_menu_text, callback_data="main_menu")]]
                reply_markup = InlineKeyboardMarkup(keyboard)

                if update.callback_query:
                    await update.callback_query.edit_message_text(no_words_text, reply_markup=reply_markup)
                else:
                    await update.message.reply_text(no_words_text, reply_markup=reply_markup)
                return

            # Calculate pagination
            total_pages = (total_words + WORDS_PER_PAGE - 1) // WORDS_PER_PAGE
            page = max(1, min(page, total_pages))
            offset = (page - 1) * WORDS_PER_PAGE

            # Get vocabulary words with stats
            words_data = await db.get_user_vocabulary_with_stats(
                user_id, limit=WORDS_PER_PAGE, offset=offset, sort_recent=sort_recent
            )

            if edit_mode:
                vocabulary_title = localization.get_text(user.interface_language, "vocabulary_edit_title")
            else:
                vocabulary_title = localization.get_text(user.interface_language, "vocabulary_title")

            page_indicator = localization.get_text(
                user.interface_language, "page_indicator", current=page, total=total_pages
            )
            message_text = f"<b>{vocabulary_title}</b>\n{page_indicator}\n\n"

            keyboard = []

            if edit_mode:
                # In edit mode, show words as buttons for deletion
                word_buttons = []
                for word_data in words_data:
                    word = word_data["word"]
                    translation = word_data["translation"]
                    word_id = word_data["id"]

                    button_text = f"❌ {word} - {translation}"
                    callback_data = f"delete_word_vocab_{word_id}_{page}_{sort_recent}"
                    word_buttons.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
                keyboard.extend(word_buttons)
            else:
                # Default view: show words grouped by date
                words_by_date = defaultdict(list)
                for word_data in words_data:
                    date_added = word_data["date_added"]
                    formatted_date = (
                        date_added.strftime("%Y-%m-%d")
                        if date_added
                        else localization.get_text(user.interface_language, "unknown_date")
                    )
                    words_by_date[formatted_date].append(word_data)

                sorted_dates = sorted(words_by_date.keys(), reverse=sort_recent)

                for date in sorted_dates:
                    message_text += f"📅 <b>{date}</b>\n"
                    for word_data in words_by_date[date]:
                        word = word_data["word"]
                        translation = word_data["translation"]
                        correct = word_data["correct_answers"]
                        total = word_data["total_attempts"]
                        success_rate = round((correct / total * 100), 0) if total > 0 else 0
                        message_text += f"📝 <b>{word}</b> - {translation} ({correct}/{total}, {success_rate:.0f}%)\n"
                    message_text += "\n"

            # Create navigation keyboard
            nav_row = []
            if page > 1:
                prev_text = localization.get_text(user.interface_language, "previous")
                callback_data = f"vocab_page_{page-1}_{sort_recent}_{edit_mode}"
                nav_row.append(InlineKeyboardButton(prev_text, callback_data=callback_data))

            if page < total_pages:
                next_text = localization.get_text(user.interface_language, "next")
                callback_data = f"vocab_page_{page+1}_{sort_recent}_{edit_mode}"
                nav_row.append(InlineKeyboardButton(next_text, callback_data=callback_data))

            if nav_row:
                keyboard.append(nav_row)

            # Sort and Edit toggle row
            if sort_recent:
                sort_text = localization.get_text(user.interface_language, "sort_oldest")
                sort_callback = f"vocab_sort_{page}_False_{edit_mode}"
                keyboard.append([InlineKeyboardButton(sort_text, callback_data=sort_callback)])
            else:
                sort_text = localization.get_text(user.interface_language, "sort_recent")
                sort_callback = f"vocab_sort_{page}_True_{edit_mode}"
                keyboard.append([InlineKeyboardButton(sort_text, callback_data=sort_callback)])

            if edit_mode:
                edit_text = localization.get_text(user.interface_language, "exit_edit_mode")
                edit_callback = f"vocab_edit_off_{page}_{sort_recent}"
                keyboard.append([InlineKeyboardButton(edit_text, callback_data=edit_callback)])
            else:
                edit_text = localization.get_text(user.interface_language, "edit_vocabulary")
                edit_callback = f"vocab_edit_on_{page}_{sort_recent}"
                keyboard.append([InlineKeyboardButton(edit_text, callback_data=edit_callback)])

            main_menu_text = localization.get_text(user.interface_language, "main_menu")
            keyboard.append([InlineKeyboardButton(main_menu_text, callback_data="main_menu")])

            reply_markup = InlineKeyboardMarkup(keyboard)

            if update.callback_query:
                await update.callback_query.edit_message_text(message_text, reply_markup=reply_markup, parse_mode="HTML")
            else:
                await update.message.reply_text(message_text, reply_markup=reply_markup, parse_mode="HTML")

        except Exception as e:
            logger.error(f"Error showing vocabulary: {e}")
            error_text = localization.get_text(user.interface_language, "vocabulary_load_error")
            if update.callback_query:
                await update.callback_query.answer(error_text)
            else:
                await update.message.reply_text(error_text)


async def handle_vocabulary_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /vocabulary command."""
    await VocabularyHandler.show_vocabulary(update, context)


async def handle_vocabulary_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle vocabulary-related callback queries."""
    query = update.callback_query
    await query.answer()

    data = query.data

    if data.startswith("vocab_page_"):
        parts = data.split("_")
        page = int(parts[2])
        sort_recent = parts[3] == "True"
        edit_mode = parts[4] == "True"
        await VocabularyHandler.show_vocabulary(update, context, page, sort_recent, edit_mode)

    elif data.startswith("vocab_sort_"):
        parts = data.split("_")
        page = int(parts[2])
        sort_recent = parts[3] == "True"
        edit_mode = parts[4] == "True"
        await VocabularyHandler.show_vocabulary(update, context, page, sort_recent, edit_mode)

    elif data.startswith("vocab_edit_on_"):
        parts = data.split("_")
        page = int(parts[3])
        sort_recent = parts[4] == "True"
        await VocabularyHandler.show_vocabulary(update, context, page, sort_recent, edit_mode=True)

    elif data.startswith("vocab_edit_off_"):
        parts = data.split("_")
        page = int(parts[3])
        sort_recent = parts[4] == "True"
        await VocabularyHandler.show_vocabulary(update, context, page, sort_recent, edit_mode=False)

    elif data == "view_vocabulary":
        await VocabularyHandler.show_vocabulary(update, context)
