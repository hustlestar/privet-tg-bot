"""User state management for the Learn Words bot."""

from typing import Dict, Any


class BotStates:
    """Bot conversation states."""

    WAITING_NATIVE_LANGUAGE = "waiting_native_language"
    WAITING_LEARNING_LANGUAGE = "waiting_learning_language"
    WAITING_RESPONSE_MODE = "waiting_response_mode"
    TRAINING_ACTIVE = "training_active"
    WAITING_TRAINING_ANSWER = "waiting_training_answer"
    SENTENCE_SELECTION_ACTIVE = "sentence_selection_active"
    REVIEW_SESSION_ACTIVE = "review_session_active"


# User state tracking
user_states: Dict[int, Dict[str, Any]] = {}
