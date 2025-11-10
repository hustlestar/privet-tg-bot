"""Message handlers for the Learn Words bot."""

import logging
from functools import partial

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from src.handlers.keyboards import create_main_menu_keyboard
from src.handlers.states import user_states, BotStates
from src.handlers.utils import save_word, prepare_language_response_and_keyboard
from src.local.localization import localization
from src.translation.translator import translator
from . import on_new_user_notify
from .training_handlers import handle_training_answer
from ..database import db
from ..explanation_formatter import explanation_formatter
from src.dao.models import User, ResponseMode

logger = logging.getLogger(__name__)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text messages based on user state."""
    user_id = update.effective_user.id
    text = update.message.text.strip()

    # Get user state
    state_data = user_states.get(user_id, {})
    current_state = state_data.get("state")

    if current_state == BotStates.WAITING_NATIVE_LANGUAGE:
        await handle_native_language(update, context, text)
    elif current_state == BotStates.WAITING_LEARNING_LANGUAGE:
        await handle_learning_language(update, context, text)
    elif current_state == BotStates.WAITING_RESPONSE_MODE:
        await handle_response_mode(update, context, text)
    elif current_state == BotStates.WAITING_TRAINING_ANSWER or current_state == BotStates.REVIEW_SESSION_ACTIVE:
        await handle_training_answer(update, context, text)
    else:
        # Default: handle word translation or sentence parsing
        await handle_word_or_sentence(update, context, text)


async def handle_native_language(update: Update, context: ContextTypes.DEFAULT_TYPE, language: str) -> None:
    """Handle native language input."""
    user_id = update.effective_user.id
    user_states[user_id]["native_language"] = language
    user_states[user_id]["interface_language"] = language  # Set interface language same as native
    user_states[user_id]["state"] = BotStates.WAITING_LEARNING_LANGUAGE

    # Get localized text
    reply_markup, text = await prepare_language_response_and_keyboard(language)

    await update.message.reply_text(text, reply_markup=reply_markup)


async def handle_learning_language(update: Update, context: ContextTypes.DEFAULT_TYPE, language: str) -> None:
    """Handle learning language input."""
    user_id = update.effective_user.id
    user_states[user_id]["learning_language"] = language
    user_states[user_id]["state"] = BotStates.WAITING_RESPONSE_MODE

    interface_lang = user_states[user_id].get("interface_language", "english")

    # Get localized button text
    short_text = localization.get_text(interface_lang, "short_translation_only")
    medium_text = localization.get_text(interface_lang, "medium_word_meaning_example")
    long_text = localization.get_text(interface_lang, "long_multiple_translations")

    keyboard = [
        [InlineKeyboardButton(short_text, callback_data="mode_short")],
        [InlineKeyboardButton(medium_text, callback_data="mode_medium")],
        [InlineKeyboardButton(long_text, callback_data="mode_long")],
    ]

    # Add main menu button
    main_menu_text = localization.get_text(interface_lang, "main_menu")
    keyboard.append([InlineKeyboardButton(main_menu_text, callback_data="main_menu")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Get localized text for the main message
    perfect_learning_text = localization.get_text(interface_lang, "perfect_learning", learning_language=language)

    text = perfect_learning_text

    await update.message.reply_text(text, reply_markup=reply_markup)


async def handle_response_mode(update: Update, context: ContextTypes.DEFAULT_TYPE, mode: str) -> None:
    """Handle response mode selection."""
    user_id = update.effective_user.id
    state_data = user_states[user_id]

    # Create user
    user = User(
        user_id=user_id,
        learning_language=state_data["learning_language"],
        interface_language=state_data.get("interface_language", "english"),
        response_mode=ResponseMode(mode),
        telegram_handle=update.effective_user.username,
    )

    await db.create_user(user, callback=partial(on_new_user_notify, context.bot))

    # Clear state
    if user_id in user_states:
        del user_states[user_id]

    interface_lang = user.interface_language
    setup_complete = localization.get_text(interface_lang, "setup_complete")
    native_lang_text = localization.get_text(interface_lang, "native_language")
    learning_lang_text = localization.get_text(interface_lang, "learning_language")
    response_mode_text = localization.get_text(interface_lang, "response_mode")
    explanation_lang_text = localization.get_text(interface_lang, "explanation_language")

    explanation_display = explanation_formatter.get_explanation_language_display(user.explanation_language, user.interface_language)

    # Create main menu keyboard
    keyboard = create_main_menu_keyboard(interface_lang)
    await update.message.reply_text(
        f"{setup_complete}\n\n"
        f"🗣️ {native_lang_text}: {user.interface_language}\n"
        f"📚 {learning_lang_text}: {user.learning_language}\n"
        f"📝 {response_mode_text}: {user.response_mode.value}\n"
        f"💬 {explanation_lang_text}: {explanation_display}\n\n"
        f"{localization.get_text(interface_lang, 'send_word_help')}",
        reply_markup=keyboard,
        parse_mode="HTML",
    )


async def handle_word_or_sentence(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> None:
    """Handle word translation or sentence parsing."""
    user_id = update.effective_user.id

    # Get user
    user = await db.get_user(user_id)
    if not user or not user.interface_language or not user.learning_language:
        # Show multilingual start message - user needs to complete setup
        welcome_text = localization.create_multilingual_welcome()
        keyboard = []

        for display, code in localization.get_language_buttons():
            keyboard.append([InlineKeyboardButton(display, callback_data=f"native_lang_{code}")])

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="HTML")
        return

    # Check if it's a sentence (more than 3 words) or a single word
    words = text.split()
    if len(words) > 12:
        sentence_too_long_text = localization.get_text(user.interface_language, "sentence_too_long")
        await update.message.reply_text(sentence_too_long_text)
        return
    elif len(words) > 4:
        await handle_sentence_parsing(update, context, text, user)
    else:
        await handle_word_translation(update, context, text, user)


async def handle_word_translation(update: Update, context: ContextTypes.DEFAULT_TYPE, word: str, user: User) -> None:
    """Handle single word translation with smart language detection."""
    try:
        # Show typing indicator
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

        # Use smart translation with language detection
        translation_data, detection_result = await translator.smart_translate_word(word, user.interface_language, user.learning_language)

        if translation_data is None:
            # Language detection couldn't determine direction - ask user
            keyboard = [
                [
                    InlineKeyboardButton(
                        f"🔄 {user.interface_language} ➡️ {user.learning_language}",
                        callback_data=f"translate_{word}_to_learning",
                    )
                ],
                [
                    InlineKeyboardButton(
                        f"🔄 {user.learning_language} ➡️ {user.interface_language}",
                        callback_data=f"translate_{word}_to_native",
                    )
                ],
            ]

            # Add main menu button
            main_menu_text = localization.get_text(user.interface_language, "main_menu")
            keyboard.append([InlineKeyboardButton(main_menu_text, callback_data="main_menu")])

            reply_markup = InlineKeyboardMarkup(keyboard)

            # Get localized text for language detection question
            detected_language_question = localization.get_text(
                user.interface_language,
                "detected_language_question",
                detected_language=detection_result["detected_language"],
                explanation=detection_result["explanation"],
            )

            await update.message.reply_text(detected_language_question, reply_markup=reply_markup, parse_mode="HTML")
            return

        # Check cache first with detected languages
        from_lang = detection_result["from_language"]
        to_lang = detection_result["to_language"]

        word_id, cached_word = await save_word(translation_data, from_lang, to_lang, user)

        await db.add_word_to_user_vocabulary(user.user_id, word_id)

        direction_info = f"🔄 <b>{from_lang} ➡️ {to_lang}</b>\n"
        if detection_result["confidence"] != "high":
            direction_info += f"🤖 <b>Detected as {detection_result['detected_language']} ({detection_result['confidence']} confidence)</b>\n\n"
        else:
            direction_info += "\n"

        word_dict = {
            "word": cached_word.word,
            "short_translation": cached_word.short_translation,
            "medium_data": cached_word.medium_data,
            "long_data": cached_word.long_data,
            "synonyms_native": cached_word.synonyms_native or [],
            "synonyms_learning": cached_word.synonyms_learning or [],
            "direction": direction_info,
        }
        formatted_response = explanation_formatter.format_explanation(word_dict, user, user.response_mode.value)

        mark_known_text = localization.get_text(user.interface_language, "mark_as_known")
        delete_word_text = localization.get_text(user.interface_language, "delete_from_vocabulary_button")
        keyboard = [
            [
                InlineKeyboardButton(mark_known_text, callback_data=f"known_{word_id}"),
                InlineKeyboardButton(delete_word_text, callback_data=f"delete_word_translate_{word_id}"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(formatted_response, reply_markup=reply_markup, parse_mode="HTML")

    except Exception as e:
        logger.error(f"Translation error: {e}")
        translation_error_text = localization.get_text(user.interface_language, "translation_error")
        await update.message.reply_text(translation_error_text)


async def handle_sentence_parsing(update: Update, context: ContextTypes.DEFAULT_TYPE, sentence: str, user: User) -> None:
    """Handle sentence parsing for word selection with smart language detection."""
    try:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

        # Use smart sentence parsing with language detection
        words, detection_result = await translator.smart_parse_sentence(sentence, user.interface_language, user.learning_language)

        if not words and detection_result.get("translation_direction") == "ask_user":
            # Language detection couldn't determine direction - ask user
            parse_native_text = localization.get_text(
                user.interface_language,
                "parse_as_native",
                native_language=user.interface_language,
            )
            parse_learning_text = localization.get_text(
                user.interface_language,
                "parse_as_learning",
                learning_language=user.learning_language,
            )

            keyboard = [
                [
                    InlineKeyboardButton(
                        parse_native_text,
                        callback_data=f"parse_sentence_native_{hash(sentence) % 10000}",
                    )
                ],
                [
                    InlineKeyboardButton(
                        parse_learning_text,
                        callback_data=f"parse_sentence_learning_{hash(sentence) % 10000}",
                    )
                ],
            ]

            # Add main menu button
            main_menu_text = localization.get_text(user.interface_language, "main_menu")
            keyboard.append([InlineKeyboardButton(main_menu_text, callback_data="main_menu")])

            reply_markup = InlineKeyboardMarkup(keyboard)

            # Store sentence for later processing
            user_states[update.effective_user.id] = {
                "pending_sentence": sentence,
                "detection_result": detection_result,
            }

            # Get localized text for parse language question
            parse_language_question = localization.get_text(
                user.interface_language,
                "parse_language_question",
                detected_language=detection_result["detected_language"],
                explanation=detection_result["explanation"],
            )

            await update.message.reply_text(parse_language_question, reply_markup=reply_markup, parse_mode="HTML")
            return

        if not words:
            no_meaningful_words_text = localization.get_text(user.interface_language, "no_meaningful_words")
            await update.message.reply_text(no_meaningful_words_text)
            return

        # Show detected language info
        detected_lang = detection_result.get("detected_language", "unknown")
        detected_language_info = localization.get_text(
            user.interface_language,
            "detected_language_info",
            detected_language=detected_lang,
        )
        direction_info = f"{detected_language_info}\n\n"

        # Store sentence context for continuous selection
        user_states[update.effective_user.id] = {
            "sentence_selection": {
                "sentence": sentence,
                "original_words": words,
                "selected_words": [],
                "detection_result": detection_result,
            },
            "state": BotStates.SENTENCE_SELECTION_ACTIVE,
        }

        # Create keyboard with words
        keyboard = []
        for word in words[:10]:  # Limit to 10 words
            keyboard.append([InlineKeyboardButton(word, callback_data=f"add_word_{word}")])

        # Add navigation buttons
        cancel_text = localization.get_text(user.interface_language, "cancel")
        keyboard.append([InlineKeyboardButton(cancel_text, callback_data="cancel_selection")])

        reply_markup = InlineKeyboardMarkup(keyboard)

        # Get localized text for found words message
        found_words_text = localization.get_text(user.interface_language, "found_words_in_sentence", sentence=sentence)

        await update.message.reply_text(
            f"{direction_info}{found_words_text}",
            reply_markup=reply_markup,
            parse_mode="HTML",
        )

    except ValueError as e:
        if "too long" in str(e).lower():
            sentence_too_long_error = localization.get_text(user.interface_language, "sentence_too_long_error")
            await update.message.reply_text(sentence_too_long_error)
        else:
            logger.error(f"Sentence parsing error: {e}")
            parse_sentence_error = localization.get_text(user.interface_language, "parse_sentence_error")
            await update.message.reply_text(parse_sentence_error)
    except Exception as e:
        logger.error(f"Sentence parsing error: {e}")
        parse_sentence_error = localization.get_text(user.interface_language, "parse_sentence_error")
        await update.message.reply_text(parse_sentence_error)
