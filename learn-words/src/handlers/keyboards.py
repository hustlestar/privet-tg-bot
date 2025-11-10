from typing import Optional, Tuple
from datetime import datetime, timedelta

from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from src.local.localization import localization
from src.dao.models import TrainingExercise, TrainingType, User, UserPlan
from src.timezones import UTC_OFFSETS
from src.time_utils import convert_utc_to_local_time


def get_continue_keyboard(
    is_correct: bool = True,
    interface_lang: str = "english",
    attempt_id: Optional[int] = None,
    word: Optional[int] = None,
    previous_repetition_level: Optional[int] = None,
) -> InlineKeyboardMarkup:
    """Create keyboard for continuing training."""
    keyboard = [
        [
            InlineKeyboardButton(
                localization.get_text(interface_lang, "another_word_button"),
                callback_data="train_continue",
            ),
            InlineKeyboardButton(
                localization.get_text(interface_lang, "stop_training_button"),
                callback_data="train_stop",
            ),
        ],
    ]

    # Add "Mark as correct answer" button only when the answer was incorrect
    if not is_correct and attempt_id is not None and previous_repetition_level is not None:
        callback_data = f"mark_correct:{attempt_id}:{previous_repetition_level}"
        incorrect_keyboard = [
            InlineKeyboardButton(
                localization.get_text(interface_lang, "mark_as_correct_button"),
                callback_data=callback_data,
            )
        ]
        if word:
            delete_word_text = localization.get_text(interface_lang, "delete_from_vocabulary_button")
            delete_word_button = InlineKeyboardButton(delete_word_text, callback_data=f"delete_word_train_{word}")
            incorrect_keyboard.append(delete_word_button)
        keyboard.insert(0, incorrect_keyboard)

    return InlineKeyboardMarkup(keyboard)


def create_exercise_keyboard(exercise: TrainingExercise, interface_lang: str) -> Tuple[InlineKeyboardMarkup, bool]:
    """Create inline keyboard for multiple choice exercises."""
    idk_button_text = localization.get_text(interface_lang, "i_dont_know_button")
    idk_callback_data = f"idk_{exercise.word.id}"
    if exercise.training_type not in [TrainingType.MULTIPLE_CHOICE, TrainingType.SYNONYM_CHOICE] or not exercise.options:
        return (
            InlineKeyboardMarkup([[InlineKeyboardButton(idk_button_text, callback_data=idk_callback_data)]]),
            False,
        )

    keyboard = []
    for i, option in enumerate(exercise.options):
        callback_data = f"answer_{i}_{exercise.word.id}"
        keyboard.append([InlineKeyboardButton(option, callback_data=callback_data)])

    keyboard.append([InlineKeyboardButton(idk_button_text, callback_data=idk_callback_data)])

    return InlineKeyboardMarkup(keyboard), True


def create_main_menu_keyboard(interface_language: str) -> InlineKeyboardMarkup:
    """Create main menu keyboard with localized text."""
    train_text = localization.get_text(interface_language, "start_training")
    vocab_text = localization.get_text(interface_language, "view_vocabulary")
    settings_text = localization.get_text(interface_language, "change_settings")

    keyboard = [
        [InlineKeyboardButton(train_text, callback_data="train_start")],
        [InlineKeyboardButton(vocab_text, callback_data="view_vocabulary")],
        [InlineKeyboardButton(settings_text, callback_data="show_settings")],
    ]
    return InlineKeyboardMarkup(keyboard)


def create_notification_time_keyboard(user: User) -> InlineKeyboardMarkup:
    """Create a static keyboard for managing notification times."""
    keyboard = []
    existing_local_times = set(convert_utc_to_local_time(t, user.timezone) for t in (user.notification_times or []))

    # Create a grid of buttons from 08:00 to 23:00
    for hour in range(8, 24, 4):
        row = []
        for i in range(4):
            if hour + i <= 23:
                time_str = f"{hour + i:02d}:00"
                if time_str in existing_local_times:
                    # This time is already set, so show a "remove" button
                    text = f"🔕 {time_str}"
                    callback_data = f"remove_notification_time_{time_str}"
                else:
                    # This time is not set, so show an "add" button
                    text = time_str
                    callback_data = f"set_notification_time_{time_str}"
                row.append(InlineKeyboardButton(text, callback_data=callback_data))
        if row:
            keyboard.append(row)

    # Add premium button if user has reached their limit
    if user.plan == UserPlan.FREE and len(user.notification_times) >= 1:
        premium_text = localization.get_text(user.interface_language, "add_another_time_premium")
        keyboard.append([InlineKeyboardButton(premium_text, callback_data="premium_subscribe")])

    # Add back button
    back_text = localization.get_text(user.interface_language, "back")
    settings_text = localization.get_text(user.interface_language, "settings")
    keyboard.append([InlineKeyboardButton(f"« {back_text} {settings_text}", callback_data="show_settings")])

    return InlineKeyboardMarkup(keyboard)


def create_timezone_keyboard(user: User) -> InlineKeyboardMarkup:
    """Create the keyboard for setting the user's timezone."""
    keyboard = []

    now_utc = datetime.utcnow()

    # Create a 3-column grid of time buttons to fit all 27 offsets
    num_columns = 3
    for i in range(0, len(UTC_OFFSETS), num_columns):
        row = []
        for j in range(num_columns):
            offset_index = i + j
            if offset_index < len(UTC_OFFSETS):
                offset = UTC_OFFSETS[offset_index]

                local_time = now_utc + timedelta(hours=offset)
                time_str = local_time.strftime("%H:%M")

                offset_str = f"UTC{offset:+}"

                row.append(InlineKeyboardButton(time_str, callback_data=f"set_timezone_{offset_str}"))
        if row:
            keyboard.append(row)

    # Add back button
    back_text = localization.get_text(user.interface_language, "back")
    settings_text = localization.get_text(user.interface_language, "settings")
    keyboard.append([InlineKeyboardButton(f"« {back_text} {settings_text}", callback_data="show_settings")])

    return InlineKeyboardMarkup(keyboard)
