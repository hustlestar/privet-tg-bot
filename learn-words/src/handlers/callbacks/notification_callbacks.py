"""Callback handlers for notification-related actions."""

import logging
from datetime import datetime

from telegram import Update, CallbackQuery
from telegram.error import BadRequest
from datetime import timezone
from telegram.ext import ContextTypes

from src.handlers.keyboards import (
    create_notification_time_keyboard,
    create_main_menu_keyboard,
    create_timezone_keyboard,
)
from ...database import db
from ...local.localization import localization
from src.dao.models import UserPlan
from ...time_utils import convert_local_to_utc_time, convert_utc_to_local_time

logger = logging.getLogger(__name__)


async def handle_confirm_repetition(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the 'I Remember These' button from a repetition notification."""
    user, notification, due_word_id, tracking_id, created_at = await _get_user_and_notification_data(update, context)

    if not user or not notification:
        # If the notification is expired, _get_user_and_notification_data will handle it.
        return

    if tracking_id:
        await db.mark_notification_as_responded(tracking_id)

    await db.batch_update_word_repetition_status(user.user_id, notification["word_ids"])
    await db.delete_due_word_notification(due_word_id)

    # Only try to edit the message if the notification is less than 47 hours old.
    is_editable = (datetime.now(timezone.utc) - created_at).total_seconds() < 47 * 3600
    if is_editable:
        try:
            await update.callback_query.edit_message_reply_markup(reply_markup=None)
        except BadRequest as e:
            if "message to edit not found" in e.message.lower():
                logger.warning(f"Failed to edit message for user {user.user_id} despite it being within the 47-hour window.")
            else:
                raise

    # Always send a confirmation message, which handles the case where the edit fails.
    await context.bot.send_message(
        update.callback_query.message.chat.id,
        localization.get_text(user.interface_language, "repetition_marked_as_reviewed"),
        reply_markup=create_main_menu_keyboard(user.interface_language),
    )


async def handle_start_review(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the 'Start Training' button from a repetition notification."""
    user, notification, due_word_id, tracking_id, created_at = await _get_user_and_notification_data(update, context)

    if not user or not notification:
        return

    if tracking_id:
        await db.mark_notification_as_responded(tracking_id)

    from src.handlers.training_handlers import start_review_session

    is_editable = (datetime.now(timezone.utc) - created_at).total_seconds() < 47 * 3600
    if is_editable:
        try:
            # First, try to remove the inline keyboard to prevent multiple clicks
            await update.callback_query.edit_message_reply_markup(reply_markup=None)
            # Then, try to edit the text to indicate the session is starting
            await update.callback_query.edit_message_text(localization.get_text(user.interface_language, "repetition_start_review_session"))
        except BadRequest as e:
            if "message to edit not found" in e.message.lower():
                logger.warning(f"Failed to edit message for user {user.user_id} on review start despite it being within the 47-hour window.")
            else:
                raise
    else:
        # If the message is not editable, we send a new message instead.
        await context.bot.send_message(
            update.callback_query.message.chat.id,
            localization.get_text(user.interface_language, "repetition_start_review_session"),
        )

    await start_review_session(update, context, word_ids=notification["word_ids"])


async def handle_notification_settings(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the 'Notification Settings' button."""
    user = await db.get_user(query.from_user.id)
    if not user:
        return

    # Check for timezone
    if not user.timezone or user.timezone == "UTC":
        title = localization.get_text(user.interface_language, "set_timezone_title")
        prompt = localization.get_text(user.interface_language, "set_timezone_prompt")
        keyboard = create_timezone_keyboard(user)

        await query.edit_message_text(f"<b>{title}</b>\n\n{prompt}", reply_markup=keyboard, parse_mode="HTML")
        return

    keyboard = create_notification_time_keyboard(user)
    title = localization.get_text(user.interface_language, "notification_settings_title")

    # Add plan-specific information to the message
    if user.plan == UserPlan.FREE:
        plan_text = localization.get_text(user.interface_language, "notification_settings_free_limit")
    else:
        plan_text = localization.get_text(user.interface_language, "notification_settings_premium_limit")

    existing_times_str = ""
    if user.notification_times:
        # Convert UTC times to local time for display
        local_times = sorted([convert_utc_to_local_time(t, user.timezone) for t in user.notification_times])
        times_list_str = "\n".join([f"• {t}" for t in local_times])

        # Use a more descriptive header
        header = localization.get_text(user.interface_language, "your_notification_times")
        existing_times_str = f"<b>{header}</b>\n{times_list_str}"

    await query.edit_message_text(
        f"<b>{title}</b>\n\n{plan_text}\n\n{existing_times_str}",
        reply_markup=keyboard,
        parse_mode="HTML",
    )


async def handle_set_timezone(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle setting the user's timezone from the timezone keyboard."""
    user = await db.get_user(query.from_user.id)
    if not user:
        return

    timezone_str = query.data.split("_")[-1]
    user.timezone = timezone_str
    await db.update_user(user)

    # Now that the timezone is set, show the notification settings
    await handle_notification_settings(query, context)


async def handle_set_notification_time(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle setting a new notification time."""
    user = await db.get_user(query.from_user.id)
    if not user:
        return

    local_time_str = query.data.split("_")[-1]
    utc_time_str = convert_local_to_utc_time(local_time_str, user.timezone)

    if not user.notification_times:
        user.notification_times = []

    # A user on a free plan can have only one notification time
    if user.plan == UserPlan.FREE and len(user.notification_times) >= 1:
        limit_text = localization.get_text(user.interface_language, "free_plan_notification_limit")
        await context.bot.send_message(
            query.from_user.id,
            limit_text,
        )
        return

    if utc_time_str not in user.notification_times:
        user.notification_times.append(utc_time_str)
        user.notification_times_count = len(user.notification_times)
        await db.update_user(user)

        # Send confirmation and then refresh the settings
        text = localization.get_text(user.interface_language, "notification_time_added", time=local_time_str)
        await context.bot.send_message(
            query.from_user.id,
            f"🔔 {text}",
        )

    await handle_notification_settings(query, context)


async def handle_remove_notification_time(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle removing a notification time."""
    user = await db.get_user(query.from_user.id)
    if not user:
        return

    local_time_str = query.data.split("_")[-1]
    utc_time_str = convert_local_to_utc_time(local_time_str, user.timezone)

    if user.notification_times and utc_time_str in user.notification_times:
        user.notification_times.remove(utc_time_str)
        user.notification_times_count = len(user.notification_times)
        await db.update_user(user)

        # Send confirmation and then refresh the settings
        text = localization.get_text(user.interface_language, "notification_time_removed", time=local_time_str)
        await context.bot.send_message(
            query.from_user.id,
            f"🔕 {text}",
        )

    await handle_notification_settings(query, context)


async def _get_user_and_notification_data(update, context):
    user_id = update.callback_query.from_user.id
    user = await db.get_user(user_id)
    if not user:
        try:
            await update.callback_query.edit_message_text(localization.get_text("english", "session_expired_train"))
        except BadRequest as e:
            if "message to edit not found" in e.message.lower():
                logger.warning(f"Failed to edit 'session expired' message for user {user_id}. The original message was already gone.")
            else:
                raise
        return None, None, None, None, None

    parts = update.callback_query.data.split("_")
    due_word_id = int(parts[2])
    tracking_id = int(parts[3]) if len(parts) > 3 else None

    notification = await db.get_due_word_notification(due_word_id)

    if not notification:
        # Since get_due_word_notification now checks the timestamp, this handles expired notifications.
        session_expired_text = localization.get_text(user.interface_language, "training_session_expired")
        try:
            await update.callback_query.edit_message_text(session_expired_text)
        except BadRequest as e:
            if "message to edit not found" in e.message.lower():
                # If the message is already gone, we just log it and move on.
                logger.warning(f"Tried to inform user {user_id} about expired session, but the message was already gone.")
                await context.bot.send_message(
                    update.callback_query.message.chat.id,
                    session_expired_text,
                    reply_markup=create_main_menu_keyboard(user.interface_language),
                )
            else:
                raise e
        return None, None, None, None, None

    if user_id != notification["user_id"]:
        logger.warning(f"User {user_id} tried to access notification {due_word_id} belonging to {notification['user_id']}")
        return None, None, None, None, None

    return user, notification, due_word_id, tracking_id, notification.get("created_at")
