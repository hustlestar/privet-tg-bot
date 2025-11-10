"""Scheduler for sending word repetition notifications."""

import logging
import random
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import Forbidden
from telegram.ext import Application

from .config import get_config, Config
from .database import db
from .handlers.keyboards import create_main_menu_keyboard
from .local.localization import localization
from src.dao.models import UserPlan, NotificationType

logger = logging.getLogger(__name__)


async def trigger_repetition_notification_for_user(user_id: int, application: Application, force: bool = False):
    """
    Triggers a repetition notification for a single user.

    Args:
        user_id: The ID of the user to notify.
        application: The Telegram application instance.
        force: If True, ignores the usual checks (like frequency) for sending.
    """
    try:
        current_time = datetime.utcnow()
        current_hour = current_time.hour
        user = await db.get_user(user_id)
        if not user:
            return

        if not force:
            has_been_sent = await db.has_sent_notification_for_hour(user_id, NotificationType.WORD_REVIEW.value, current_hour)
            if has_been_sent:
                logger.debug(f"Skipping notification for user {user_id}, already sent for this hour.")
                return

            sent_count = await db.get_todays_notification_count(user_id, NotificationType.WORD_REVIEW.value)
            if user.plan == UserPlan.FREE and sent_count > 0:
                return
            if user.plan != UserPlan.FREE and sent_count >= user.notification_times_count:
                return

        # Check for unanswered review notifications
        unanswered_notification = await db.get_unanswered_review_notification(user_id)
        existing_word_ids = []
        should_combine_words = False
        
        if unanswered_notification:
            existing_word_ids = unanswered_notification["word_ids"]
            logger.info(f"Found unanswered notification for user {user_id} with {len(existing_word_ids)} words")
            
            # Only combine words if the total would be less than 25
            should_combine_words = len(existing_word_ids) < 25
            
            # Try to delete the old message to avoid clutter
            if unanswered_notification["message_id"]:
                try:
                    await application.bot.delete_message(chat_id=user_id, message_id=unanswered_notification["message_id"])
                    logger.info(f"Successfully deleted old notification message {unanswered_notification['message_id']} for user {user_id}")
                except Forbidden:
                    logger.warning(f"Cannot delete message for user {user_id} - bot was blocked")
                    await db.mark_user_as_blocked(user_id)
                    # Clean up the notification records since we can't send to this user
                    await db.mark_notification_as_responded(unanswered_notification["notification_id"])
                    await db.delete_due_word_notification(unanswered_notification["due_word_id"])
                    return  # Skip this user entirely
                except Exception as e:
                    logger.warning(f"Failed to delete old notification message for user {user_id}: {e}")
            
            # Clean up old records - we'll create new ones
            # Mark as replaced (not responded) with timestamp showing when we replaced it
            await db.mark_notification_as_replaced(unanswered_notification["notification_id"])
            await db.delete_due_word_notification(unanswered_notification["due_word_id"])
            logger.info(f"Replaced old notification records for user {user_id}")

        # Get words that are already in pending notifications (excluding the one we just deleted)
        pending_word_ids = await db.get_pending_notification_word_ids(user_id)

        # Get due words, excluding those that are already in pending notifications
        words = await db.get_due_words_for_user(user_id, exclude_word_ids=pending_word_ids)
        logger.info(f"Found {len(words)} new due words for user {user_id}")
        
        # Combine with existing words from unanswered notification only if appropriate
        if should_combine_words and existing_word_ids:
            # Get word details for existing_word_ids that aren't already in the new words
            new_word_ids = {w["word_id"] for w in words}
            additional_word_ids = [wid for wid in existing_word_ids if wid not in new_word_ids]
            
            if additional_word_ids:
                logger.info(f"Adding {len(additional_word_ids)} words from previous unanswered notification")
                # Fetch details for these words
                additional_words = []
                for word_id in additional_word_ids[:max(0, 25 - len(words))]:  # Keep within 25 word limit
                    word_details = await db.get_word_details(word_id)
                    if word_details:
                        additional_words.append({
                            "word_id": word_id,
                            "word": word_details["word"],
                            "short_translation": word_details["short_translation"]
                        })
                words.extend(additional_words)
                logger.info(f"Total words after combining: {len(words)}")
        elif existing_word_ids and not should_combine_words:
            logger.info(f"Not combining words because previous notification had {len(existing_word_ids)} words (>=25 limit)")
        
        if not words:
            if force:
                await application.bot.send_message(user_id, "You have no new words due for repetition right now.")
            return

        # Limit to 25 words total
        words = words[:25]
        word_ids = [w["word_id"] for w in words]
        
        # Create new notification record without message_id first
        tracking_id = await db.log_notification(user_id, NotificationType.WORD_REVIEW.value)
        due_word_id = await db.create_due_word_notification(user_id, word_ids)

        interface_lang = user.interface_language
        word_list = "\n".join([f"<b>{w['word']}</b> - {w['short_translation']}" for w in words])
        message = localization.get_text(interface_lang, "repetition_notification_body", word_list=word_list)

        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(f'✍️ {localization.get_text(interface_lang, "repetition_i_remember_button")}',
                                      callback_data=f"confirm_repetition_{due_word_id}_{tracking_id}")],
                [InlineKeyboardButton(f'💪🏻 {localization.get_text(interface_lang, "repetition_start_training_button")} 💪🏻',
                                      callback_data=f"start_review_{due_word_id}_{tracking_id}")]
            ]
        )

        try:
            sent_message = await application.bot.send_message(
                user_id,
                f"{localization.get_text(interface_lang, 'repetition_notification_title')}\n\n{message}",
                reply_markup=keyboard,
                parse_mode="HTML"
            )
            
            # Update the notification with the message_id
            await db.update_notification_message_id(tracking_id, sent_message.message_id)
            
            if force:
                await application.bot.send_message(user_id, "A test notification has been sent.")
                
        except Forbidden as e:
            logger.warning(f"User {user_id} has blocked the bot - marking as blocked")
            # Mark user as blocked in database
            await db.mark_user_as_blocked(user_id)
            # Clean up the notification we just created since we couldn't send it
            await db.mark_notification_as_responded(tracking_id)
            await db.delete_due_word_notification(due_word_id)
            return

    except Forbidden as e:
        logger.warning(f"User {user_id} has blocked the bot - marking as blocked")
        await db.mark_user_as_blocked(user_id)
    except Exception as x:
        logger.error(f"Failed to send notification to user {user_id}: {x}", exc_info=True)


async def send_repetition_notifications(application: Application):
    """
    Fetches words due for repetition and sends notifications to users,
    respecting user settings, plans, and daily limits.
    """
    try:
        now_utc = datetime.utcnow().time().replace(minute=0, second=0, microsecond=0)
        config = get_config()
        try:
            default_time = datetime.strptime(config.default_notification_time, "%H:%M").time()
        except ValueError:
            logger.error("Invalid default_notification_time format. Please use HH:MM.")
            return

        user_ids = await db.get_users_for_notification(now_utc, default_time)
        if user_ids:
            logger.info(f"Sending notifications to {len(user_ids)} users.")

        for user_id in user_ids:
            await trigger_repetition_notification_for_user(user_id, application)

    except Exception as e:
        logger.error(f"Error in send_repetition_notifications: {e}", exc_info=True)


async def cleanup_old_notifications():
    """Clean up old due word notifications that are past the 48-hour edit window."""
    try:
        # We clean up notifications older than 72 hours, as users have this long to respond.
        deleted_count = await db.delete_old_due_word_notifications(interval_hours=72)
        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} old due word notifications.")
    except Exception as e:
        logger.error(f"Error in cleanup_old_notifications: {e}", exc_info=True)


async def send_inactivity_notifications(application: Application):
    """Send inactivity notifications to users who haven't added words recently."""
    config = get_config()
    inactivity_days = config.inactivity_notification_days

    users = await db.user_dao.get_all_users()
    for user in users:
        last_added_date = await db.user_dao.get_last_word_added_date(user.user_id)

        if last_added_date is None:
            # User has never added a word, check created_at
            if user.created_at and (datetime.utcnow() - user.created_at).days >= inactivity_days:
                days_since_creation = (datetime.utcnow() - user.created_at).days
                await _send_inactivity_reminder(application, user, days_since_creation)
        elif (datetime.utcnow() - last_added_date).days >= inactivity_days:
            days_since_last_word = (datetime.utcnow() - last_added_date).days
            await _send_inactivity_reminder(application, user, days_since_last_word)


async def _send_inactivity_reminder(application, user, days_inactive):
    """Send a single inactivity reminder to a user."""
    # Delete previous inactivity notification
    previous_notification_id = await db.notification_dao.get_and_delete_inactivity_notification(user.user_id)
    if previous_notification_id:
        try:
            await application.bot.delete_message(chat_id=user.user_id, message_id=previous_notification_id)
        except Exception as e:
            logger.error(f"Failed to delete previous inactivity notification for user {user.user_id}: {e}")

    # Send new notification
    interface_lang = user.interface_language
    reminder_messages = [
        localization.get_text(interface_lang, "inactivity_reminder_1"),
        localization.get_text(interface_lang, "inactivity_reminder_2", days=days_inactive),
        localization.get_text(interface_lang, "inactivity_reminder_3", days=days_inactive),
    ]
    message_text = random.choice(reminder_messages)

    keyboard = create_main_menu_keyboard(interface_lang)
    try:
        sent_message = await application.bot.send_message(
            user.user_id, message_text, reply_markup=keyboard
        )
        await db.notification_dao.log_notification(
            user.user_id, NotificationType.INACTIVE_BUDGE.value, sent_message.message_id
        )
    except Exception as e:
        logger.error(f"Failed to send inactivity notification to user {user.user_id}: {e}")


def start_scheduler(application: Application):
    """
    Initializes and starts the scheduler.
    """
    config: Config = get_config()
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_repetition_notifications, trigger="interval", minutes=config.repetition_notification_interval_minutes, args=[application])
    scheduler.add_job(cleanup_old_notifications, trigger="interval", hours=config.cleanup_old_notifications_interval_hours)

    # Schedule inactivity notifications
    try:
        notification_time = datetime.strptime(config.inactivity_notification_time, "%H:%M").time()
        scheduler.add_job(
            send_inactivity_notifications,
            trigger="cron",
            day_of_week="sun",
            hour=notification_time.hour,
            minute=notification_time.minute,
            args=[application],
        )
    except ValueError:
        logger.error("Invalid inactivity_notification_time format. Please use HH:MM.")

    scheduler.start()
    logger.info("Scheduler started.")
