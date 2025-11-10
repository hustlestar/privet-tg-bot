"""Command handlers for the Learn Words bot."""

import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from src.local.localization import localization
from src.handlers.keyboards import create_main_menu_keyboard
from src.handlers.states import user_states
from ..database import db
from ..explanation_formatter import explanation_formatter
from src.language_config import language_config
from src.scheduler import trigger_repetition_notification_for_user
from src.handlers import MAINTAINER

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    user_id = update.effective_user.id
    
    # Clear any existing state to ensure clean start
    if user_id in user_states:
        del user_states[user_id]

    # Check if user already exists and has complete setup
    existing_user = await db.get_user(user_id)
    if existing_user and existing_user.interface_language and existing_user.learning_language:
        interface_lang = existing_user.interface_language

        keyboard = create_main_menu_keyboard(interface_lang)
        welcome_back = localization.get_text(interface_lang, "welcome_back")
        send_word_help = localization.get_text(interface_lang, "send_word_help")

        await update.message.reply_text(
            f"{welcome_back}\n\n" f"{send_word_help}\n",
            reply_markup=keyboard,
            parse_mode="HTML",
        )
        return

    # New user setup - show multilingual welcome
    welcome_text = localization.create_multilingual_welcome()
    keyboard = []

    for display, code in language_config.get_interface_keyboard():
        keyboard.append([InlineKeyboardButton(display, callback_data=f"native_lang_{code}")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="HTML")


async def train_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /train command."""
    user_id = update.effective_user.id

    # Check if user exists
    user = await db.get_user(user_id)
    if not user:
        please_start_setup = localization.get_text("english", "please_start_setup")
        await update.message.reply_text(please_start_setup)
        return

    # Check if user has words to train
    vocab_count = await db.get_user_vocabulary_count(user_id)
    if vocab_count == 0:
        # Create main menu keyboard
        keyboard = create_main_menu_keyboard(user.interface_language)
        no_vocabulary_msg = localization.get_text(user.interface_language, "no_vocabulary_yet")
        await update.message.reply_text(no_vocabulary_msg, reply_markup=keyboard)
        return

    from .training_handlers import start_training_session

    await start_training_session(update, context)


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /stats command."""
    user_id = update.effective_user.id

    user = await db.get_user(user_id)
    if not user:
        please_start_msg = localization.get_text("english", "please_start_first")
        await update.message.reply_text(please_start_msg)
        return

    reply_markup, response = await _prepare_stats_response_and_keyboard(user, user_id)

    await update.message.reply_text(response, reply_markup=reply_markup, parse_mode="HTML")


async def stats_command_callback(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /stats command from callback query."""
    user_id = query.from_user.id

    user = await db.get_user(user_id)
    if not user:
        please_start_msg = localization.get_text("english", "please_start_first")
        await query.edit_message_text(please_start_msg)
        return

    reply_markup, response = await _prepare_stats_response_and_keyboard(user, user_id)

    await query.edit_message_text(response, reply_markup=reply_markup, parse_mode="HTML")


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /settings command."""
    user_id = update.effective_user.id

    user = await db.get_user(user_id)
    if not user:
        please_start_msg = localization.get_text("english", "please_start_first")
        await update.message.reply_text(please_start_msg)
        return

    reply_markup, settings_text = await prepare_settings_response_and_keyboard(user)

    await update.message.reply_text(settings_text, reply_markup=reply_markup, parse_mode="HTML")


async def prepare_settings_response_and_keyboard(user):
    settings_text = explanation_formatter.format_settings_display(user)
    # Get localized text
    interface_lang_text = localization.get_text(user.interface_language, "interface_language_settings")
    learning_lang_text = localization.get_text(user.interface_language, "learning_language_settings")
    explanation_lang_text = localization.get_text(user.interface_language, "explanation_preference_title").replace("💬 **", "💬 ").replace("**", "")
    response_mode_text = localization.get_text(user.interface_language, "response_mode_settings")
    stats_text = localization.get_text(user.interface_language, "view_stats")
    notification_settings_text = localization.get_text(user.interface_language, "notification_settings")
    main_menu_text = localization.get_text(user.interface_language, "main_menu")

    keyboard = [
        [InlineKeyboardButton(interface_lang_text, callback_data="settings_interface_language")],
        [InlineKeyboardButton(learning_lang_text, callback_data="settings_learning_language")],
        [InlineKeyboardButton(explanation_lang_text, callback_data="explanation_command")],
        [InlineKeyboardButton(response_mode_text, callback_data="settings_response_mode")],
        [InlineKeyboardButton(stats_text, callback_data="show_stats")],
        [
            InlineKeyboardButton(
                notification_settings_text,
                callback_data="settings_notifications_settings",
            )
        ],
        [InlineKeyboardButton(main_menu_text, callback_data="main_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup, settings_text


async def explanation_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /explanation command."""
    user_id = update.effective_user.id

    user = await db.get_user(user_id)
    if not user:
        please_start_msg = localization.get_text("english", "please_start_first")
        await update.message.reply_text(please_start_msg)
        return

    (
        choose_text,
        current_text,
        learning_option,
        mixed_option,
        native_option,
        options_text,
        reply_markup,
        title,
    ) = await _prepare_explanation_language_response_and_keyboard(user)

    await update.message.reply_text(
        f"{title}\n\n" f"{current_text}\n\n" f"{options_text}\n" f"{native_option}\n" f"{learning_option}\n" f"{mixed_option}\n\n" f"{choose_text}",
        reply_markup=reply_markup,
        parse_mode="HTML",
    )


async def explanation_command_callback(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /explanation command from callback query."""
    user_id = query.from_user.id

    user = await db.get_user(user_id)
    if not user:
        please_start_msg = localization.get_text("english", "please_start_first")
        await query.edit_message_text(please_start_msg)
        return

    (
        choose_text,
        current_text,
        learning_option,
        mixed_option,
        native_option,
        options_text,
        reply_markup,
        title,
    ) = await _prepare_explanation_language_response_and_keyboard(user)

    await query.edit_message_text(
        f"{title}\n\n" f"{current_text}\n\n" f"{options_text}\n" f"{native_option}\n" f"{learning_option}\n" f"{mixed_option}\n\n" f"{choose_text}",
        reply_markup=reply_markup,
        parse_mode="HTML",
    )


async def _prepare_stats_response_and_keyboard(user, user_id):
    stats = await db.get_user_stats(user_id)
    # Get localized text
    stats_title = localization.get_text(user.interface_language, "statistics_title")
    vocab_stat = localization.get_text(user.interface_language, "vocabulary_stat", count=stats["total_words"])
    known_words_stat = localization.get_text(user.interface_language, "known_words_stat", count=stats["known_words"])
    total_attempts = stats.get("total_attempts")
    total_correct = stats.get("total_correct")

    if isinstance(total_attempts, int) and isinstance(total_correct, int) and total_attempts > 0:
        accuracy_rate = (total_correct / total_attempts) * 100.0
        accuracy_stat = localization.get_text(user.interface_language, "overall_accuracy_stat", rate=accuracy_rate)
    else:
        accuracy_rate = 0.0
        accuracy_stat = localization.get_text(user.interface_language, "overall_accuracy_stat", rate=accuracy_rate)
    attempts_stat = localization.get_text(user.interface_language, "total_attempts_stat", count=stats["total_attempts"])
    correct_stat = localization.get_text(user.interface_language, "correct_answers_stat", count=stats["total_correct"])
    last_7_days = localization.get_text(user.interface_language, "last_7_days")
    recent_attempts = localization.get_text(user.interface_language, "recent_attempts", count=stats["recent_attempts"])
    recent_correct = localization.get_text(user.interface_language, "recent_correct", count=stats["recent_correct"])
    if stats["recent_attempts"] > 0:
        recent_accuracy_rate = (stats["recent_correct"] / stats["recent_attempts"]) * 100
    else:
        recent_accuracy_rate = 0
    recent_accuracy = localization.get_text(user.interface_language, "recent_accuracy", rate=recent_accuracy_rate)
    back_text = localization.get_text(user.interface_language, "back")
    settings_text = localization.get_text(user.interface_language, "settings")
    response = (
        f"{stats_title}\n\n"
        f"{vocab_stat}\n"
        f"{known_words_stat}\n"
        f"{accuracy_stat}\n"
        f"{attempts_stat}\n"
        f"{correct_stat}\n\n"
        f"{last_7_days}\n"
        f"{recent_attempts}\n"
        f"{recent_correct}\n"
        f"{recent_accuracy}"
    )
    keyboard = [
        [InlineKeyboardButton(f"{back_text} {settings_text}", callback_data="show_settings")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup, response


async def vocabulary_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /vocabulary command."""
    user_id = update.effective_user.id

    user = await db.get_user(user_id)
    if not user:
        please_start_msg = localization.get_text("english", "please_start_first")
        await update.message.reply_text(please_start_msg)
        return

    from .vocabulary_handlers import VocabularyHandler

    await VocabularyHandler.show_vocabulary(update, context)


async def _prepare_explanation_language_response_and_keyboard(user):
    current_display = explanation_formatter.get_explanation_language_display(user.explanation_language, user.interface_language)
    # Get localized text
    main_menu_text = localization.get_text(user.interface_language, "main_menu")
    title = localization.get_text(user.interface_language, "explanation_preference_title")
    current = localization.get_text(user.interface_language, "current")
    current_text = f"<b>{current}</b> {current_display}"
    options_text = localization.get_text(user.interface_language, "explanation_options")
    native_option = localization.get_text(user.interface_language, "native_language_option").format(language=user.interface_language)
    learning_option = localization.get_text(user.interface_language, "learning_language_option").format(language=user.learning_language)
    mixed_option = localization.get_text(user.interface_language, "mixed_mode_option").format(
        learning_language=user.learning_language, native_language=user.interface_language
    )
    choose_text = localization.get_text(user.interface_language, "choose_preference")
    native_button = localization.get_text(user.interface_language, "native_language_button")
    learning_button = localization.get_text(user.interface_language, "learning_language_button")
    mixed_button = localization.get_text(user.interface_language, "mixed_mode_button")
    keyboard = [
        [InlineKeyboardButton(native_button, callback_data="set_explanation_native")],
        [InlineKeyboardButton(learning_button, callback_data="set_explanation_learning")],
        [InlineKeyboardButton(mixed_button, callback_data="set_explanation_mixed")],
        [InlineKeyboardButton(main_menu_text, callback_data="main_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return (
        choose_text,
        current_text,
        learning_option,
        mixed_option,
        native_option,
        options_text,
        reply_markup,
        title,
    )


async def test_notification_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /test_notification command for the maintainer."""
    user_id = update.effective_user.id

    if user_id != MAINTAINER:
        # Silently ignore the command if it's not from the maintainer
        logger.warning(f"User {user_id} tried to use the /test_notification command.")
        return

    await update.message.reply_text("Attempting to send a test repetition notification...")
    await trigger_repetition_notification_for_user(user_id, context.application, force=True)
