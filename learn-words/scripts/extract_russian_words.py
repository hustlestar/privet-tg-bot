#!/usr/bin/env python3
"""
Extract Russian Words Script

This script extracts all distinct words that have from_language as 'russian'
from the database and saves them as a JSON file.

Usage:
    python scripts/extract_russian_words.py
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import application modules
from src.database import Database

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class RussianWordsExtractor:
    """Extracts all distinct Russian words from the database."""

    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.output_dir = self.script_dir / "extracted_words"

        # Ensure output directory exists
        self.output_dir.mkdir(exist_ok=True)

        self.db: Database = None

    async def initialize(self):
        """Initialize database connection."""
        logger.info("Initializing database connection...")

        try:
            self.db = Database()
            await self.db.connect()
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    async def cleanup(self):
        """Clean up database connection."""
        if self.db:
            await self.db.close()
            logger.info("Database connection closed")

    async def extract_russian_words(self) -> List[str]:
        """Extract all distinct words where from_language is 'russian'."""
        logger.info("Extracting Russian words from database...")

        try:
            async with self.db.pool.acquire() as conn:
                rows = await conn.fetch(
                    """
                    SELECT DISTINCT word
                    FROM words
                    WHERE from_language = 'russian'
                    ORDER BY word
                    """
                )

                words = [row["word"] for row in rows]

                logger.info(f"Extracted {len(words)} distinct Russian words")
                return words

        except Exception as e:
            logger.error(f"Failed to extract Russian words: {e}")
            raise

    async def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about Russian words in the database."""
        logger.info("Gathering statistics...")

        try:
            async with self.db.pool.acquire() as conn:
                # Total count of Russian words
                total_count = await conn.fetchval("SELECT COUNT(*) FROM words WHERE from_language = 'russian'")

                # Distinct count
                distinct_count = await conn.fetchval("SELECT COUNT(DISTINCT word) FROM words WHERE from_language = 'russian'")

                # Count by target language
                target_lang_counts = await conn.fetch(
                    """
                    SELECT to_language, COUNT(*) as count
                    FROM words 
                    WHERE from_language = 'russian'
                    GROUP BY to_language
                    ORDER BY count DESC
                    """
                )

                # Count by word type
                word_type_counts = await conn.fetch(
                    """
                    SELECT word_type, COUNT(*) as count
                    FROM words 
                    WHERE from_language = 'russian' AND word_type IS NOT NULL
                    GROUP BY word_type
                    ORDER BY count DESC
                    """
                )

                # Date range
                date_range = await conn.fetchrow(
                    """
                    SELECT MIN(created_at) as earliest, MAX(created_at) as latest
                    FROM words 
                    WHERE from_language = 'russian'
                    """
                )

                stats = {
                    "total_translations": total_count,
                    "distinct_words": distinct_count,
                    "target_languages": {row["to_language"]: row["count"] for row in target_lang_counts},
                    "word_types": {row["word_type"]: row["count"] for row in word_type_counts},
                    "date_range": {
                        "earliest": (date_range["earliest"].isoformat() if date_range["earliest"] else None),
                        "latest": (date_range["latest"].isoformat() if date_range["latest"] else None),
                    },
                }

                return stats

        except Exception as e:
            logger.error(f"Failed to gather statistics: {e}")
            raise

    def save_to_json(self, words: List[str], stats: Dict[str, Any]):
        """Save the extracted words to JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save just the words
        words_file = self.output_dir / f"russian_words_{timestamp}.json"
        words_data = {
            "metadata": {
                "extracted_at": datetime.now().isoformat(),
                "total_words": len(words),
                "description": "All distinct Russian words from the database (from_language = russian)",
            },
            "statistics": stats,
            "words": words,
        }

        try:
            with open(words_file, "w", encoding="utf-8") as f:
                json.dump(words_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Russian words saved to: {words_file}")
        except Exception as e:
            logger.error(f"Failed to save words file: {e}")
            raise

    def print_statistics(self, stats: Dict[str, Any]):
        """Print statistics to console."""
        print("\n" + "=" * 60)
        print("RUSSIAN WORDS EXTRACTION STATISTICS")
        print("=" * 60)

        print(f"\nTotal Statistics:")
        print(f"  Total translations: {stats['total_translations']:,}")
        print(f"  Distinct words: {stats['distinct_words']:,}")

        if stats["date_range"]["earliest"]:
            print(f"  Date range: {stats['date_range']['earliest']} to {stats['date_range']['latest']}")

        print(f"\nTarget Languages:")
        for lang, count in stats["target_languages"].items():
            print(f"  {lang}: {count:,} translations")

        if stats["word_types"]:
            print(f"\nWord Types:")
            for word_type, count in stats["word_types"].items():
                print(f"  {word_type}: {count:,} words")

        print("=" * 60)

    async def run(self):
        """Main execution method."""
        try:
            await self.initialize()

            # Extract words and gather statistics
            words = await self.extract_russian_words()
            stats = await self.get_statistics()

            # Print statistics
            self.print_statistics(stats)

            # Save to JSON files
            self.save_to_json(words, stats)

            logger.info("Russian words extraction completed successfully!")

        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            raise
        finally:
            await self.cleanup()


async def main():
    """Main entry point."""
    extractor = RussianWordsExtractor()
    await extractor.run()


if __name__ == "__main__":
    asyncio.run(main())
