#!/usr/bin/env python3
"""
Simple Parallel Translation Script

A streamlined version of the database population script that provides only
the core parallel translation functionality without checkpoints, statistics,
reports, or CLI interface.

Usage:
    from scripts.simple_parallel_translator import simple_parallel_translation

    result = await simple_parallel_translation(
        input_file="path/to/words.json",
        from_lang="russian",
        to_lang="english",
        native_lang="russian",
        learning_lang="english"
    )
"""

import asyncio
import json
import logging
import os.path
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Set

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import application modules
from src.database import Database, db
from src.translation.translator import TranslationService
from scripts.util import TokenBucketRateLimiter, CircuitBreaker, ErrorClassifier

logger = logging.getLogger(__name__)


async def simple_parallel_translation(
    input_file: str,
    from_lang: str,
    to_lang: str,
    native_lang: str,
    learning_lang: str,
    batch_size: int = 50,
    max_concurrent: int = 25,
    requests_per_second: float = 50.0,
) -> Dict[str, Any]:
    """
    Simple parallel translation of words from file to database.

    Args:
        input_file: Path to JSON file containing word list
        from_lang: Source language for translation
        to_lang: Target language for translation
        native_lang: User's native language
        learning_lang: User's learning language
        batch_size: Number of words to process per batch
        max_concurrent: Maximum concurrent translation tasks
        requests_per_second: Rate limit for API calls

    Returns:
        Dict containing processing results:
        {
            "total_words": int,
            "processed": int,
            "skipped": int,
            "errors": int,
            "duration": float,
            "throughput": float
        }
    """
    start_time = time.time()

    # Initialize components
    database = None
    translator = None

    try:
        # Load word list from file
        words = await _load_words_from_file(input_file)
        if not words:
            return {
                "total_words": 0,
                "processed": 0,
                "skipped": 0,
                "errors": 1,
                "duration": 0,
                "throughput": 0,
                "error": "Failed to load words from file",
            }

        logger.info(f"Loaded {len(words)} words from {input_file}")

        # Initialize database and translator
        database = Database()
        await database.connect()
        await db.connect()

        translator = TranslationService()

        logger.info(f"Starting parallel translation: {len(words)} words ({from_lang} -> {to_lang})")

        # Process words in parallel batches
        total_processed = 0
        total_skipped = 0
        total_errors = 0

        # Split words into batches
        batches = [words[i : i + batch_size] for i in range(0, len(words), batch_size)]

        for batch_index, batch in enumerate(batches, 1):
            logger.info(f"Processing batch {batch_index}/{len(batches)} ({len(batch)} words)")

            batch_result = await _process_batch_parallel(
                batch=batch,
                from_lang=from_lang,
                to_lang=to_lang,
                native_lang=native_lang,
                learning_lang=learning_lang,
                translator=translator,
                database=database,
                max_concurrent=max_concurrent,
                requests_per_second=requests_per_second,
            )

            total_processed += batch_result["processed"]
            total_skipped += batch_result["skipped"]
            total_errors += batch_result["errors"]

            # Log batch progress
            logger.info(
                f"Batch {batch_index} completed: "
                f"{batch_result['processed']} processed, "
                f"{batch_result['skipped']} skipped, "
                f"{batch_result['errors']} errors"
            )

        # Calculate final results
        duration = time.time() - start_time
        throughput = len(words) / duration if duration > 0 else 0

        result = {
            "total_words": len(words),
            "processed": total_processed,
            "skipped": total_skipped,
            "errors": total_errors,
            "duration": duration,
            "throughput": throughput,
        }

        logger.info(
            f"Translation completed: {total_processed} processed, "
            f"{total_skipped} skipped, {total_errors} errors "
            f"in {duration:.1f}s ({throughput:.1f} words/s)"
        )

        return result

    except Exception as e:
        logger.error(f"Translation failed: {e}")
        duration = time.time() - start_time
        return {
            "total_words": 0,
            "processed": 0,
            "skipped": 0,
            "errors": 1,
            "duration": duration,
            "throughput": 0,
            "error": str(e),
        }

    finally:
        # Cleanup
        if database:
            await database.close()


async def _load_words_from_file(file_path: str) -> List[Dict]:
    """Load words from JSON file."""
    try:
        path = Path(file_path)
        if not path.exists():
            logger.error(f"File not found: {file_path}")
            return []

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Handle different JSON structures
        if isinstance(data, dict) and "words" in data:
            words = list(set(data["words"]))
        elif isinstance(data, list):
            words = list(set(data))
        else:
            logger.error(f"Invalid JSON structure in {file_path}")
            return []

        logger.info(f"Loaded {len(words)} words from {file_path}")
        return words

    except Exception as e:
        logger.error(f"Failed to load words from {file_path}: {e}")
        return []


async def _process_batch_parallel(
    batch: List[Dict],
    from_lang: str,
    to_lang: str,
    native_lang: str,
    learning_lang: str,
    translator: TranslationService,
    database: Database,
    max_concurrent: int,
    requests_per_second: float,
) -> Dict[str, int]:
    """Process a batch of words with parallel translation."""

    # Initialize parallel processing components
    semaphore = asyncio.Semaphore(max_concurrent)
    rate_limiter = TokenBucketRateLimiter(rate=requests_per_second, burst=max_concurrent, adaptive=True)
    circuit_breaker = CircuitBreaker()

    # Statistics tracking
    stats = {"processed": 0, "skipped": 0, "errors": 0}

    # Create parallel translation tasks
    tasks = []
    for word_entry in batch:
        task = asyncio.create_task(
            _translate_word_parallel(
                word_entry=word_entry,
                from_lang=from_lang,
                to_lang=to_lang,
                native_lang=native_lang,
                learning_lang=learning_lang,
                translator=translator,
                database=database,
                semaphore=semaphore,
                rate_limiter=rate_limiter,
                circuit_breaker=circuit_breaker,
                stats=stats,
            )
        )
        tasks.append(task)

    # Execute all tasks concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Check for exceptions in results
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"Task {i} failed with exception: {result}")
            stats["errors"] += 1

    return stats


async def _translate_word_parallel(
    word_entry: Dict,
    from_lang: str,
    to_lang: str,
    native_lang: str,
    learning_lang: str,
    translator: TranslationService,
    database: Database,
    semaphore: asyncio.Semaphore,
    rate_limiter: TokenBucketRateLimiter,
    circuit_breaker: CircuitBreaker,
    stats: Dict[str, int],
) -> bool:
    """Translate a single word with parallel processing support."""

    async with semaphore:  # Limit concurrency
        # Handle both string and dictionary word entries
        if isinstance(word_entry, str):
            word = word_entry.strip()
        elif isinstance(word_entry, dict):
            word = word_entry.get("word", "").strip()
        else:
            logger.warning(f"Invalid word entry type: {type(word_entry)} - {word_entry}")
            stats["errors"] += 1
            return False

        if not word:
            logger.warning(f"Empty word in entry: {word_entry}")
            stats["errors"] += 1
            return False

        logger.debug(f"Processing word: '{word}' ({from_lang} -> {to_lang})")

        try:
            # Check circuit breaker
            if await circuit_breaker.is_open():
                stats["errors"] += 1
                return False

            # Rate limiting
            await rate_limiter.acquire()

            # Check if word already exists
            if await _check_word_exists(word, from_lang, to_lang, native_lang, database):
                stats["skipped"] += 1
                return True

            # Translate with retry logic
            success = await _translate_with_retry(
                word=word,
                from_lang=from_lang,
                to_lang=to_lang,
                native_lang=native_lang,
                learning_lang=learning_lang,
                translator=translator,
                max_retries=3,
            )

            if success:
                stats["processed"] += 1
                await circuit_breaker.record_success()
                rate_limiter.record_success()
                return True
            else:
                stats["errors"] += 1
                await circuit_breaker.record_failure()
                rate_limiter.record_error()
                return False

        except Exception as e:
            error_type = ErrorClassifier.classify_error(e)
            stats["errors"] += 1
            await circuit_breaker.record_failure()
            rate_limiter.record_error()
            logger.error(f"Translation failed for '{word}': {e}")
            return False


async def _check_word_exists(word: str, from_lang: str, to_lang: str, native_lang: str, database: Database) -> bool:
    """Check if a word translation already exists in the database."""
    try:
        existing_word = await database.get_word(
            word.lower().strip(),
            from_lang.lower(),
            to_lang.lower(),
            native_lang.lower(),
        )
        return existing_word is not None
    except Exception as e:
        logger.warning(f"Error checking word existence: {e}")
        return False


async def _translate_with_retry(
    word: str,
    from_lang: str,
    to_lang: str,
    native_lang: str,
    learning_lang: str,
    translator: TranslationService,
    max_retries: int = 3,
) -> bool:
    """Translate a word with retry logic and exponential backoff."""

    for attempt in range(max_retries):
        try:
            # Use the enhanced translation method
            translation_data = await translator.translate_word_enhanced(
                word=word,
                from_language=from_lang,
                to_language=to_lang,
                user_native=native_lang,
                user_learning=learning_lang,
            )

            return translation_data is not None

        except Exception as e:
            error_type = ErrorClassifier.classify_error(e)

            if error_type == "RATE_LIMIT":
                # Exponential backoff for rate limits
                wait_time = (2**attempt) + (0.1 * attempt)
                logger.warning(f"Rate limit hit for '{word}', waiting {wait_time:.1f}s (attempt {attempt + 1})")
                await asyncio.sleep(wait_time)
            elif attempt == max_retries - 1:
                # Last attempt failed
                logger.error(f"Failed to translate '{word}' after {max_retries} attempts: {e}")
                return False
            else:
                # Other errors - shorter wait
                wait_time = 0.5 * (attempt + 1)
                logger.warning(f"Translation error for '{word}', retrying in {wait_time:.1f}s: {e}")
                await asyncio.sleep(wait_time)

    return False


# Example usage
async def main():
    """Example usage of the simple parallel translator."""

    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    # # Example translation
    # result = await simple_parallel_translation(
    #     input_file=os.path.join(os.getcwd(), "generated_lists", "advanced_english.json"),
    #     from_lang="english",
    #     to_lang="russian",
    #     native_lang="russian",
    #     learning_lang="english",
    #     batch_size=25,
    #     max_concurrent=20
    # )

    result = await simple_parallel_translation(
        input_file=os.path.join(os.getcwd(), "generated_lists", "advanced_russian.json"),
        from_lang="russian",
        to_lang="english",
        native_lang="russian",
        learning_lang="english",
        batch_size=25,
        max_concurrent=20,
    )
    result = await simple_parallel_translation(
        input_file=os.path.join(os.getcwd(), "generated_lists", "my_leo_english.json"),
        from_lang="english",
        to_lang="russian",
        native_lang="russian",
        learning_lang="english",
        batch_size=25,
        max_concurrent=20,
    )

    print(f"Translation Results: {result}")


if __name__ == "__main__":
    asyncio.run(main())
