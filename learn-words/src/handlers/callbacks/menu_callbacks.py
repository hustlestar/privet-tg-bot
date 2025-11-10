"""Menu and navigation callback handlers for the Learn Words bot."""

import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from src.language_config import language_config
from src.local.localization import localization
from .settings_callbacks import settings_command_callback
from ..command_handlers import stats_command_callback
from src.handlers.keyboards import create_main_menu_keyboard
from ..states import user_states, BotStates
from ...database import db

logger = logging.getLogger(__name__)


async def handle_menu_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle menu and navigation callbacks."""
    query = update.callback_query
    data = query.data

    if data == "main_menu":
        await handle_main_menu_callback(query, context)
    elif data == "cancel_selection":
        await handle_cancel_selection_callback(query, context)
    elif data == "show_stats":
        await stats_command_callback(query, context)
    elif data == "show_settings":
        await settings_command_callback(query, context)


async def handle_main_menu_callback(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle main menu callback."""
    user_id = query.from_user.id
    
    # Clear any existing state when returning to main menu
    if user_id in user_states:
        del user_states[user_id]

    user = await db.get_user(user_id)
    if not user or not user.interface_language or not user.learning_language:
        # Show multilingual start message - user needs to complete setup
        welcome_text = localization.create_multilingual_welcome()
        keyboard = []

        for display, code in language_config.get_interface_keyboard():
            keyboard.append([InlineKeyboardButton(display, callback_data=f"native_lang_{code}")])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(welcome_text, reply_markup=reply_markup, parse_mode="HTML")
        return

    interface_lang = user.interface_language

    # Create main menu keyboard
    keyboard = create_main_menu_keyboard(interface_lang)

    # Get localized welcome text
    welcome_text = localization.get_text(interface_lang, "send_word_help")
    main_menu_text = localization.get_text(interface_lang, "main_menu")

    await query.edit_message_text(
        f"🏠 <b>{main_menu_text}</b>\n\n{welcome_text}",
        reply_markup=keyboard,
        parse_mode="HTML",
    )


async def handle_cancel_selection_callback(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle cancel selection callback."""
    user_id = query.from_user.id

    user = await db.get_user(user_id)
    interface_lang = user.interface_language if user else "english"

    # Clear any sentence selection state
    if user_id in user_states and user_states[user_id].get("state") == BotStates.SENTENCE_SELECTION_ACTIVE:
        del user_states[user_id]

    # Create main menu keyboard
    keyboard = create_main_menu_keyboard(interface_lang)

    cancel_text = localization.get_text(interface_lang, "cancel")
    await query.edit_message_text(f"{cancel_text} ✅", reply_markup=keyboard)
