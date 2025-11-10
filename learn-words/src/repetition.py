"""Spaced repetition logic for the Learn Words bot."""

from datetime import datetime, timedelta
from typing import List

# --- Repetition Intervals ---
# A list of intervals in days for each repetition level.
REPETITION_INTERVALS: List[int] = [1, 3, 7, 14, 30, 90, 180, 365, 730, 1095, 1460]


def get_next_review_date(repetition_level: int, is_correct: bool, is_review_session: bool = False) -> (int, datetime):
    """
    Calculate the next review date based on the user's answer.

    Args:
        repetition_level: The current repetition level of the word.
        is_correct: Whether the user's answer was correct.
        is_review_session: Whether this is part of a review session.

    Returns:
        A tuple containing the new repetition level and the next review date.
    """
    if is_correct:
        # If the answer is correct, advance to the next level.
        if is_review_session:
            new_level = min(repetition_level + 1, len(REPETITION_INTERVALS) - 1)
        else:
            new_level = min(repetition_level + 1, 5) if repetition_level < 5 else repetition_level
    else:
        # If the answer is incorrect, reset the level.
        new_level = max(repetition_level - 1 if repetition_level < 3 else repetition_level - 2, 0)

    # Calculate the next review date by adding the interval to the current date.
    days_to_add = REPETITION_INTERVALS[new_level]
    next_review_at = datetime.now() + timedelta(days=days_to_add)

    return new_level, next_review_at
