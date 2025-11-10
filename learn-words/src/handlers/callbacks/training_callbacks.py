"""Training callback handlers for the Learn Words bot."""

import logging

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from src.handlers.keyboards import (
    create_main_menu_keyboard,
    get_continue_keyboard,
)
from src.local.localization import localization
from ..states import user_states, BotStates
from ..training_handlers import (
    start_training_session_callback,
    prepare_attempt_feedback_response_and_keyboard, send_next_review_exercise,
)
from ...database import db
from ...training import training_system

logger = logging.getLogger(__name__)


async def handle_training_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle training-related callbacks."""
    query = update.callback_query
    data = query.data

    if data.startswith("answer_"):
        parts = data.split("_")
        option_index = int(parts[1])
        word_id = int(parts[2])
        await handle_multiple_choice_answer(query, context, option_index, word_id)
    elif data.startswith("idk_"):
        word_id = int(data.split("_")[1])
        await handle_i_dont_know_callback(query, context, word_id)
    elif data.startswith("known_"):
        word_id = int(data.split("_")[1])
        await handle_mark_as_known(query, context, word_id)
    elif data == "train_start" or data == "train_continue":
        await continue_training_callback(query, context)
    elif data == "train_stop":
        await stop_training_callback(query, context)
    elif data.startswith("mark_correct"):
        await handle_mark_correct(query, context)


async def stop_training_callback(query, context):
    user_id = query.from_user.id
    state_data = user_states.get(user_id, {})
    
    # Remove keyboard from the previous message in review session
    if state_data.get("state") == BotStates.REVIEW_SESSION_ACTIVE:
        await query.edit_message_reply_markup(reply_markup=None)
    
    # Clear user state when stopping training
    if user_id in user_states:
        del user_states[user_id]
    
    user = await db.get_user(query.from_user.id)
    interface_lang = user.interface_language if user else "english"
    training_ended_text = localization.get_text(interface_lang, "training_ended")
    great_job_text = localization.get_text(interface_lang, "great_job")
    keyboard = create_main_menu_keyboard(interface_lang)
    await context.bot.send_message(
        query.message.chat.id,
        f"{training_ended_text} {great_job_text} 🎉",
        reply_markup=keyboard,
        parse_mode="HTML",
    )


async def continue_training_callback(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the 'Continue' button click."""
    user_id = query.from_user.id
    chat_id = query.message.chat_id
    state_data = user_states.get(user_id, {})

    if state_data.get("state") == BotStates.REVIEW_SESSION_ACTIVE:
        # Remove keyboard from the previous message in review session
        await query.edit_message_reply_markup(reply_markup=None)
        await send_next_review_exercise(user_id, chat_id, context, query=query)
    else:
        await start_training_session_callback(query, context)


async def handle_multiple_choice_answer(query, context, option_index: int, word_id: int) -> None:
    """Handle multiple choice answer selection."""
    user_id = query.from_user.id
    state_data = user_states.get(user_id, {})
    exercise = state_data.get("current_exercise")

    if not exercise or exercise.word.id != word_id:
        user = await db.get_user(user_id)
        interface_lang = user.interface_language if user else "english"

        session_expired_text = localization.get_text(interface_lang, "training_session_expired")

        use_train_text = localization.get_text(interface_lang, "use_train_command")
        await query.edit_message_text(f"{session_expired_text} {use_train_text}")
        return

    # Get selected answer
    if option_index >= len(exercise.options):
        user = await db.get_user(user_id)
        interface_lang = user.interface_language if user else "english"

        invalid_option_text = localization.get_text(interface_lang, "invalid_option")

        await query.edit_message_text(invalid_option_text)
        return

    selected_answer = exercise.options[option_index]
    is_correct = selected_answer == exercise.correct_answer

    feedback, keyboard = await prepare_attempt_feedback_response_and_keyboard(user_id, exercise, is_correct)

    await query.edit_message_text(feedback, reply_markup=keyboard, parse_mode="HTML")

    # Clear training state
    if state_data.get("state") != BotStates.REVIEW_SESSION_ACTIVE:
        if user_id in user_states:
            del user_states[user_id]


async def handle_i_dont_know_callback(query, context, word_id: int) -> None:
    """Handle the 'I don't know' button click."""
    user_id = query.from_user.id
    state_data = user_states.get(user_id, {})
    exercise = state_data.get("current_exercise")

    if not exercise or exercise.word.id != word_id:
        user = await db.get_user(user_id)
        interface_lang = user.interface_language if user else "english"
        session_expired_text = localization.get_text(interface_lang, "training_session_expired")
        use_train_text = localization.get_text(interface_lang, "use_train_command")
        await query.edit_message_text(f"{session_expired_text} {use_train_text}")
        return

    # Treat as an incorrect answer
    is_correct = False
    feedback, keyboard = await prepare_attempt_feedback_response_and_keyboard(user_id, exercise, is_correct)

    await query.edit_message_text(feedback, reply_markup=keyboard, parse_mode="HTML")

    # Clear training state
    if state_data.get("state") != BotStates.REVIEW_SESSION_ACTIVE:
        if user_id in user_states:
            del user_states[user_id]


async def handle_mark_as_known(query, context, word_id: int) -> None:
    """Handle marking a word as known."""
    user_id = query.from_user.id

    try:
        # Mark word as known in database
        success = await db.mark_word_as_known_by_id(user_id, word_id)

        user = await db.get_user(user_id)
        interface_lang = user.interface_language if user else "english"

        if success:
            await query.edit_message_text(f"✅ {query.message.text} ✅")
        else:
            could_not_mark_text = localization.get_text(interface_lang, "could_not_mark_known")
            await query.edit_message_text(f"❌ {could_not_mark_text}\n{query.message.text}")

    except Exception as e:
        logger.error(f"Error marking word as known: {e}")

        user = await db.get_user(user_id)
        interface_lang = user.interface_language if user else "english"

        error_marking_text = localization.get_text(interface_lang, "error_marking_known")

        await query.edit_message_text(f"❌ {error_marking_text}")


async def handle_mark_correct(query, context) -> None:
    """Handle marking an answer as correct."""
    user_id = query.from_user.id

    try:
        # Extract attempt ID and previous repetition level from callback data
        callback_data = query.data
        parts = callback_data.split(":")
        if len(parts) != 3:
            raise ValueError("Invalid callback data format for mark_correct")

        await query.edit_message_reply_markup(reply_markup=None)

        attempt_id = int(parts[1])
        previous_repetition_level = int(parts[2])

        # Get user's interface language
        user = await db.get_user(user_id)
        interface_lang = user.interface_language if user else "english"

        # Update the training attempt to correct
        success = await training_system.mark_attempt_correct(attempt_id, previous_repetition_level)

        if not success:
            error_text = localization.get_text(interface_lang, "attempt_already_correct_or_not_found")
            await context.bot.send_message(query.message.chat.id, f"⚠️ {error_text}")
            return

        # Get success message
        success_text = localization.get_text(interface_lang, "marked_as_correct")

        # Get continue keyboard (for correct answers, no attempt ID needed)
        keyboard = get_continue_keyboard(True, interface_lang)

        # Update the message
        await context.bot.send_message(
            query.message.chat.id,
            f"✅ {success_text}",
            reply_markup=keyboard,
            parse_mode="HTML",
        )

    except (ValueError, IndexError) as e:
        logger.error(f"Invalid callback data for mark_correct: {query.data}, error: {e}")

        user = await db.get_user(user_id)
        interface_lang = user.interface_language if user else "english"

        error_text = localization.get_text(interface_lang, "invalid_request")
        await context.bot.send_message(query.message.chat.id, f"❌ {error_text}")

    except Exception as e:
        logger.error(f"Error marking answer as correct: {e}")

        user = await db.get_user(user_id)
        interface_lang = user.interface_language if user else "english"

        error_occurred_text = localization.get_text(interface_lang, "error_occurred")
        await context.bot.send_message(query.message.chat.id, f"❌ {error_occurred_text}")
