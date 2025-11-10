"""Language selection callback handlers for the Learn Words bot."""

import logging
from functools import partial

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from .. import on_new_user_notify
from ..utils import prepare_language_response_and_keyboard
from ...database import db
from src.local.localization import localization
from ..states import user_states, BotStates
from src.dao.models import User, ResponseMode

logger = logging.getLogger(__name__)


async def handle_language_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle language selection callbacks."""
    query = update.callback_query
    data = query.data

    if data.startswith("native_lang_"):
        language = data.split("_", 2)[2]
        await handle_native_language_callback(query, context, language)
    elif data.startswith("learning_lang_"):
        language = data.split("_", 2)[2]
        await handle_learning_language_callback(query, context, language)


async def handle_native_language_callback(query, context: ContextTypes.DEFAULT_TYPE, language: str) -> None:
    """Handle native language selection from callback query."""
    user_id = query.from_user.id

    # Create or update user with native language immediately
    existing_user = await db.get_user(user_id)
    if existing_user:
        # Update existing user
        existing_user.interface_language = language
        await db.update_user(existing_user)
    else:
        # Create new user with partial data
        user = User(
            user_id=user_id,
            learning_language=None,  # Will be set in next step
            interface_language=language,
            response_mode=ResponseMode.MEDIUM,  # Default, will be set in next step
        )
        await db.create_user(user, callback=partial(on_new_user_notify, context.bot))

    # Store in user state for flow continuation
    user_states[user_id] = {
        "native_language": language,
        "interface_language": language,
        "state": BotStates.WAITING_LEARNING_LANGUAGE,
    }

    # Get localized text
    reply_markup, text = await prepare_language_response_and_keyboard(language)

    await query.edit_message_text(text, reply_markup=reply_markup)


async def handle_learning_language_callback(query, context: ContextTypes.DEFAULT_TYPE, language: str) -> None:
    """Handle learning language selection from callback query."""
    user_id = query.from_user.id

    # Get user from database and update learning language immediately
    user = await db.get_user(user_id)
    if not user:
        session_expired_text = localization.get_text("english", "session_expired_train")
        await query.edit_message_text(session_expired_text)
        return

    # Update user with learning language
    user.learning_language = language
    await db.update_user(user)

    # Update user state for flow continuation
    if user_id not in user_states:
        user_states[user_id] = {}
    user_states[user_id]["learning_language"] = language
    user_states[user_id]["state"] = BotStates.WAITING_RESPONSE_MODE

    interface_lang = user_states[user_id].get("interface_language", "english")

    keyboard = [
        [
            InlineKeyboardButton(
                localization.get_text(interface_lang, "short_translation_only"),
                callback_data="mode_short",
            )
        ],
        [
            InlineKeyboardButton(
                localization.get_text(interface_lang, "medium_word_meaning_example"),
                callback_data="mode_medium",
            )
        ],
        [
            InlineKeyboardButton(
                localization.get_text(interface_lang, "long_multiple_translations"),
                callback_data="mode_long",
            )
        ],
    ]

    # Add main menu button
    main_menu_text = localization.get_text(interface_lang, "main_menu")
    keyboard.append([InlineKeyboardButton(main_menu_text, callback_data="main_menu")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    text = localization.get_text(interface_lang, "perfect_learning", learning_language=language)

    await query.edit_message_text(text, reply_markup=reply_markup)
