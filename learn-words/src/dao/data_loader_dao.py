import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class DataLoaderDao:
    def __init__(self, pool):
        self.pool = pool

    async def get_words_by_language(self, language: str) -> List[Dict[str, Any]]:
        """Get all distinct words for a specific language from database.

        Args:
            language: The language to fetch words for (e.g., 'russian', 'english')

        Returns:
            List of word dictionaries with word, frequency, source, and created_at
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT DISTINCT word, from_language, created_at
                FROM words 
                WHERE from_language = $1
                ORDER BY word
                """,
                language.lower().strip(),
            )

            # Format as word entries compatible with existing word list format
            word_entries = []
            for row in rows:
                word_entries.append(
                    {
                        "word": row["word"],
                        "frequency": 1000,  # Default frequency for database words
                        "source": "database",
                        "created_at": (row["created_at"].isoformat() if row["created_at"] else None),
                    }
                )

            logger.info(f"Fetched {len(word_entries)} words for language '{language}' from database")
            return word_entries

    async def get_words_by_languages(self, languages: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """Get words for multiple languages from database.

        Args:
            languages: List of languages to fetch words for

        Returns:
            Dictionary mapping language names to lists of word entries
        """
        word_lists = {}

        for language in languages:
            try:
                word_entries = await self.get_words_by_language(language)
                word_lists[language] = word_entries
            except Exception as e:
                logger.error(f"Failed to fetch words for language '{language}': {e}")
                word_lists[language] = []

        return word_lists

    async def get_language_word_counts(self) -> Dict[str, int]:
        """Get word counts by language from database.

        Returns:
            Dictionary mapping language names to word counts
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT from_language, COUNT(DISTINCT word) as word_count
                FROM words 
                GROUP BY from_language
                ORDER BY from_language
                """
            )

            counts = {}
            for row in rows:
                counts[row["from_language"]] = row["word_count"]

            logger.info(f"Database word counts: {counts}")
            return counts

    async def get_available_languages(self) -> List[str]:
        """Get list of languages that have words in database.

        Returns:
            List of language names that have words in the database
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT DISTINCT from_language
                FROM words
                ORDER BY from_language
                """
            )

            languages = [row["from_language"] for row in rows]
            logger.info(f"Available languages in database: {languages}")
            return languages

    async def get_database_word_statistics(self) -> Dict[str, Any]:
        """Get comprehensive word statistics from database.

        Returns:
            Dictionary with detailed statistics about words in database
        """
        async with self.pool.acquire() as conn:
            # Get basic counts
            word_counts = await self.get_language_word_counts()

            # Get total statistics
            total_stats = await conn.fetchrow(
                """
                SELECT 
                    COUNT(DISTINCT word) as total_unique_words,
                    COUNT(*) as total_translations,
                    COUNT(DISTINCT from_language) as total_languages,
                    MIN(created_at) as first_word_added,
                    MAX(created_at) as last_word_added
                FROM words
                """
            )

            # Get language pair statistics
            pair_stats = await conn.fetch(
                """
                SELECT 
                    from_language,
                    to_language,
                    COUNT(DISTINCT word) as word_count,
                    COUNT(*) as translation_count
                FROM words
                GROUP BY from_language, to_language
                ORDER BY from_language, to_language
                """
            )

            statistics = {
                "word_counts_by_language": word_counts,
                "total_unique_words": total_stats["total_unique_words"],
                "total_translations": total_stats["total_translations"],
                "total_languages": total_stats["total_languages"],
                "first_word_added": (total_stats["first_word_added"].isoformat() if total_stats["first_word_added"] else None),
                "last_word_added": (total_stats["last_word_added"].isoformat() if total_stats["last_word_added"] else None),
                "language_pairs": [
                    {
                        "from_language": row["from_language"],
                        "to_language": row["to_language"],
                        "word_count": row["word_count"],
                        "translation_count": row["translation_count"],
                    }
                    for row in pair_stats
                ],
            }

            return statistics
