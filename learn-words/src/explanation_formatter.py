"""Explanation formatting utilities based on user language preferences."""

from typing import Dict, Any
from src.dao.models import ExplanationLanguage, User
from .local.localization import localization, get_translated_value
from src.config import get_config
from src.time_utils import convert_utc_to_local_time


class ExplanationFormatter:
    """Format explanations based on user's explanation language preference."""

    @staticmethod
    def format_explanation(word_data: Dict[str, Any], user: User, response_mode: str = "medium") -> str:
        """Format explanation based on user's explanation language preference."""
        original_word = word_data.get("word", "")
        translation = word_data.get("short_translation", "")
        result = f"<b>{original_word}</b> - " + f"{translation}\n"

        if response_mode == "short":
            return result

        elif response_mode == "medium":
            medium_data = word_data.get("medium_data", {})

            # Always show original and translation for native explanations
            if user.explanation_language == ExplanationLanguage.NATIVE:
                source_lang = word_data.get("source_language", user.learning_language)
                target_lang = word_data.get("target_language", user.interface_language)

                result += f"🔄{source_lang} -> {target_lang}\n\n"

                # Add native language explanation
                meaning = medium_data.get("meaning_native", medium_data.get("meaning", ""))
                if meaning:
                    result += meaning

            elif user.explanation_language == ExplanationLanguage.LEARNING:
                meaning = medium_data.get("meaning_learning", medium_data.get("meaning", ""))
                result += f"\n<b>{localization.get_text(user.interface_language, 'meaning')}:</b> {meaning}"

            else:  # MIXED
                source_lang = word_data.get("source_language", user.learning_language)
                target_lang = word_data.get("target_language", user.interface_language)

                # Show translation direction for mixed mode too
                result += f"🔄{source_lang} -> {target_lang}\n\n"

                meaning_native = medium_data.get("meaning_native", medium_data.get("meaning", ""))
                meaning_learning = medium_data.get("meaning_learning", medium_data.get("meaning", ""))

                if meaning_native:
                    result += f"📝 <b>{user.interface_language}:</b> {meaning_native}"
                if meaning_learning and meaning_learning != meaning_native:
                    result += f"\n🎯 <b>{user.learning_language}:</b> {meaning_learning}"

            # Add synonyms if available
            synonyms_learning = word_data.get("synonyms_learning", [])
            if synonyms_learning:
                result += f"\n🔗 <b>{localization.get_text(user.interface_language, 'synonyms')}:</b> {', '.join(synonyms_learning[:3])}"

            # Add pronunciation if available
            pronunciation = medium_data.get("pronunciation", "")
            if pronunciation:
                result += f"\n🔊 {pronunciation}"

            # Add grammar info if available
            grammar_info = medium_data.get("grammar_info", "")
            if grammar_info:
                result += f"\n📝 {grammar_info}"

            # Add example
            example = medium_data.get("example", "")
            if example:
                result += f"\n💡 {example}"

            return result

        else:  # long mode
            long_data = word_data.get("long_data", {})

            # Add "word - translation" header as requested
            original_word = word_data.get("word", "")
            translation = word_data.get("short_translation", "")
            result = f"<b>{original_word}</b> - {translation}\n\n"

            # Start with translations
            translations = long_data.get("translations", [])
            result += f"<b>{localization.get_text(user.interface_language, 'translations')}:</b> {', '.join(translations[:5])}"

            # Add meanings based on preference
            if user.explanation_language == ExplanationLanguage.NATIVE:
                meanings = long_data.get("meanings_native", long_data.get("meanings", []))
                if meanings:
                    result += f"\n\n<b>{localization.get_text(user.interface_language, 'meanings')} ({user.interface_language}):</b>"
                    for i, meaning in enumerate(meanings[:3], 1):
                        result += f"\n{i}. {meaning}"
            elif user.explanation_language == ExplanationLanguage.LEARNING:
                meanings = long_data.get("meanings_learning", long_data.get("meanings", []))
                if meanings:
                    result += f"\n\n<b>{localization.get_text(user.learning_language, 'meanings')} ({user.learning_language}):</b>"
                    for i, meaning in enumerate(meanings[:3], 1):
                        result += f"\n{i}. {meaning}"
            else:  # MIXED
                meanings_native = long_data.get("meanings_native", long_data.get("meanings", []))
                meanings_learning = long_data.get("meanings_learning", long_data.get("meanings", []))

                if meanings_native:
                    result += f"\n\n<b>{localization.get_text(user.interface_language, 'meanings')} ({user.interface_language}):</b>"
                    for i, meaning in enumerate(meanings_native[:2], 1):
                        result += f"\n{i}. {meaning}"

                if meanings_learning and meanings_learning != meanings_native:
                    result += f"\n\n<b>{localization.get_text(user.learning_language, 'meanings')} ({user.learning_language}):</b>"
                    for i, meaning in enumerate(meanings_learning[:2], 1):
                        result += f"\n{i}. {meaning}"

            # Add synonyms
            synonyms_learning = word_data.get("synonyms_learning", [])
            if synonyms_learning:
                result += f"\n\n<b>{localization.get_text(user.learning_language, 'synonyms')}:</b> {', '.join(synonyms_learning[:5])}"

            # Add examples
            examples = long_data.get("examples", [])
            if examples:
                result += f"\n\n<b>{localization.get_text(user.interface_language, 'examples')}:</b>"
                for i, example in enumerate(examples[:3], 1):
                    result += f"\n{i}. {example}"

            # Add cultural context
            cultural_context = long_data.get("cultural_context", long_data.get("context", ""))
            if cultural_context:
                result += f"\n\n<b>{localization.get_text(user.interface_language, 'cultural_context')}:</b> {cultural_context}"

            # Add grammar details
            grammar_details = long_data.get("grammar_details", "")
            if grammar_details:
                result += f"\n\n<b>{localization.get_text(user.interface_language, 'grammar')}:</b> {grammar_details}"

            # Add pronunciation guide
            pronunciation_guide = long_data.get("pronunciation_guide", "")
            if pronunciation_guide:
                result += f"\n\n<b>{localization.get_text(user.interface_language, 'pronunciation')}:</b> {pronunciation_guide}"

            # Add usage notes
            usage_notes = long_data.get("usage_notes", "")
            if usage_notes:
                result += f"\n\n<b>{localization.get_text(user.interface_language, 'usage_notes')}:</b> {usage_notes}"

            return result

    @staticmethod
    def get_explanation_language_display(explanation_language: ExplanationLanguage, interface_language: str = "english") -> str:
        """Get display text for explanation language preference."""
        if explanation_language == ExplanationLanguage.NATIVE:
            return localization.get_text(interface_language, "native_language_easier")
        elif explanation_language == ExplanationLanguage.LEARNING:
            return localization.get_text(interface_language, "learning_language_immersive")
        else:  # MIXED
            return localization.get_text(interface_language, "mixed_mode_description")

    @staticmethod
    def format_settings_display(user: User) -> str:
        """Format user settings for display."""
        config = get_config()

        # Timezone display
        timezone_str = user.timezone or localization.get_text(user.interface_language, "not_set")

        # Notification settings display
        if user.notification_times:
            # Convert UTC times to user's timezone
            if user.timezone and user.timezone != "UTC":
                local_times = []
                for utc_time in sorted(user.notification_times):
                    local_time = convert_utc_to_local_time(utc_time, user.timezone)
                    local_times.append(local_time)
                notification_times_str = ", ".join(local_times)
            else:
                notification_times_str = ", ".join(sorted(user.notification_times))
        else:
            # If no times set, show default time in user's timezone
            if user.timezone and user.timezone != "UTC":
                local_default = convert_utc_to_local_time(config.default_notification_time, user.timezone)
                notification_times_str = local_default
            else:
                notification_times_str = f"{config.default_notification_time} UTC"

        return f"""<b>{localization.get_text(user.interface_language, 'your_current_settings')}:</b>

🌍 <b>{localization.get_text(user.interface_language, 'interface_language_label')}:</b> {get_translated_value(user.interface_language, user.interface_language)}
🎯 <b>{localization.get_text(user.interface_language, 'learning_language_label')}:</b> {get_translated_value(user.learning_language, user.interface_language)}
💬 <b>{localization.get_text(user.interface_language, 'explanation_language_label')}:</b> {get_translated_value(user.explanation_language.value, user.interface_language)}
📝 <b>{localization.get_text(user.interface_language, 'response_mode_label')}:</b> {get_translated_value(user.response_mode.value, user.interface_language)}
🕒 <b>{localization.get_text(user.interface_language, 'timezone_label')}:</b> {timezone_str}
🔔 <b>{localization.get_text(user.interface_language, 'notification_times_label')}:</b> {notification_times_str}

"""


# Global formatter instance
explanation_formatter = ExplanationFormatter()
