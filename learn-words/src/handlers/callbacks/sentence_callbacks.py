"""Sentence parsing callback handlers for the Learn Words bot."""

import logging
import hashlib
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from ...database import db
from src.translation.translator import translator
from src.local.localization import localization
from src.handlers.keyboards import create_main_menu_keyboard
from ..states import user_states, BotStates
from ...explanation_formatter import explanation_formatter

logger = logging.getLogger(__name__)


async def handle_sentence_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle sentence parsing callbacks."""
    query = update.callback_query
    data = query.data

    if data.startswith("parse_sentence_"):
        # Handle sentence parsing direction selection
        parts = data.split("_")
        direction = parts[2]  # "native" or "learning"
        sentence_hash = parts[3]
        await handle_sentence_parsing_direction(query, context, direction, sentence_hash)
    elif data.startswith("add_word_"):
        word = data.split("_", 2)[2]
        await handle_add_word_from_sentence(query, context, word)
    elif data.startswith("sentence_word_"):
        # Handle progressive sentence word selection
        parts = data.split("_")
        word = parts[2]
        session_id = parts[3]
        await handle_sentence_word_selection(query, context, word, session_id)
    elif data.startswith("sentence_done_"):
        # Handle finishing sentence selection
        session_id = data.split("_")[2]
        await handle_sentence_selection_done(query, context, session_id)
    elif data == "finish_sentence_selection":
        # Handle finishing sentence selection from continuous selection
        await handle_finish_sentence_selection(query, context)
    elif data == "cancel_selection":
        # Handle canceling sentence selection
        await handle_cancel_sentence_selection(query, context)


async def handle_sentence_parsing_direction(query, context, direction: str, sentence_hash: str) -> None:
    """Handle sentence parsing direction selection with progressive word selection."""
    user_id = query.from_user.id

    try:
        user = await db.get_user(user_id)
        if not user:
            please_start_text = localization.get_text("english", "please_start_first")
            await query.edit_message_text(please_start_text)
            return

        interface_lang = user.interface_language

        # Get the original sentence from user state or context
        sentence_data = user_states.get(user_id, {}).get("sentence_data")
        if not sentence_data or sentence_data.get("hash") != sentence_hash:
            session_expired_text = localization.get_text(interface_lang, "session_expired")
            await query.edit_message_text(f"❌ {session_expired_text}")
            return

        sentence = sentence_data.get("text", "")

        # Determine source and target languages
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

        # Parse sentence into words
        words = extract_words_from_sentence(sentence)

        if not words:
            no_words_found_text = localization.get_text(interface_lang, "no_words_found")
            await query.edit_message_text(f"❌ {no_words_found_text}")
            return

        # Create session for progressive selection
        session_id = generate_session_id(user_id, sentence_hash)

        # Store session data
        user_states[user_id] = {
            "state": BotStates.SENTENCE_SELECTION_ACTIVE,
            "sentence_session": {
                "id": session_id,
                "sentence": sentence,
                "words": words,
                "source_lang": source_lang,
                "target_lang": target_lang,
                "selected_words": [],
                "current_index": 0,
            },
        }

        # Show first word selection
        await show_word_selection(query, user, words[0], session_id, 0, len(words))

    except Exception as e:
        logger.error(f"Error handling sentence parsing direction: {e}")

        user = await db.get_user(user_id)
        interface_lang = user.interface_language if user else "english"

        error_occurred_text = localization.get_text(interface_lang, "error_occurred")
        await query.edit_message_text(f"❌ {error_occurred_text}")


async def handle_sentence_word_selection(query, context, word: str, session_id: str) -> None:
    """Handle progressive word selection from sentence parsing."""
    user_id = query.from_user.id

    try:
        user = await db.get_user(user_id)
        if not user:
            please_start_text = localization.get_text("english", "please_start_first")
            await query.edit_message_text(please_start_text)
            return

        interface_lang = user.interface_language

        # Get session data
        session_data = user_states.get(user_id, {}).get("sentence_session")
        if not session_data or session_data.get("id") != session_id:
            session_expired_text = localization.get_text(interface_lang, "session_expired")
            await query.edit_message_text(f"❌ {session_expired_text}")
            return

        # Add word to selected words
        session_data["selected_words"].append(word)
        session_data["current_index"] += 1

        # Check if there are more words
        if session_data["current_index"] < len(session_data["words"]):
            # Show next word
            next_word = session_data["words"][session_data["current_index"]]
            await show_word_selection(
                query,
                user,
                next_word,
                session_id,
                session_data["current_index"],
                len(session_data["words"]),
            )
        else:
            # All words processed, show summary
            await handle_sentence_selection_done(query, context, session_id, show_final_word=True)

    except Exception as e:
        logger.error(f"Error handling sentence word selection: {e}")

        user = await db.get_user(user_id)
        interface_lang = user.interface_language if user else "english"

        error_occurred_text = localization.get_text(interface_lang, "error_occurred")
        await query.edit_message_text(f"❌ {error_occurred_text}")


async def handle_sentence_selection_done(query, context, session_id: str, show_final_word: bool = False) -> None:
    """Handle finishing sentence word selection."""
    user_id = query.from_user.id

    try:
        user = await db.get_user(user_id)
        if not user:
            please_start_text = localization.get_text("english", "please_start_first")
            await query.edit_message_text(please_start_text)
            return

        interface_lang = user.interface_language

        # Get session data
        session_data = user_states.get(user_id, {}).get("sentence_session")
        if not session_data or session_data.get("id") != session_id:
            session_expired_text = localization.get_text(interface_lang, "session_expired")
            await query.edit_message_text(f"❌ {session_expired_text}")
            return

        selected_words = session_data.get("selected_words", [])

        if not selected_words:
            no_words_selected_text = localization.get_text(interface_lang, "no_words_selected")
            keyboard = create_main_menu_keyboard(interface_lang)

            await query.edit_message_text(f"ℹ️ {no_words_selected_text}", reply_markup=keyboard)
        else:
            # Process selected words for translation
            words_processed_text = localization.get_text(interface_lang, "words_processed")
            selected_words_text = localization.get_text(interface_lang, "selected_words")

            response = f"✅ <b>{words_processed_text}</b>\n\n"
            response += f"<b>{selected_words_text}:</b> {', '.join(selected_words)}\n\n"
            response += f"{localization.get_text(interface_lang, 'words_added_to_vocabulary')}"

            # Add words to vocabulary (simplified - in real implementation, you'd translate each)
            for word in selected_words:
                try:
                    # This is a simplified version - you might want to translate each word
                    await db.add_word(
                        user_id=user_id,
                        word=word,
                        translation=f"Translation of {word}",  # Placeholder
                        source_language=session_data["source_lang"],
                        target_language=session_data["target_lang"],
                    )
                except Exception as e:
                    logger.error(f"Error adding word {word}: {e}")

            keyboard = create_main_menu_keyboard(interface_lang)
            await query.edit_message_text(response, reply_markup=keyboard, parse_mode="HTML")

        # Clear session data
        if user_id in user_states:
            del user_states[user_id]

    except Exception as e:
        logger.error(f"Error handling sentence selection done: {e}")

        user = await db.get_user(user_id)
        interface_lang = user.interface_language if user else "english"

        error_occurred_text = localization.get_text(interface_lang, "error_occurred")
        await query.edit_message_text(f"❌ {error_occurred_text}")


async def handle_add_word_from_sentence(query, context, word: str) -> None:
    """Handle adding a word from sentence parsing with continuous selection."""
    user_id = query.from_user.id

    try:
        # Delete the original sentence selection message to avoid clutter
        await query.delete_message()

        user = await db.get_user(user_id)
        if not user:
            please_start_text = localization.get_text("english", "please_start_first")
            # Since we deleted the message, send a new one instead of editing
            await context.bot.send_message(query.message.chat.id, please_start_text)
            return

        interface_lang = user.interface_language

        # Get or initialize sentence selection state
        sentence_state = user_states.get(user_id, {}).get("sentence_selection", {})

        # If no sentence state exists, try to extract from the current message
        if not sentence_state:
            # Try to extract sentence from the current message text
            message_text = query.message.text
            if "I found these words in your sentence:" in message_text:
                # Extract sentence from the message
                lines = message_text.split("\n")
                for line in lines:
                    if line.startswith("*") and line.endswith("*"):
                        sentence = line.strip("*")
                        # Initialize sentence state
                        words = extract_words_from_sentence(sentence)
                        sentence_state = {
                            "sentence": sentence,
                            "original_words": words,
                            "selected_words": [],
                            "detection_result": {},
                        }
                        break

        if not sentence_state:
            # Fallback to simple word addition without sentence context
            await handle_simple_word_addition_no_edit(context, query.message.chat.id, word, user)
            return

        # Get translation for the word
        translation_data = await translator.translate_word(word, user.learning_language, user.interface_language, user.interface_language)

        if translation_data is None:
            translation_failed_text = localization.get_text(interface_lang, "translation_failed")
            await context.bot.send_message(query.message.chat.id, f"❌ {translation_failed_text}")
            return

        # Save translation to database and get Word object
        word_id = await db.save_word(translation_data)
        cached_word = await db.get_word(word, user.learning_language, user.interface_language)

        # Add to user's vocabulary
        await db.add_word_to_user_vocabulary(user.user_id, word_id)

        # Add word to selected words list
        sentence_state["selected_words"].append(word)

        # Update user state
        user_states[user_id] = {
            "sentence_selection": sentence_state,
            "state": BotStates.SENTENCE_SELECTION_ACTIVE,
        }

        # Format response using explanation formatter - with null check
        from ...explanation_formatter import explanation_formatter

        formatted_response, reply_markup = await prepare_sentence_response_and_keyboard_from_cache(
            word, translation_data, cached_word, interface_lang, user, word_id
        )

        # Send the translation
        await context.bot.send_message(
            query.message.chat.id,
            formatted_response,
            reply_markup=reply_markup,
            parse_mode="HTML",
        )

        # Now show the sentence again with updated keyboard (word removed)
        await show_sentence_selection_updated(context, query.message.chat.id, user, sentence_state)

    except Exception as e:
        logger.error(f"Error adding word from sentence: {e}")

        user = await db.get_user(user_id)
        interface_lang = user.interface_language if user else "english"

        error_occurred_text = localization.get_text(interface_lang, "error_occurred")
        await context.bot.send_message(query.message.chat.id, f"❌ {error_occurred_text}")


async def handle_simple_word_addition(query, context, word: str, user) -> None:
    """Handle simple word addition without sentence context (fallback)."""
    interface_lang = user.interface_language
    logger.info(f"Add")
    try:
        # Get translation for the word
        translation_data = await translator.translate_word(word, user.learning_language, user.interface_language, user.interface_language)

        if translation_data is None:
            translation_failed_text = localization.get_text(interface_lang, "translation_failed")
            await query.edit_message_text(f"❌ {translation_failed_text}")
            return

        # Save translation to database and get Word object
        formatted_response, reply_markup = await prepare_sentence_response_and_keyboard(word, translation_data, user, interface_lang)

        await context.bot.send_message(
            query.message.chat.id,
            formatted_response,
            reply_markup=reply_markup,
            parse_mode="HTML",
        )

    except Exception as e:
        logger.error(f"Error in simple word addition: {e}")
        error_occurred_text = localization.get_text(interface_lang, "error_occurred")
        await query.edit_message_text(f"❌ {error_occurred_text}")


async def handle_simple_word_addition_no_edit(context, chat_id: int, word: str, user) -> None:
    """Handle simple word addition without sentence context (no edit version)."""
    interface_lang = user.interface_language

    try:
        # Get translation for the word
        translation_data = await translator.translate_word(word, user.learning_language, user.interface_language, user.interface_language)

        if translation_data is None:
            translation_failed_text = localization.get_text(interface_lang, "translation_failed")
            await context.bot.send_message(chat_id, f"❌ {translation_failed_text}")
            return

        # Save translation to database and get Word object
        formatted_response, reply_markup = await prepare_sentence_response_and_keyboard(word, translation_data, user, interface_lang)

        await context.bot.send_message(chat_id, formatted_response, reply_markup=reply_markup, parse_mode="HTML")

    except Exception as e:
        logger.error(f"Error in simple word addition (no edit): {e}")
        error_occurred_text = localization.get_text(interface_lang, "error_occurred")
        await context.bot.send_message(chat_id, f"❌ {error_occurred_text}")


async def prepare_sentence_response_and_keyboard(word, translation_data, user, interface_lang):
    word_id = await db.save_word(translation_data)
    cached_word = await db.get_word(word, user.learning_language, user.interface_language)
    # Add to user's vocabulary
    await db.add_word_to_user_vocabulary(user.user_id, word_id)
    # Format response using explanation formatter - with null check
    formatted_response, reply_markup = await prepare_sentence_response_and_keyboard_from_cache(
        word, translation_data, cached_word, interface_lang, user, word_id
    )
    return formatted_response, reply_markup


async def prepare_sentence_response_and_keyboard_from_cache(word, translation_data, cached_word, interface_lang, user, word_id):
    if cached_word is None:
        logger.warning(f"cached_word is None for word '{word}', using translation_data as fallback")
        word_dict = {
            "word": translation_data.word,
            "short_translation": translation_data.short,
            "medium_data": translation_data.medium,
            "long_data": translation_data.long,
            "synonyms_native": translation_data.synonyms_native,
            "synonyms_learning": translation_data.synonyms_learning,
        }
    else:
        word_dict = {
            "word": cached_word.word,
            "short_translation": cached_word.short_translation,
            "medium_data": cached_word.medium_data,
            "long_data": cached_word.long_data,
            "synonyms_native": cached_word.synonyms_native or [],
            "synonyms_learning": cached_word.synonyms_learning or [],
        }
    formatted_response = explanation_formatter.format_explanation(word_dict, user, user.response_mode.value)
    keyboard = [
        [
            InlineKeyboardButton(
                f"{localization.get_text(interface_lang, 'mark_as_known')}",
                callback_data=f"known_{word_id}",
            )
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return formatted_response, reply_markup


async def show_sentence_selection_updated(context, chat_id: int, user, sentence_state: dict) -> None:
    """Show the sentence selection interface with updated keyboard (selected words removed)."""
    interface_lang = user.interface_language

    sentence = sentence_state["sentence"]
    original_words = sentence_state["original_words"]
    selected_words = sentence_state["selected_words"]

    # Get remaining words (not yet selected)
    remaining_words = [word for word in original_words if word not in selected_words]

    if not remaining_words:
        # All words have been selected, show completion message
        reply_markup, response = await prepare_all_words_selected_response_and_keyboard(selected_words, interface_lang)

        await context.bot.send_message(chat_id, response, reply_markup=reply_markup, parse_mode="HTML")

        # Clear sentence selection state
        user_id = user.user_id
        if user_id in user_states:
            user_states[user_id].pop("sentence_selection", None)
            if not user_states[user_id]:
                del user_states[user_id]

        return

    # Show detected language info if available
    detection_result = sentence_state.get("detection_result", {})
    detected_lang = detection_result.get("detected_language", "unknown")

    if detected_lang != "unknown":
        detected_language_info = localization.get_text(interface_lang, "detected_language_info", detected_language=detected_lang)
        direction_info = f"{detected_language_info}\n\n"
    else:
        direction_info = ""

    # Create keyboard with remaining words
    keyboard = []
    for word in remaining_words[:10]:  # Limit to 10 words
        keyboard.append([InlineKeyboardButton(word, callback_data=f"add_word_{word}")])

    # Add finish selection button if some words have been selected
    if selected_words:
        finish_text = localization.get_text(interface_lang, "finish_selection")
        keyboard.append([InlineKeyboardButton(f"✅ {finish_text}", callback_data="finish_sentence_selection")])

    # Add cancel button
    cancel_text = localization.get_text(interface_lang, "cancel")
    keyboard.append([InlineKeyboardButton(cancel_text, callback_data="cancel_selection")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Create message text
    found_words_text = localization.get_text(interface_lang, "found_words_in_sentence", sentence=sentence)

    # Add info about selected words if any
    message_text = f"{direction_info}{found_words_text}"
    if selected_words:
        selected_info = localization.get_text(interface_lang, "selected_words")
        message_text += f"\n\n✅ <b>{selected_info}:</b> {', '.join(selected_words)}"

    await context.bot.send_message(chat_id, message_text, reply_markup=reply_markup, parse_mode="HTML")


async def prepare_all_words_selected_response_and_keyboard(selected_words, interface_lang):
    words_processed_text = localization.get_text(interface_lang, "words_processed")
    selected_words_text = localization.get_text(interface_lang, "selected_words")
    response = f"✅ <b>{words_processed_text}</b>\n\n"
    response += f"<b>{selected_words_text}:</b> {', '.join(selected_words)}\n\n"
    response += f"{localization.get_text(interface_lang, 'words_added_to_vocabulary')}"
    keyboard = create_main_menu_keyboard(interface_lang)
    return keyboard, response


async def show_word_selection(query, user, word: str, session_id: str, current_index: int, total_words: int):
    """Show word selection interface."""
    interface_lang = user.interface_language

    # Create keyboard
    keyboard = [
        [
            InlineKeyboardButton(
                f"✅ {localization.get_text(interface_lang, 'add_word')}: {word}",
                callback_data=f"sentence_word_{word}_{session_id}",
            )
        ],
        [
            InlineKeyboardButton(
                f"⏭️ {localization.get_text(interface_lang, 'skip_word')}",
                callback_data=f"sentence_word_skip_{session_id}",
            )
        ],
        [
            InlineKeyboardButton(
                f"✅ {localization.get_text(interface_lang, 'finish_selection')}",
                callback_data=f"sentence_done_{session_id}",
            )
        ],
        [
            InlineKeyboardButton(
                localization.get_text(interface_lang, "cancel"),
                callback_data="cancel_selection",
            )
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Create message text
    word_selection_text = localization.get_text(interface_lang, "word_selection")
    progress_text = localization.get_text(interface_lang, "progress")

    message_text = (
        f"📝 <b>{word_selection_text}</b>\n\n"
        f"<b>{localization.get_text(interface_lang, 'current_word')}:</b> {word}\n"
        f"<b>{progress_text}:</b> {current_index + 1}/{total_words}\n\n"
        f"{localization.get_text(interface_lang, 'select_word_action')}"
    )

    await query.edit_message_text(message_text, reply_markup=reply_markup, parse_mode="HTML")


def extract_words_from_sentence(sentence: str) -> list:
    """Extract meaningful words from a sentence."""
    import re

    # Simple word extraction - remove punctuation and split
    words = re.findall(r"\b[a-zA-ZÀ-ÿ]+\b", sentence)

    # Filter out very short words and common stop words
    stop_words = {
        "a",
        "an",
        "the",
        "and",
        "or",
        "but",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "with",
        "by",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "could",
        "should",
        "may",
        "might",
        "can",
        "must",
    }

    meaningful_words = []
    for word in words:
        if len(word) > 2 and word.lower() not in stop_words:
            meaningful_words.append(word)

    return meaningful_words


async def handle_finish_sentence_selection(query, context) -> None:
    """Handle finishing sentence selection from continuous selection."""
    user_id = query.from_user.id

    try:
        user = await db.get_user(user_id)
        if not user:
            please_start_text = localization.get_text("english", "please_start_first")
            await query.edit_message_text(please_start_text)
            return

        interface_lang = user.interface_language

        # Get sentence selection state
        sentence_state = user_states.get(user_id, {}).get("sentence_selection", {})

        if not sentence_state:
            session_expired_text = localization.get_text(interface_lang, "session_expired")
            await query.edit_message_text(f"❌ {session_expired_text}")
            return

        selected_words = sentence_state.get("selected_words", [])

        if not selected_words:
            no_words_selected_text = localization.get_text(interface_lang, "no_words_selected")
            keyboard = create_main_menu_keyboard(interface_lang)

            await query.edit_message_text(f"ℹ️ {no_words_selected_text}", reply_markup=keyboard)
        else:
            # Show completion message
            reply_markup, response = await prepare_all_words_selected_response_and_keyboard(selected_words, interface_lang)

            await query.edit_message_text(response, reply_markup=reply_markup, parse_mode="HTML")

        # Clear sentence selection state
        if user_id in user_states:
            user_states[user_id].pop("sentence_selection", None)
            if not user_states[user_id]:
                del user_states[user_id]

    except Exception as e:
        logger.error(f"Error finishing sentence selection: {e}")

        user = await db.get_user(user_id)
        interface_lang = user.interface_language if user else "english"

        error_occurred_text = localization.get_text(interface_lang, "error_occurred")
        await query.edit_message_text(f"❌ {error_occurred_text}")


async def handle_cancel_sentence_selection(query, context) -> None:
    """Handle canceling sentence selection."""
    user_id = query.from_user.id

    try:
        user = await db.get_user(user_id)
        if not user:
            please_start_text = localization.get_text("english", "please_start_first")
            await query.edit_message_text(please_start_text)
            return

        interface_lang = user.interface_language

        # Clear sentence selection state
        if user_id in user_states:
            user_states[user_id].pop("sentence_selection", None)
            if not user_states[user_id]:
                del user_states[user_id]

        # Show main menu
        keyboard = create_main_menu_keyboard(interface_lang)
        cancel_text = localization.get_text(interface_lang, "cancel")
        await query.edit_message_text(f"❌ {cancel_text}", reply_markup=keyboard)

    except Exception as e:
        logger.error(f"Error canceling sentence selection: {e}")

        user = await db.get_user(user_id)
        interface_lang = user.interface_language if user else "english"

        error_occurred_text = localization.get_text(interface_lang, "error_occurred")
        await query.edit_message_text(f"❌ {error_occurred_text}")


def generate_session_id(user_id: int, sentence_hash: str) -> str:
    """Generate a unique session ID for sentence processing."""
    import time

    data = f"{user_id}_{sentence_hash}_{int(time.time())}"
    return hashlib.md5(data.encode()).hexdigest()[:8]
