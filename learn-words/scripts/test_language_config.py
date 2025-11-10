#!/usr/bin/env python3
"""Test script for the new .env-based language configuration system."""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.language_config import language_config
from src.config import get_config


def test_language_configuration():
    """Test the language configuration system."""
    print("🧪 Testing .env Language Configuration System")
    print("=" * 50)

    # Test configuration loading
    config = get_config()
    print(f"✅ Configuration loaded successfully")
    print(f"   Interface languages: {config.supported_interface_languages}")
    print(f"   Learning languages: {config.supported_learning_languages}")
    print()

    # Test language validation
    print("🔍 Testing Language Validation")
    print("-" * 30)

    # Test valid interface languages
    valid_interface = ["english", "spanish", "russian", "polish"]
    for lang in valid_interface:
        result = language_config.validate_interface_language(lang)
        print(f"   Interface '{lang}': {'✅' if result else '❌'}")

    # Test invalid interface language
    invalid_interface = "klingon"
    result = language_config.validate_interface_language(invalid_interface)
    print(f"   Interface '{invalid_interface}': {'✅' if result else '❌'} (should be ❌)")
    print()

    # Test valid learning languages
    valid_learning = [
        "english",
        "spanish",
        "french",
        "german",
        "italian",
        "portuguese",
        "russian",
        "polish",
    ]
    for lang in valid_learning:
        result = language_config.validate_learning_language(lang)
        print(f"   Learning '{lang}': {'✅' if result else '❌'}")

    # Test invalid learning language
    invalid_learning = "elvish"
    result = language_config.validate_learning_language(invalid_learning)
    print(f"   Learning '{invalid_learning}': {'✅' if result else '❌'} (should be ❌)")
    print()

    # Test keyboard generation
    print("⌨️  Testing Keyboard Generation")
    print("-" * 30)

    interface_keyboard = language_config.get_interface_keyboard()
    print(f"   Interface keyboard ({len(interface_keyboard)} options):")
    for display, code in interface_keyboard:
        print(f"     {display} -> {code}")
    print()

    learning_keyboard = language_config.get_learning_keyboard()
    print(f"   Learning keyboard ({len(learning_keyboard)} options):")
    for display, code in learning_keyboard:
        print(f"     {display} -> {code}")
    print()

    # Test learning keyboard with exclusion
    excluded_native = "english"
    learning_keyboard_filtered = language_config.get_learning_keyboard(exclude_native=excluded_native)
    print(f"   Learning keyboard excluding '{excluded_native}' ({len(learning_keyboard_filtered)} options):")
    for display, code in learning_keyboard_filtered:
        print(f"     {display} -> {code}")
    print()

    # Test language combination validation
    print("🔗 Testing Language Combination Validation")
    print("-" * 40)

    test_combinations = [
        ("english", "spanish"),  # Valid
        ("russian", "english"),  # Valid
        ("english", "english"),  # Invalid (same language)
        ("english", "klingon"),  # Invalid (unsupported learning)
        ("elvish", "spanish"),  # Invalid (unsupported native)
    ]

    for native, learning in test_combinations:
        result = language_config.is_language_combination_valid(native, learning)
        status = "✅" if result else "❌"
        print(f"   {native} -> {learning}: {status}")
    print()

    # Test fallback languages
    print("🔄 Testing Fallback Languages")
    print("-" * 25)

    fallback_native = language_config.get_fallback_native_language()
    print(f"   Fallback native: {fallback_native}")

    fallback_learning = language_config.get_fallback_learning_language()
    print(f"   Fallback learning: {fallback_learning}")

    fallback_learning_excluded = language_config.get_fallback_learning_language(exclude_native="spanish")
    print(f"   Fallback learning (excluding spanish): {fallback_learning_excluded}")
    print()

    print("🎉 All tests completed!")


if __name__ == "__main__":
    test_language_configuration()
