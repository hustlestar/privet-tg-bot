#!/usr/bin/env python3
"""Test script to verify the start command uses the new language configuration."""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.language_config import language_config


def test_start_command_languages():
    """Test that the start command will show only configured languages."""
    print("🚀 Testing Start Command Language Configuration")
    print("=" * 50)

    print("📱 Languages that will appear in /start command:")
    print("   (Native language selection)")
    print()

    interface_keyboard = language_config.get_interface_keyboard()
    for i, (display, code) in enumerate(interface_keyboard, 1):
        print(f"   {i}. {display} (code: {code})")

    print()
    print(f"✅ Total interface languages available: {len(interface_keyboard)}")
    print()

    print("🎓 Languages that will appear for learning selection:")
    print("   (After selecting native language)")
    print()

    # Test with different native languages
    test_natives = ["english", "russian", "spanish"]

    for native in test_natives:
        if language_config.validate_interface_language(native):
            learning_keyboard = language_config.get_learning_keyboard(exclude_native=native)
            print(f"   If native = {native}:")
            for display, code in learning_keyboard:
                print(f"     • {display} (code: {code})")
            print(f"     Total: {len(learning_keyboard)} options")
            print()

    print("🔧 To change available languages, modify your .env file:")
    print("   SUPPORTED_INTERFACE_LANGUAGES=english,spanish,russian,polish")
    print("   SUPPORTED_LEARNING_LANGUAGES=english,spanish,french,german,russian,polish")


if __name__ == "__main__":
    test_start_command_languages()
