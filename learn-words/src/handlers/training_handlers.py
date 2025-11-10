"""Training handlers for the Learn Words bot."""

import logging
import random
from typing import List

from typing import Optional

from telegram import Update, CallbackQuery
from telegram.ext import ContextTypes

from src.handlers.keyboards import get_continue_keyboard, create_exercise_keyboard, create_main_menu_keyboard
from src.local.localization import localization  # Added import
from .states import user_states, BotStates
from ..database import db
from ..training import training_system

logger = logging.getLogger(__name__)


async def start_training_session(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start a training session."""
    user_id = update.effective_user.id
    user = await db.get_user(user_id)
    interface_lang = user.interface_language if user else "english"

    try:
        # Get training exercise
        exercise = await training_system.get_training_exercise(user_id, interface_lang)
        if not exercise:
            await update.message.reply_text(localization.get_text(interface_lang, "training_no_words_available"))
            return

        # Store current exercise in user state
        user_states[user_id] = {
            "state": BotStates.TRAINING_ACTIVE,
            "current_exercise": exercise,
        }

        # Send exercise
        keyboard, is_multiple = create_exercise_keyboard(exercise, interface_lang)

        if is_multiple:
            # Multiple choice
            await update.message.reply_text(exercise.question, reply_markup=keyboard, parse_mode="HTML")
        else:
            # Text input required
            user_states[user_id]["state"] = BotStates.WAITING_TRAINING_ANSWER
            await update.message.reply_text(
                localization.get_text(
                    interface_lang,
                    "training_type_answer_prompt",
                    question=exercise.question,
                ),
                reply_markup=keyboard,
                parse_mode="HTML",
            )

    except Exception as e:
        logger.error(f"Training session error: {e}")
        await update.message.reply_text(localization.get_text(interface_lang, "training_error_start"))


async def send_next_review_exercise(
    user_id: int, chat_id: int, context: ContextTypes.DEFAULT_TYPE, query: Optional[CallbackQuery] = None
) -> None:
    """Fetches the next word from the review queue, sends the exercise, and updates the state."""

    logger.debug(f"Sending next review exercise for user {user_id}")
    user = await db.get_user(user_id)
    interface_lang = user.interface_language if user else "english"
    state_data = user_states.get(user_id, {})
    review_word_ids = state_data.get("review_word_ids", [])

    if not review_word_ids:
        review_session_finished = f'🫡 {localization.get_text(interface_lang, "review_session_complete")} 🥳'
        await context.bot.send_message(chat_id, review_session_finished, reply_markup=create_main_menu_keyboard(interface_lang), parse_mode="HTML")
        if user_id in user_states:
            del user_states[user_id]
        return

    # Take the next word from the list
    next_word_id = review_word_ids[0]
    remaining_word_ids = review_word_ids[1:]

    exercise = await training_system.get_review_exercise(user_id, interface_lang, next_word_id)
    if not exercise:
        review_session_finished = f'🫡 {localization.get_text(interface_lang, "review_session_complete")} 🥳'
        logger.error(f"Could not generate exercise for word_id {next_word_id}, ending session.")
        await context.bot.send_message(chat_id, review_session_finished, reply_markup=create_main_menu_keyboard(interface_lang), parse_mode="HTML")
        if user_id in user_states:
            del user_states[user_id]
        return

    # Update the user's state with the remaining words *before* sending the next one
    user_states[user_id]["review_word_ids"] = remaining_word_ids
    user_states[user_id]["current_exercise"] = exercise
    logger.debug(f"Words remaining in review for user {user_id}: {len(remaining_word_ids)} {remaining_word_ids}")

    keyboard, is_multiple = create_exercise_keyboard(exercise, interface_lang)
    if is_multiple:
        await context.bot.send_message(
            chat_id,
            exercise.question,
            reply_markup=keyboard,
            parse_mode="HTML",
        )
    else:
        await context.bot.send_message(
            chat_id,
            localization.get_text(
                interface_lang,
                "training_type_answer_prompt",
                question=exercise.question,
            ),
            reply_markup=keyboard,
            parse_mode="HTML",
        )


async def start_review_session(update: Update, context: ContextTypes.DEFAULT_TYPE, word_ids: List[int]) -> None:
    """Start a review session for a specific list of words."""
    user_id = update.callback_query.from_user.id
    chat_id = update.callback_query.message.chat_id
    logger.info(f"Initializing review session for user {user_id} with {len(word_ids)} words: {word_ids}")

    # Shuffle the word list to make reviews less predictable and store the whole list in state
    random.shuffle(word_ids)
    user_states[user_id] = {
        "state": BotStates.REVIEW_SESSION_ACTIVE,
        "review_word_ids": word_ids,
    }

    # Immediately start the first exercise
    await send_next_review_exercise(user_id, chat_id, context, query=update.callback_query)


async def start_training_session_callback(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start a training session from callback query."""
    user_id = query.from_user.id
    user = await db.get_user(user_id)
    interface_lang = user.interface_language if user else "english"

    try:
        # Get training exercise
        exercise = await training_system.get_training_exercise(user_id, interface_lang)
        if not exercise:
            await query.edit_message_text(localization.get_text(interface_lang, "training_no_words_available"))
            return
        else:
            await query.edit_message_reply_markup(reply_markup=None)

        # Store current exercise in user state
        user_states[user_id] = {
            "state": BotStates.TRAINING_ACTIVE,
            "current_exercise": exercise,
        }

        # Send exercise
        keyboard, is_multiple = create_exercise_keyboard(exercise, interface_lang)

        if is_multiple:
            # Multiple choice
            await context.bot.send_message(
                query.message.chat.id,
                exercise.question,
                reply_markup=keyboard,
                parse_mode="HTML",
            )
        else:
            # Text input required
            user_states[user_id]["state"] = BotStates.WAITING_TRAINING_ANSWER
            await context.bot.send_message(
                query.message.chat.id,
                localization.get_text(
                    interface_lang,
                    "training_type_answer_prompt",
                    question=exercise.question,
                ),
                reply_markup=keyboard,
                parse_mode="HTML",
            )

    except Exception as e:
        logger.error(f"Training session error: {e}")
        await query.edit_message_text(localization.get_text(interface_lang, "training_error_start"))


async def handle_training_answer(update: Update, context: ContextTypes.DEFAULT_TYPE, answer: str) -> None:
    """Handle training answer input."""
    user_id = update.effective_user.id
    state_data = user_states.get(user_id, {})
    exercise = state_data.get("current_exercise")

    # Get user's interface language - this part was already good, but we need it for the string below
    user = await db.get_user(user_id)
    interface_lang = user.interface_language if user else "english"  # Renamed for clarity from plan

    if not exercise:
        await update.message.reply_text(localization.get_text(interface_lang, "training_no_active_session"))
        return

    # Check answer
    is_correct = training_system.check_answer(answer, exercise.correct_answer, exercise.training_type)

    # Add like reaction if answer is correct
    if is_correct:
        try:
            await update.message.set_reaction("👍")
        except Exception as e:
            logger.error(f"Failed to add reaction: {e}")

    is_review = state_data.get("state") == BotStates.REVIEW_SESSION_ACTIVE
    feedback, keyboard = await prepare_attempt_feedback_response_and_keyboard(user_id, exercise, is_correct, is_review)

    await update.message.reply_text(feedback, reply_markup=keyboard, parse_mode="HTML")

    # If in a review session, prepare for the next word
    if state_data.get("state") == BotStates.REVIEW_SESSION_ACTIVE:
        # Don't clear the state yet, just remove the current exercise
        if "current_exercise" in user_states.get(user_id, {}):
            del user_states[user_id]["current_exercise"]
    elif user_id in user_states:
        # Clear training state for regular training
        del user_states[user_id]


async def prepare_attempt_feedback_response_and_keyboard(user_id, exercise, is_correct, is_review: bool = False):
    # Get user word stats to fetch current repetition level
    stats = await db.get_user_word_stats(user_id, exercise.word.id)
    previous_repetition_level = stats.repetition_level if stats else 0

    # Record attempt and get attempt ID
    attempt_id = await training_system.record_attempt(user_id, exercise.word.id, exercise.training_type, is_correct, is_review)

    # Get user's interface language
    user = await db.get_user(user_id)
    interface_lang = user.interface_language if user else "english"

    # Send feedback
    feedback = training_system.get_feedback_message(
        is_correct, exercise.correct_answer, exercise.word, exercise.training_type, interface_lang
    )

    # Pass the previous repetition level to the keyboard creation
    keyboard = get_continue_keyboard(
        is_correct,
        interface_lang,
        attempt_id,
        exercise.word.id,
        previous_repetition_level=previous_repetition_level,
    )
    return feedback, keyboard
