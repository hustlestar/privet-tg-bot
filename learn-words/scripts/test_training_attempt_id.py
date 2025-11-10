#!/usr/bin/env python3
"""
Test script for training attempt ID functionality.

This script tests the new training attempt ID system to ensure it works correctly.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database import Database
from src.training import TrainingSystem
from src.dao.models import TrainingType


async def test_training_attempt_id_flow():
    """Test the complete training attempt ID flow."""
    print("Testing Training Attempt ID Functionality")
    print("=" * 50)

    # Initialize components
    db = Database()
    training_system = TrainingSystem()

    try:
        await db.connect()
        print("✓ Database connection established")

        # Test 1: Record a training attempt and get ID
        print("\n1. Testing record_attempt() returns attempt ID...")
        user_id = 12345  # Test user ID
        word_id = 1  # Test word ID
        training_type = TrainingType.TRANSLATION
        is_correct = False  # Incorrect attempt initially

        attempt_id = await training_system.record_attempt(user_id, word_id, training_type, is_correct)
        print(f"   ✓ Recorded attempt with ID: {attempt_id}")
        assert isinstance(attempt_id, int), "Attempt ID should be an integer"

        # Test 2: Test keyboard generation with attempt ID
        print("\n2. Testing get_continue_keyboard() with attempt ID...")
        keyboard = get_continue_keyboard(is_correct=False, interface_lang="english", attempt_id=attempt_id)

        # Check if the keyboard has the mark_correct button with attempt ID
        found_mark_correct = False
        for row in keyboard.inline_keyboard:
            for button in row:
                if button.callback_data and button.callback_data.startswith("mark_correct:"):
                    found_mark_correct = True
                    callback_attempt_id = int(button.callback_data.split(":")[1])
                    assert callback_attempt_id == attempt_id, f"Callback attempt ID {callback_attempt_id} should match {attempt_id}"
                    print(f"   ✓ Found mark_correct button with attempt ID: {callback_attempt_id}")
                    break

        assert found_mark_correct, "Should have mark_correct button for incorrect answers"

        # Test 3: Test marking attempt as correct
        print("\n3. Testing mark_attempt_correct()...")
        success = await training_system.mark_attempt_correct(attempt_id)
        print(f"   ✓ Mark attempt correct result: {success}")
        assert success, "Should successfully mark attempt as correct"

        # Test 4: Try to mark the same attempt as correct again (should fail)
        print("\n4. Testing duplicate mark_attempt_correct()...")
        success_duplicate = await training_system.mark_attempt_correct(attempt_id)
        print(f"   ✓ Duplicate mark attempt result: {success_duplicate}")
        assert not success_duplicate, "Should not allow marking already correct attempt"

        # Test 5: Test keyboard generation for correct answers (no attempt ID needed)
        print("\n5. Testing get_continue_keyboard() for correct answers...")
        keyboard_correct = get_continue_keyboard(is_correct=True, interface_lang="english")

        # Check that there's no mark_correct button for correct answers
        found_mark_correct_for_correct = False
        for row in keyboard_correct.inline_keyboard:
            for button in row:
                if button.callback_data and button.callback_data.startswith("mark_correct:"):
                    found_mark_correct_for_correct = True
                    break

        assert not found_mark_correct_for_correct, "Should not have mark_correct button for correct answers"
        print("   ✓ No mark_correct button for correct answers")

        # Test 6: Test with invalid attempt ID
        print("\n6. Testing mark_attempt_correct() with invalid ID...")
        invalid_success = await training_system.mark_attempt_correct(99999)
        print(f"   ✓ Invalid attempt ID result: {invalid_success}")
        assert not invalid_success, "Should fail for invalid attempt ID"

        print("\n✓ All training attempt ID tests passed!")
        return True

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        await db.close()
        print("✓ Database connection closed")


async def test_callback_data_parsing():
    """Test callback data parsing logic."""
    print("\n" + "=" * 50)
    print("Testing Callback Data Parsing")
    print("=" * 50)

    # Test valid callback data
    test_cases = [
        ("mark_correct:123", True, 123),
        ("mark_correct:456", True, 456),
        ("mark_correct:1", True, 1),
        ("mark_correct:", False, None),  # Missing ID
        ("mark_correct", False, None),  # No colon
        ("other_callback:123", False, None),  # Wrong prefix
        ("mark_correct:abc", False, None),  # Invalid ID format
    ]

    for callback_data, should_succeed, expected_id in test_cases:
        try:
            if ":" not in callback_data:
                raise ValueError("Invalid callback data format")

            prefix, attempt_id_str = callback_data.split(":", 1)
            if prefix != "mark_correct":
                raise ValueError("Wrong callback prefix")

            attempt_id = int(attempt_id_str)

            if should_succeed:
                assert attempt_id == expected_id, f"Expected {expected_id}, got {attempt_id}"
                print(f"   ✓ '{callback_data}' -> {attempt_id}")
            else:
                print(f"   ✗ '{callback_data}' should have failed but didn't")
                return False

        except (ValueError, IndexError):
            if not should_succeed:
                print(f"   ✓ '{callback_data}' correctly failed")
            else:
                print(f"   ✗ '{callback_data}' should have succeeded but failed")
                return False

    print("\n✓ All callback data parsing tests passed!")
    return True


async def test_localization_keys():
    """Test that all required localization keys exist."""
    print("\n" + "=" * 50)
    print("Testing Localization Keys")
    print("=" * 50)

    from src.local.localization import localization

    required_keys = [
        "marked_as_correct",
        "attempt_already_correct_or_not_found",
        "invalid_request",
    ]

    languages = ["english", "russian", "polish", "spanish"]

    for lang in languages:
        print(f"\nTesting {lang} localization...")
        for key in required_keys:
            try:
                text = localization.get_text(lang, key)
                assert text and text != key, f"Key '{key}' should have a translation"
                print(f"   ✓ {key}: '{text}'")
            except Exception as e:
                print(f"   ✗ {key}: Missing or invalid - {e}")
                return False

    print("\n✓ All localization keys exist!")
    return True


async def main():
    """Run all tests."""
    print("Training Attempt ID Test Suite")
    print("=" * 60)

    # Test 1: Core functionality
    test1_success = await test_training_attempt_id_flow()

    # Test 2: Callback data parsing
    test2_success = await test_callback_data_parsing()

    # Test 3: Localization
    test3_success = await test_localization_keys()

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Training attempt ID flow: {'PASS' if test1_success else 'FAIL'}")
    print(f"Callback data parsing: {'PASS' if test2_success else 'FAIL'}")
    print(f"Localization keys: {'PASS' if test3_success else 'FAIL'}")

    if test1_success and test2_success and test3_success:
        print("\n🎉 All tests PASSED! Training attempt ID system is working correctly.")
        return 0
    else:
        print("\n❌ Some tests FAILED. Please check the implementation.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
