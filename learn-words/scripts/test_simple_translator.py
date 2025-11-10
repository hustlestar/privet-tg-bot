#!/usr/bin/env python3
"""
Test script for the simple parallel translator.

This script demonstrates how to use the simple_parallel_translation function
to translate words from a file in parallel batches.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.simple_parallel_translator import simple_parallel_translation

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

logger = logging.getLogger(__name__)


async def test_simple_translator():
    """Test the simple parallel translator with a small word list."""

    # Create a test word list file
    test_words = [
        {"word": "привет", "frequency": 1000},
        {"word": "мир", "frequency": 800},
        {"word": "дом", "frequency": 600},
        {"word": "работа", "frequency": 500},
        {"word": "время", "frequency": 400},
    ]

    test_file = Path("scripts/test_words.json")

    # Create test file
    try:
        with open(test_file, "w", encoding="utf-8") as f:
            json.dump({"words": test_words}, f, ensure_ascii=False, indent=2)
        logger.info(f"Created test file: {test_file}")
    except Exception as e:
        logger.error(f"Failed to create test file: {e}")
        return

    try:
        # Test the simple parallel translator
        logger.info("Starting simple parallel translation test...")

        result = await simple_parallel_translation(
            input_file=str(test_file),
            from_lang="russian",
            to_lang="english",
            native_lang="russian",
            learning_lang="english",
            batch_size=3,  # Small batch for testing
            max_concurrent=5,  # Low concurrency for testing
            requests_per_second=10.0,  # Conservative rate limit
        )

        # Print results
        print("\n" + "=" * 50)
        print("SIMPLE PARALLEL TRANSLATION TEST RESULTS")
        print("=" * 50)
        print(f"Total words: {result['total_words']}")
        print(f"Processed: {result['processed']}")
        print(f"Skipped: {result['skipped']}")
        print(f"Errors: {result['errors']}")
        print(f"Duration: {result['duration']:.2f} seconds")
        print(f"Throughput: {result['throughput']:.2f} words/second")

        if "error" in result:
            print(f"Error: {result['error']}")

        success_rate = (result["processed"] / result["total_words"] * 100) if result["total_words"] > 0 else 0
        print(f"Success rate: {success_rate:.1f}%")
        print("=" * 50)

    except Exception as e:
        logger.error(f"Test failed: {e}")

    finally:
        # Clean up test file
        try:
            if test_file.exists():
                test_file.unlink()
                logger.info(f"Cleaned up test file: {test_file}")
        except Exception as e:
            logger.warning(f"Failed to clean up test file: {e}")


async def test_with_existing_file():
    """Test with an existing word list file if available."""

    # Look for existing word list files
    scripts_dir = Path(__file__).parent
    generated_lists_dir = scripts_dir / "generated_lists"

    possible_files = [
        "russian_100.json",
        "russian_1000.json",
        "english_100.json",
        "polish_100.json",
    ]

    test_file = None
    for filename in possible_files:
        filepath = generated_lists_dir / filename
        if filepath.exists():
            test_file = filepath
            break

    if not test_file:
        logger.info("No existing word list files found for testing")
        return

    logger.info(f"Testing with existing file: {test_file}")

    # Determine languages from filename
    if "russian" in test_file.name:
        from_lang, to_lang = "russian", "english"
        native_lang, learning_lang = "russian", "english"
    elif "english" in test_file.name:
        from_lang, to_lang = "english", "russian"
        native_lang, learning_lang = "english", "russian"
    elif "polish" in test_file.name:
        from_lang, to_lang = "polish", "english"
        native_lang, learning_lang = "polish", "english"
    else:
        logger.warning(f"Cannot determine languages for {test_file}")
        return

    try:
        result = await simple_parallel_translation(
            input_file=str(test_file),
            from_lang=from_lang,
            to_lang=to_lang,
            native_lang=native_lang,
            learning_lang=learning_lang,
            batch_size=20,
            max_concurrent=10,
            requests_per_second=25.0,
        )

        print(f"\n📁 Results for {test_file.name}:")
        print(f"   Total: {result['total_words']}, Processed: {result['processed']}")
        print(f"   Skipped: {result['skipped']}, Errors: {result['errors']}")
        print(f"   Duration: {result['duration']:.1f}s, Throughput: {result['throughput']:.1f} words/s")

    except Exception as e:
        logger.error(f"Test with existing file failed: {e}")


async def main():
    """Run all tests."""
    print("🧪 Testing Simple Parallel Translator")
    print("=" * 50)

    # Test 1: Small test with generated words
    await test_simple_translator()

    # Test 2: Test with existing files if available
    await test_with_existing_file()

    print("\n✅ All tests completed!")


if __name__ == "__main__":
    asyncio.run(main())
