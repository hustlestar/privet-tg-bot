"""Settings callback handlers for the Learn Words bot."""

import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from src.handlers.keyboards import create_main_menu_keyboard
from src.language_config import language_config
from src.local.localization import localization, get_translated_value
from ..command_handlers import prepare_settings_response_and_keyboard
from ..states import user_states
from ...database import db
from ...explanation_formatter import explanation_formatter
from src.dao.models import ResponseMode, ExplanationLanguage

logger = logging.getLogger(__name__)


async def handle_settings_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle settings-related callbacks."""
    query = update.callback_query
    data = query.data

    if data.startswith("mode_"):
        mode = data.split("_")[1]
        await handle_response_mode_callback(query, context, mode)
    elif data.startswith("set_mode_"):
        mode = data.split("_")[2]
        await handle_set_response_mode_callback(query, context, mode)
    elif data.startswith("set_explanation_"):
        explanation_type = data.split("_")[2]
        await handle_explanation_language_callback(query, context, explanation_type)
    elif data == "settings_response_mode":
        await handle_settings_response_mode(query, context)
    elif data == "settings_interface_language":
        await handle_settings_interface_language(query, context)
    elif data.startswith("set_interface_lang_"):
        language = data.split("_")[3]
        await handle_set_interface_language_callback(query, context, language)
    elif data == "settings_learning_language":
        await handle_settings_learning_language(query, context)
    elif data.startswith("set_learning_lang_"):
        language = data.split("_")[3]
        await handle_set_learning_language_callback(query, context, language)


async def handle_response_mode_callback(query, context: ContextTypes.DEFAULT_TYPE, mode: str) -> None:
    """Handle response mode selection from callback query."""
    user_id = query.from_user.id

    # Get existing user from database
    user = await db.get_user(user_id)
    if not user:
        await query.edit_message_text("Session expired. Please start with /start")
        return

    # Update user with response mode
    user.response_mode = ResponseMode(mode)
    await db.update_user(user)

    # Clear state
    if user_id in user_states:
        del user_states[user_id]

    interface_lang = user.interface_language
    setup_complete = localization.get_text(interface_lang, "setup_complete")
    native_lang_text = localization.get_text(interface_lang, "native_language")
    learning_lang_text = localization.get_text(interface_lang, "learning_language")
    response_mode_text = localization.get_text(interface_lang, "response_mode")
    explanation_lang_text = localization.get_text(interface_lang, "explanation_language")

    # Create main menu keyboard
    keyboard = create_main_menu_keyboard(interface_lang)

    await query.edit_message_text(
        f"{setup_complete}\n\n"
        f"🗣️ {native_lang_text}: {get_translated_value(user.interface_language, interface_lang)}\n"
        f"📚 {learning_lang_text}: {get_translated_value(user.learning_language, interface_lang)}\n"
        f"📝 {response_mode_text}: {get_translated_value(user.response_mode.value, interface_lang)}\n"
        f"💬 {explanation_lang_text}: {get_translated_value(user.explanation_language.value, interface_lang)}\n\n"
        f"{localization.get_text(interface_lang, 'send_word_help')}",
        reply_markup=keyboard,
        parse_mode="HTML",
    )


async def handle_set_response_mode_callback(query, context: ContextTypes.DEFAULT_TYPE, mode: str) -> None:
    """Handle response mode update from settings."""
    user_id = query.from_user.id

    user = await db.get_user(user_id)
    if not user:
        await query.edit_message_text("Please start with /start first!")
        return

    await db.update_user_response_mode(user_id, ResponseMode(mode))

    # Create back to main menu keyboard
    keyboard = create_main_menu_keyboard(user.interface_language)

    # Get localized text
    response_updated_text = localization.get_text(user.interface_language, "response_mode_updated")

    await query.edit_message_text(f"✅ {response_updated_text}: {mode}", reply_markup=keyboard)


async def handle_explanation_language_callback(query, context: ContextTypes.DEFAULT_TYPE, explanation_type: str) -> None:
    """Handle explanation language selection from callback query."""
    user_id = query.from_user.id

    user = await db.get_user(user_id)
    if not user:
        await query.edit_message_text("Please start with /start first!")
        return

    # Map callback data to enum
    explanation_mapping = {
        "native": ExplanationLanguage.NATIVE,
        "learning": ExplanationLanguage.LEARNING,
        "mixed": ExplanationLanguage.MIXED,
    }

    if explanation_type not in explanation_mapping:
        await query.edit_message_text("Invalid explanation language option.")
        return

    new_explanation_language = explanation_mapping[explanation_type]

    # Update user preference
    await db.update_user_explanation_language(user_id, new_explanation_language)

    # Get display text
    display_text = explanation_formatter.get_explanation_language_display(new_explanation_language, interface_language=user.interface_language)

    # Create back to main menu keyboard
    keyboard = create_main_menu_keyboard(user.interface_language)

    # Get localized text
    interface_lang = user.interface_language
    explanation_updated_text = localization.get_text(interface_lang, "explanation_language_updated")
    new_setting_text = localization.get_text(interface_lang, "new_setting")
    affects_text = localization.get_text(interface_lang, "explanation_affects")

    await query.edit_message_text(
        f"✅ <b>{explanation_updated_text}</b>\n\n"
        f"<b>{new_setting_text}:</b> {display_text}\n\n"
        f"{affects_text}:\n"
        f"• {localization.get_text(interface_lang, 'in_translations')}\n"
        f"• {localization.get_text(interface_lang, 'during_training')}\n"
        f"• {localization.get_text(interface_lang, 'in_vocabulary_reviews')}\n\n"
        f"{localization.get_text(interface_lang, 'change_anytime_explanation')}",
        reply_markup=keyboard,
        parse_mode="HTML",
    )


async def handle_settings_response_mode(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle response mode settings from callback query."""
    user_id = query.from_user.id

    user = await db.get_user(user_id)
    if not user:
        await query.edit_message_text(
            localization.get_text(
                context.user_data.get("interface_language", "english"),
                "please_start_first",
            )
        )
        return

    # Get localized text
    interface_lang = user.interface_language
    back_text = localization.get_text(interface_lang, "back")
    main_menu_text = localization.get_text(interface_lang, "main_menu")
    settings_text = localization.get_text(interface_lang, "settings")
    short_responses_text = localization.get_text(interface_lang, "short_responses")
    medium_responses_text = localization.get_text(interface_lang, "medium_responses")
    long_responses_text = localization.get_text(interface_lang, "long_responses")

    keyboard = [
        [InlineKeyboardButton(f"📝 {short_responses_text}", callback_data="set_mode_short")],
        [InlineKeyboardButton(f"📖 {medium_responses_text}", callback_data="set_mode_medium")],
        [InlineKeyboardButton(f"📚 {long_responses_text}", callback_data="set_mode_long")],
        [InlineKeyboardButton(f"{back_text} {settings_text}", callback_data="show_settings")],
        [InlineKeyboardButton(main_menu_text, callback_data="main_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Get localized text for content
    response_mode_settings_text = localization.get_text(interface_lang, "response_mode_settings")
    current_text = localization.get_text(interface_lang, "current")
    options_text = localization.get_text(interface_lang, "options")
    short_desc_text = localization.get_text(interface_lang, "short_description")
    medium_desc_text = localization.get_text(interface_lang, "medium_description")
    long_desc_text = localization.get_text(interface_lang, "long_description")
    choose_preference_text = localization.get_text(interface_lang, "choose_preference")

    await query.edit_message_text(
        f"📝 <b>{response_mode_settings_text}</b>\n\n"
        f"<b>{current_text}:</b> {get_translated_value(user.response_mode.value, user.interface_language)}\n\n"
        f"<b>{options_text}:</b>\n"
        f"📝 <b>{localization.get_text(interface_lang, 'short')}</b> - {short_desc_text}\n"
        f"📖 <b>{localization.get_text(interface_lang, 'medium')}</b> - {medium_desc_text}\n"
        f"📚 <b>{localization.get_text(interface_lang, 'long')}</b> - {long_desc_text}\n\n"
        f"{choose_preference_text}:",
        reply_markup=reply_markup,
        parse_mode="HTML",
    )


# Language options are now dynamically generated from language_config
def get_language_options() -> list:
    """Get language options from configuration."""
    return language_config.get_interface_keyboard()


def get_learning_language_options() -> list:
    """Get learning language options from configuration."""
    return language_config.get_learning_keyboard()


async def handle_settings_interface_language(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle interface language settings selection."""
    user_id = query.from_user.id
    user = await db.get_user(user_id)
    if not user:
        return

    interface_lang = user.interface_language

    # Get localized text
    select_text = localization.get_text(interface_lang, "select_interface_language")
    current_text = localization.get_text(interface_lang, "current")
    back_text = localization.get_text(interface_lang, "back")
    settings_text = localization.get_text(interface_lang, "settings")
    main_menu_text = localization.get_text(interface_lang, "main_menu")

    # Create language selection keyboard (2x4 grid)
    keyboard = []
    language_options = get_language_options()
    for i in range(0, len(language_options), 2):
        row = []
        for j in range(2):
            if i + j < len(language_options):
                display_name, lang_code = language_options[i + j]
                row.append(InlineKeyboardButton(display_name, callback_data=f"set_interface_lang_{lang_code}"))
        keyboard.append(row)

    # Add back and main menu buttons
    keyboard.extend(
        [
            [InlineKeyboardButton(f"{back_text} {settings_text}", callback_data="show_settings")],
            [InlineKeyboardButton(main_menu_text, callback_data="main_menu")],
        ]
    )

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Get current interface language display name
    language_options = get_language_options()
    current_display = next(
        (display for display, code in language_options if code == interface_lang),
        interface_lang,
    )

    await query.edit_message_text(
        f"🌍 <b>{localization.get_text(interface_lang, 'interface_language_settings')}</b>\n\n"
        f"<b>{current_text}:</b> {current_display}\n\n"
        f"{select_text}",
        reply_markup=reply_markup,
        parse_mode="HTML",
    )


async def handle_set_interface_language_callback(query, context: ContextTypes.DEFAULT_TYPE, language: str) -> None:
    """Handle interface language update."""
    user_id = query.from_user.id
    user = await db.get_user(user_id)
    if not user:
        return

    # Update interface language in database
    await db.update_user_interface_language(user_id, language)

    # Get updated user
    user = await db.get_user(user_id)

    # Get localized text in new language
    success_text = localization.get_text(language, "interface_language_updated")

    # Create back to main menu keyboard
    keyboard = create_main_menu_keyboard(language)
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(f"✅ {success_text}", reply_markup=reply_markup, parse_mode="HTML")


async def handle_settings_learning_language(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle learning language settings selection."""
    user_id = query.from_user.id
    user = await db.get_user(user_id)
    if not user:
        return

    interface_lang = user.interface_language

    # Get localized text
    select_text = localization.get_text(interface_lang, "select_learning_language")
    current_text = localization.get_text(interface_lang, "current")
    back_text = localization.get_text(interface_lang, "back")
    settings_text = localization.get_text(interface_lang, "settings")
    main_menu_text = localization.get_text(interface_lang, "main_menu")

    # Create language selection keyboard (2x4 grid)
    keyboard = []
    learning_language_options = get_learning_language_options()
    for i in range(0, len(learning_language_options), 2):
        row = []
        for j in range(2):
            if i + j < len(learning_language_options):
                display_name, lang_code = learning_language_options[i + j]
                row.append(InlineKeyboardButton(display_name, callback_data=f"set_learning_lang_{lang_code}"))
        keyboard.append(row)

    # Add back and main menu buttons
    keyboard.extend(
        [
            [InlineKeyboardButton(f"{back_text} {settings_text}", callback_data="show_settings")],
            [InlineKeyboardButton(main_menu_text, callback_data="main_menu")],
        ]
    )

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Get current learning language display name
    learning_language_options = get_learning_language_options()
    current_display = next(
        (display for display, code in learning_language_options if code == user.learning_language.lower()),
        user.learning_language,
    )

    await query.edit_message_text(
        f"🎯 <b>{localization.get_text(interface_lang, 'learning_language_settings')}</b>\n\n"
        f"<b>{current_text}:</b> {current_display}\n\n"
        f"{select_text}",
        reply_markup=reply_markup,
        parse_mode="HTML",
    )


async def handle_set_learning_language_callback(query, context: ContextTypes.DEFAULT_TYPE, language: str) -> None:
    """Handle learning language update."""
    user_id = query.from_user.id
    user = await db.get_user(user_id)
    if not user:
        return

    # Update learning language in database
    await db.update_user_learning_language(user_id, language)

    # Get localized text
    success_text = localization.get_text(user.interface_language, "learning_language_updated")

    # Create back to main menu keyboard
    keyboard = create_main_menu_keyboard(user.interface_language)

    await query.edit_message_text(f"✅ {success_text}", reply_markup=keyboard, parse_mode="HTML")


async def settings_command_callback(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /settings command from callback query."""
    user_id = query.from_user.id

    user = await db.get_user(user_id)
    if not user:
        please_start_msg = localization.get_text("english", "please_start_first")
        await query.edit_message_text(please_start_msg)
        return

    reply_markup, settings_text = await prepare_settings_response_and_keyboard(user)

    await query.edit_message_text(settings_text, reply_markup=reply_markup, parse_mode="HTML")
