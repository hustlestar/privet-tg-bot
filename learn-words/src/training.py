"""Training system for the Learn Words bot."""

import random
from typing import Optional

from src.local.localization import localization, get_translated_value
from .database import db
from src.dao.models import Word, TrainingType, TrainingExercise, TrainingAttempt


class TrainingSystem:
    """Manages training exercises and word selection."""

    async def get_training_exercise(self, user_id: int, interface_language: str) -> Optional[TrainingExercise]:  # Added interface_language
        """Get a training exercise for the user."""

        # Get a word for training based on priority
        word_data = await db.get_word_for_training(user_id)
        if not word_data:
            return None

        word, stats = word_data

        # Select training type based on translation direction and user preferences
        training_type = self._select_training_type(word)

        # Create exercise based on type
        if training_type == TrainingType.DIRECT_TRANSLATION:
            return await self._create_direct_translation_exercise(word, interface_language)
        elif training_type == TrainingType.MULTIPLE_CHOICE:
            return await self._create_multiple_choice_exercise(word, user_id, interface_language)
        elif training_type == TrainingType.REVERSE_TRANSLATION:
            return await self._create_reverse_translation_exercise(word, interface_language)
        elif training_type == TrainingType.SYNONYM_CHOICE:
            return await self._create_synonym_choice_exercise(word, user_id, interface_language)

        return None

    async def get_review_exercise(self, user_id: int, interface_language: str, word_id: int) -> Optional[TrainingExercise]:
        """Get a review exercise for a specific word."""
        word_data = await db.get_word_by_id_for_user(user_id, word_id)
        if not word_data:
            return None

        word, stats = word_data

        # Select training type and create exercise
        training_type = self._select_training_type(word)
        if training_type == TrainingType.DIRECT_TRANSLATION:
            return await self._create_direct_translation_exercise(word, interface_language)
        elif training_type == TrainingType.MULTIPLE_CHOICE:
            return await self._create_multiple_choice_exercise(word, user_id, interface_language)
        elif training_type == TrainingType.REVERSE_TRANSLATION:
            return await self._create_reverse_translation_exercise(word, interface_language)
        elif training_type == TrainingType.SYNONYM_CHOICE:
            return await self._create_synonym_choice_exercise(word, user_id, interface_language)

        return None

    def _select_training_type(self, word: Word) -> TrainingType:
        """Select training type based on translation direction and synonym considerations."""
        # Check if word has synonyms (multiple translations)
        has_synonyms = False
        if hasattr(word, "synonyms_learning") and word.synonyms_learning:
            has_synonyms = len(word.synonyms_learning) > 0

        # Training type selection logic based on user requirements:
        # 1. Always use training tasks (testing) as default
        # 2. Avoid write tasks when target has many synonyms (would be too long)
        # 3. Keep write tasks only for synonyms -> English direction

        if has_synonyms:
            return random.choices(
                [
                    TrainingType.SYNONYM_CHOICE,
                    TrainingType.MULTIPLE_CHOICE,
                    TrainingType.DIRECT_TRANSLATION,
                    TrainingType.REVERSE_TRANSLATION,
                ],
                weights=[0.5, 0.2, 0.15, 0.15],
            )[0]

        else:
            # No synonyms or simple case: use all training types but prefer testing
            return random.choices(
                [
                    TrainingType.MULTIPLE_CHOICE,
                    TrainingType.DIRECT_TRANSLATION,
                    TrainingType.REVERSE_TRANSLATION,
                ],
                weights=[0.5, 0.3, 0.2],
            )[0]

    async def _create_direct_translation_exercise(self, word: Word, interface_language: str) -> TrainingExercise:  # Added interface_language
        """Create a direct translation exercise (learning language -> native language)."""
        question = localization.get_text(interface_language, "training_question_translate_word", word=word.word)
        correct_answer = word.short_translation

        return TrainingExercise(
            word=word,
            training_type=TrainingType.DIRECT_TRANSLATION,
            question=question,
            correct_answer=correct_answer,
        )

    async def _create_multiple_choice_exercise(
        self, word: Word, user_id: int, interface_language: str
    ) -> TrainingExercise:  # Added interface_language
        """Create a multiple choice exercise."""
        question = localization.get_text(interface_language, "training_question_what_does_it_mean", word=word.word)
        correct_answer = word.short_translation

        # Get distractors from user's vocabulary
        distractors = await db.get_random_translations_for_distractors(user_id, word.id, word.to_language, 3)

        # If not enough distractors, add some generic ones
        if len(distractors) < 3:
            generic_distractors = [
                "house", "water", "food", "time", "person", "place", "thing",
                "good", "bad", "big", "small", "new", "old", "run", "walk", "see", "hear"
            ]
            needed = 3 - len(distractors)
            # Make sure we don't add the correct answer as a generic distractor
            filtered_generic = [d for d in generic_distractors if d.lower() != correct_answer.lower()]
            additional = random.sample(filtered_generic, min(needed, len(filtered_generic)))
            distractors.extend(additional)

        # Ensure we don't have duplicates and the correct answer isn't in distractors
        distractors = [d for d in distractors if d.lower() != correct_answer.lower()][:3]

        # Create options list and shuffle
        options = [correct_answer] + distractors
        random.shuffle(options)

        return TrainingExercise(
            word=word,
            training_type=TrainingType.MULTIPLE_CHOICE,
            question=question,
            correct_answer=correct_answer,
            options=options,
        )

    async def _create_reverse_translation_exercise(self, word: Word, interface_language: str) -> TrainingExercise:  # Added interface_language
        """Create a reverse translation exercise (native language -> learning language)."""
        translated_from_language = get_translated_value(word.from_language, interface_language)

        # Helper to remove last char if it's 'й'
        def remove_last_char_if_specific(s, char_to_remove):
            if s.endswith(char_to_remove):
                return s[:-1]
            return s

        # Decline the language name for the question
        if interface_language == "russian":
            translated_from_language = remove_last_char_if_specific(translated_from_language, "й")
        
        question = localization.get_text(
            interface_language,
            "training_question_how_to_say",
            short_translation=word.short_translation,
            from_language=translated_from_language,
        )
        correct_answer = word.word

        return TrainingExercise(
            word=word,
            training_type=TrainingType.REVERSE_TRANSLATION,
            question=question,
            correct_answer=correct_answer,
        )

    async def _create_synonym_choice_exercise(self, word: Word, user_id: int, interface_language: str) -> TrainingExercise:
        """Create a multiple choice exercise for guessing a word by its synonyms."""
        if not word.synonyms_learning:
            # Fallback to a different exercise if there are no synonyms
            return await self._create_multiple_choice_exercise(word, user_id, interface_language)

        synonyms_str = ", ".join(word.synonyms_learning)
        question = localization.get_text(interface_language, "training_question_choose_synonym", synonyms=synonyms_str)
        correct_answer = word.word

        # Get distractors (other words in the same language)
        distractor_words = await db.get_random_words_for_synonym_distractors(
            user_id,
            word.id,
            from_language=word.from_language,
            learning_language=word.to_language,
            count=3,
            exclude_words=[word.word],
        )

        # Process distractors to get the correct string for the option
        distractors = []
        for distractor_word in distractor_words:
            if distractor_word.to_language == word.to_language:
                distractors.append(distractor_word.word)
            else:
                distractors.append(distractor_word.short_translation)

        # Final check to ensure no duplicates and correct answer isn't in distractors
        distractors = [d for d in distractors if d.lower() != correct_answer.lower()][:3]

        options = [correct_answer] + distractors
        random.shuffle(options)

        return TrainingExercise(
            word=word,
            training_type=TrainingType.SYNONYM_CHOICE,
            question=question,
            correct_answer=correct_answer,
            options=options,
        )

    def check_answer(self, user_answer: str, correct_answer: str, training_type: TrainingType) -> bool:
        """Check if the user's answer is correct."""
        user_answer = user_answer.lower().strip()
        correct_answer = correct_answer.lower().strip()

        if training_type in [TrainingType.MULTIPLE_CHOICE, TrainingType.SYNONYM_CHOICE]:
            # For multiple choice, exact match
            return user_answer == correct_answer
        else:
            # For text input, allow some flexibility
            # Check exact match first
            if user_answer == correct_answer:
                return True

            # Check if user answer is contained in correct answer or vice versa
            # This helps with articles, plurals, etc.
            if len(user_answer) > 2 and len(correct_answer) > 2:
                if user_answer in correct_answer or correct_answer in user_answer:
                    return True

            # Check for common variations (remove articles, etc.)
            user_clean = self._clean_answer(user_answer)
            correct_clean = self._clean_answer(correct_answer)

            return user_clean == correct_clean

    def _clean_answer(self, answer: str) -> str:
        """Clean answer for comparison (remove articles, extra spaces, etc.)."""
        # Remove common articles and prepositions
        words_to_remove = {
            "the",
            "a",
            "an",
            "to",
            "of",
            "in",
            "on",
            "at",
            "for",
            "with",
            "by",
        }

        words = answer.split()
        cleaned_words = [word for word in words if word not in words_to_remove]

        return " ".join(cleaned_words)

    async def record_attempt(
        self,
        user_id: int,
        word_id: int,
        training_type: TrainingType,
        is_correct: bool,
        is_review_session: bool = False,
    ) -> int:
        """Record a training attempt. Returns attempt ID."""
        attempt = TrainingAttempt(
            id=None,
            user_id=user_id,
            word_id=word_id,
            training_type=training_type,
            is_correct=is_correct,
        )

        attempt_id = await db.record_training_attempt(attempt, is_review_session)
        return attempt_id

    async def mark_attempt_correct(self, attempt_id: int, previous_repetition_level: int) -> bool:
        """Mark a training attempt as correct. Returns success status."""
        return await db.update_training_attempt_to_correct(attempt_id, previous_repetition_level)

    def get_feedback_message(
        self,
        is_correct: bool,
        correct_answer: str,
        word: Word,
        training_type: TrainingType,
        interface_lang: str = "english",
    ) -> str:
        """Generate feedback message for the user."""
        base_message = ""
        if is_correct:
            messages = [
                localization.get_text(
                    interface_lang,
                    "correct_answer_1",
                    correct_answer=word.short_translation,
                    word=word.word,
                ),
                localization.get_text(
                    interface_lang,
                    "correct_answer_2",
                    correct_answer=word.short_translation,
                    word=word.word,
                ),
                localization.get_text(
                    interface_lang,
                    "correct_answer_3",
                    correct_answer=word.short_translation,
                    word=word.word,
                ),
                localization.get_text(
                    interface_lang,
                    "correct_answer_4",
                    correct_answer=word.short_translation,
                    word=word.word,
                ),
                localization.get_text(
                    interface_lang,
                    "correct_answer_5",
                    correct_answer=word.short_translation,
                    word=word.word,
                ),
            ]
            base_message = random.choice(messages)
        else:
            meaning = word.medium_data.get("meaning", "")
            base_message = localization.get_text(
                interface_lang,
                "incorrect_answer",
                correct_answer=word.short_translation,
                meaning=meaning,
                word=word.word,
            )

        if training_type == TrainingType.SYNONYM_CHOICE and word.synonyms_learning:
            synonyms_str = ", ".join(word.synonyms_learning)
            synonyms_label = localization.get_text(interface_lang, "synonyms")
            base_message += f"\n\n{synonyms_label}: <u><b>{synonyms_str}</b></u>"

        return base_message


# Global training system instance
training_system = TrainingSystem()
