from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from ..database import db
from ..language_config import language_config
from ..local.localization import localization


async def save_word(translation_data, from_lang, to_lang, user):
    normalized_word = translation_data.word
    cached_word = await db.get_word(normalized_word, from_lang, to_lang, user.interface_language)
    if cached_word:
        word_id = cached_word.id
    else:
        # Save new translation
        word_id = await db.save_word(translation_data)
        cached_word = await db.get_word(normalized_word, from_lang, to_lang, user.interface_language)
    return word_id, cached_word


async def prepare_language_response_and_keyboard(language):
    text = localization.get_text(language, "select_learning_language")
    # Get learning language options (excluding native language)
    learning_options = language_config.get_learning_keyboard(exclude_native=language)
    keyboard = []
    for display_name, code in learning_options:
        keyboard.append([InlineKeyboardButton(display_name, callback_data=f"learning_lang_{code}")])
    # Add main menu button
    main_menu_text = localization.get_text(language, "main_menu")
    keyboard.append([InlineKeyboardButton(main_menu_text, callback_data="main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup, text
