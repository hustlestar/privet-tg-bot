#!/usr/bin/env python3
"""
Word List Generator for Learn Words Application

This script generates lists of the most common words for supported languages.
It aggregates words from multiple sources including NLTK corpora, online frequency lists,
and manually curated lists to create high-quality word lists for language learning.

Usage:
    python scripts/generate_word_lists.py --languages english,polish,russian,spanish --count 5000
    python scripts/generate_word_lists.py --language polish --count 3000
    python scripts/generate_word_lists.py --help
"""

import argparse
import json
import logging
import os
import re
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from urllib.request import urlopen
from urllib.error import URLError

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# Configure logging
def setup_logging(script_dir):
    """Setup logging with correct paths."""
    log_file = script_dir / "reports" / "word_list_generation.log"
    log_file.parent.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
    )


logger = logging.getLogger(__name__)


class WordListGenerator:
    """Generates word lists from multiple sources for different languages."""

    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.word_sources_dir = self.script_dir / "word_sources"
        self.generated_lists_dir = self.script_dir / "generated_lists"
        self.reports_dir = self.script_dir / "reports"

        # Ensure directories exist
        self.generated_lists_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)

        # Setup logging with correct paths
        setup_logging(self.script_dir)

        # Language configuration
        self.language_sources = {
            "english": {
                "online_sources": [
                    "https://raw.githubusercontent.com/first20hours/google-10000-english/master/google-10000-english-usa.txt",
                    "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/en/en_50k.txt",
                ],
                "manual_lists": ["basic_english_850.txt", "oxford_3000.txt"],
                "nltk_available": True,
            },
            "polish": {
                "online_sources": ["https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/pl/pl_50k.txt"],
                "manual_lists": ["polish_common_5000.txt"],
                "nltk_available": False,
            },
            "russian": {
                "online_sources": ["https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/ru/ru_50k.txt"],
                "manual_lists": ["russian_common_5000.txt"],
                "nltk_available": False,
            },
            "spanish": {
                "online_sources": ["https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/es/es_50k.txt"],
                "manual_lists": ["spanish_common_5000.txt"],
                "nltk_available": False,
            },
        }

        # Word filtering patterns
        self.word_patterns = {
            "english": re.compile(r"^[a-zA-Z]+$"),
            "polish": re.compile(r"^[a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ]+$"),
            "russian": re.compile(r"^[а-яёА-ЯЁ]+$"),
            "spanish": re.compile(r"^[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ]+$"),
        }

        # Minimum and maximum word lengths
        self.min_word_length = 2
        self.max_word_length = 20

        # Words to exclude (common stop words, inappropriate content, etc.)
        self.excluded_words = {
            "english": {
                "the",
                "and",
                "or",
                "but",
                "in",
                "on",
                "at",
                "to",
                "for",
                "of",
                "with",
                "by",
            },
            "polish": {
                "i",
                "w",
                "na",
                "z",
                "do",
                "od",
                "za",
                "o",
                "po",
                "przez",
                "dla",
                "bez",
            },
            "russian": {
                "и",
                "в",
                "на",
                "с",
                "по",
                "для",
                "от",
                "до",
                "за",
                "о",
                "к",
                "у",
            },
            "spanish": {
                "y",
                "en",
                "de",
                "a",
                "el",
                "la",
                "los",
                "las",
                "un",
                "una",
                "con",
                "por",
            },
        }

    def generate_word_list(self, language: str, target_count: int = 5000) -> List[Dict]:
        """Generate a word list for the specified language."""
        logger.info(f"Starting word list generation for {language} (target: {target_count} words)")

        if language not in self.language_sources:
            raise ValueError(f"Unsupported language: {language}")

        # Collect words from all sources
        all_words = Counter()
        sources_used = []

        # 1. Try to get words from NLTK if available
        if self.language_sources[language].get("nltk_available", False):
            nltk_words = self._get_nltk_words(language)
            if nltk_words:
                all_words.update(nltk_words)
                sources_used.append("NLTK")
                logger.info(f"Added {len(nltk_words)} words from NLTK")

        # 2. Get words from online sources
        for url in self.language_sources[language].get("online_sources", []):
            try:
                online_words = self._get_online_words(url, language)
                if online_words:
                    all_words.update(online_words)
                    sources_used.append(f"Online: {url.split('/')[-1]}")
                    logger.info(f"Added {len(online_words)} words from {url}")
            except Exception as e:
                logger.warning(f"Failed to fetch words from {url}: {e}")

        # 3. Get words from manual lists
        for manual_file in self.language_sources[language].get("manual_lists", []):
            try:
                manual_words = self._get_manual_words(language, manual_file)
                if manual_words:
                    all_words.update(manual_words)
                    sources_used.append(f"Manual: {manual_file}")
                    logger.info(f"Added {len(manual_words)} words from {manual_file}")
            except Exception as e:
                logger.warning(f"Failed to load manual list {manual_file}: {e}")

        if not all_words:
            raise ValueError(f"No words found for language: {language}")

        # Filter and clean words
        filtered_words = self._filter_words(all_words, language)
        logger.info(f"Filtered to {len(filtered_words)} valid words")

        # Select top words
        top_words = self._select_top_words(filtered_words, target_count)
        logger.info(f"Selected top {len(top_words)} words")

        # Create word list with metadata
        word_list = []
        for rank, (word, frequency) in enumerate(top_words, 1):
            word_entry = {
                "rank": rank,
                "word": word,
                "frequency": frequency,
                "length": len(word),
                "language": language,
            }
            word_list.append(word_entry)

        # Generate metadata
        metadata = {
            "language": language,
            "total_words": len(word_list),
            "target_count": target_count,
            "sources_used": sources_used,
            "generation_date": datetime.now().isoformat(),
            "min_word_length": self.min_word_length,
            "max_word_length": self.max_word_length,
            "statistics": {
                "avg_word_length": sum(len(word["word"]) for word in word_list) / len(word_list),
                "min_frequency": min(word["frequency"] for word in word_list),
                "max_frequency": max(word["frequency"] for word in word_list),
                "total_frequency": sum(word["frequency"] for word in word_list),
            },
        }

        return {"metadata": metadata, "words": word_list}

    def _get_nltk_words(self, language: str) -> Optional[Counter]:
        """Get words from NLTK corpora (primarily for English)."""
        if language != "english":
            return None

        try:
            import nltk
            from nltk.corpus import brown, reuters, gutenberg
            from nltk.tokenize import word_tokenize

            # Download required NLTK data if not present
            try:
                nltk.data.find("corpora/brown")
            except LookupError:
                logger.info("Downloading NLTK brown corpus...")
                nltk.download("brown", quiet=True)

            try:
                nltk.data.find("corpora/reuters")
            except LookupError:
                logger.info("Downloading NLTK reuters corpus...")
                nltk.download("reuters", quiet=True)

            try:
                nltk.data.find("corpora/gutenberg")
            except LookupError:
                logger.info("Downloading NLTK gutenberg corpus...")
                nltk.download("gutenberg", quiet=True)

            words = Counter()

            # Brown corpus
            try:
                brown_words = [word.lower() for word in brown.words() if word.isalpha()]
                words.update(brown_words)
                logger.info(f"Added {len(brown_words)} words from Brown corpus")
            except Exception as e:
                logger.warning(f"Failed to load Brown corpus: {e}")

            # Reuters corpus
            try:
                reuters_words = [word.lower() for word in reuters.words() if word.isalpha()]
                words.update(reuters_words)
                logger.info(f"Added {len(reuters_words)} words from Reuters corpus")
            except Exception as e:
                logger.warning(f"Failed to load Reuters corpus: {e}")

            # Gutenberg corpus
            try:
                gutenberg_words = [word.lower() for word in gutenberg.words() if word.isalpha()]
                words.update(gutenberg_words)
                logger.info(f"Added {len(gutenberg_words)} words from Gutenberg corpus")
            except Exception as e:
                logger.warning(f"Failed to load Gutenberg corpus: {e}")

            return words

        except ImportError:
            logger.warning("NLTK not available, skipping NLTK sources")
            return None
        except Exception as e:
            logger.warning(f"Error accessing NLTK corpora: {e}")
            return None

    def _get_online_words(self, url: str, language: str) -> Optional[Counter]:
        """Get words from online frequency lists."""
        try:
            logger.info(f"Fetching words from {url}")

            with urlopen(url, timeout=30) as response:
                content = response.read().decode("utf-8")

            words = Counter()
            lines = content.strip().split("\n")

            for line in lines[:10000]:  # Limit to first 10k lines
                line = line.strip()
                if not line:
                    continue

                # Handle different formats
                if "\t" in line:
                    # Format: word\tfrequency
                    parts = line.split("\t")
                    if len(parts) >= 2:
                        word = parts[0].strip().lower()
                        try:
                            frequency = int(parts[1])
                        except ValueError:
                            frequency = 1
                        words[word] = frequency
                elif " " in line:
                    # Format: word frequency
                    parts = line.split()
                    if len(parts) >= 2:
                        word = parts[0].strip().lower()
                        try:
                            frequency = int(parts[1])
                        except ValueError:
                            frequency = 1
                        words[word] = frequency
                else:
                    # Format: just word (assume frequency 1)
                    word = line.strip().lower()
                    words[word] = 1

            return words

        except URLError as e:
            logger.error(f"Failed to fetch from {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error processing online source {url}: {e}")
            return None

    def _get_manual_words(self, language: str, filename: str) -> Optional[Counter]:
        """Get words from manual word lists."""
        file_path = self.word_sources_dir / language / filename

        if not file_path.exists():
            logger.warning(f"Manual word list not found: {file_path}")
            return None

        try:
            words = Counter()

            with open(file_path, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue

                    # Handle different formats
                    if "\t" in line:
                        parts = line.split("\t")
                        word = parts[0].strip().lower()
                        frequency = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 1
                    elif " " in line:
                        parts = line.split()
                        word = parts[0].strip().lower()
                        frequency = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 1
                    else:
                        word = line.strip().lower()
                        frequency = 1

                    words[word] = frequency

            return words

        except Exception as e:
            logger.error(f"Error reading manual word list {file_path}: {e}")
            return None

    def _filter_words(self, words: Counter, language: str) -> Counter:
        """Filter words based on language-specific criteria."""
        filtered = Counter()
        pattern = self.word_patterns.get(language)
        excluded = self.excluded_words.get(language, set())

        for word, frequency in words.items():
            # Basic length check
            if len(word) < self.min_word_length or len(word) > self.max_word_length:
                continue

            # Language-specific pattern check
            if pattern and not pattern.match(word):
                continue

            # Exclude common stop words
            if word in excluded:
                continue

            # Exclude words with numbers or special characters
            if any(char.isdigit() for char in word):
                continue

            # Exclude very short words that are likely not useful
            if len(word) < 3 and frequency < 10:
                continue

            filtered[word] = frequency

        return filtered

    def _select_top_words(self, words: Counter, target_count: int) -> List[Tuple[str, int]]:
        """Select the top words based on frequency and other criteria."""
        # Get most common words
        most_common = words.most_common(target_count * 2)  # Get more than needed for filtering

        # Apply additional filtering for quality
        selected = []
        seen_words = set()

        for word, frequency in most_common:
            if len(selected) >= target_count:
                break

            # Skip if already seen (shouldn't happen with Counter, but just in case)
            if word in seen_words:
                continue

            # Additional quality checks
            if self._is_quality_word(word):
                selected.append((word, frequency))
                seen_words.add(word)

        return selected

    def _is_quality_word(self, word: str) -> bool:
        """Check if a word meets quality criteria."""
        # Avoid words with repeated characters (like "aaa", "zzz")
        if len(set(word)) < len(word) * 0.5:
            return False

        # Avoid words that are too repetitive
        if len(word) > 3:
            for i in range(len(word) - 2):
                if word[i] == word[i + 1] == word[i + 2]:
                    return False

        return True

    def save_word_list(self, word_list_data: Dict, language: str) -> str:
        """Save the word list to a JSON file."""
        filename = f"{language}_{len(word_list_data['words'])}.json"
        filepath = self.generated_lists_dir / filename

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(word_list_data, f, ensure_ascii=False, indent=2)

            logger.info(f"Word list saved to {filepath}")
            return str(filepath)

        except Exception as e:
            logger.error(f"Failed to save word list to {filepath}: {e}")
            raise

    def generate_report(self, results: Dict[str, Dict]) -> str:
        """Generate a summary report of the word list generation."""
        report_filename = f"word_list_generation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        report_path = self.reports_dir / report_filename

        try:
            with open(report_path, "w", encoding="utf-8") as f:
                f.write("Word List Generation Report\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

                for language, data in results.items():
                    if "error" in data:
                        f.write(f"Language: {language.upper()}\n")
                        f.write(f"Status: FAILED\n")
                        f.write(f"Error: {data['error']}\n\n")
                    else:
                        metadata = data["metadata"]
                        f.write(f"Language: {language.upper()}\n")
                        f.write(f"Status: SUCCESS\n")
                        f.write(f"Words generated: {metadata['total_words']}\n")
                        f.write(f"Target count: {metadata['target_count']}\n")
                        f.write(f"Sources used: {', '.join(metadata['sources_used'])}\n")
                        f.write(f"Average word length: {metadata['statistics']['avg_word_length']:.1f}\n")
                        f.write(f"Frequency range: {metadata['statistics']['min_frequency']} - {metadata['statistics']['max_frequency']}\n")
                        f.write(f"File saved: {data['filepath']}\n\n")

                f.write("Generation completed successfully!\n")

            logger.info(f"Report saved to {report_path}")
            return str(report_path)

        except Exception as e:
            logger.error(f"Failed to generate report: {e}")
            return ""


def main():
    """Main function to run the word list generator."""
    parser = argparse.ArgumentParser(
        description="Generate word lists for language learning",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --languages english,polish,russian,spanish --count 5000
  %(prog)s --language polish --count 3000
  %(prog)s --language english --count 1000 --output-dir custom_lists/
        """,
    )

    parser.add_argument(
        "--languages",
        type=str,
        help="Comma-separated list of languages to generate (english,polish,russian,spanish)",
    )

    parser.add_argument("--language", type=str, help="Single language to generate")

    parser.add_argument(
        "--count",
        type=int,
        default=9700,
        help="Number of words to generate per language (default: 5000)",
    )

    parser.add_argument("--output-dir", type=str, help="Custom output directory for generated lists")

    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Determine which languages to process
    if args.languages:
        languages = [lang.strip() for lang in args.languages.split(",")]
    elif args.language:
        languages = [args.language]
    else:
        # Default to all supported languages
        languages = ["english", "polish", "russian", "spanish"]

    # Initialize generator
    generator = WordListGenerator()

    # Override output directory if specified
    if args.output_dir:
        generator.generated_lists_dir = Path(args.output_dir)
        generator.generated_lists_dir.mkdir(parents=True, exist_ok=True)

    # Generate word lists
    results = {}
    total_start_time = time.time()

    for language in languages:
        logger.info(f"Processing language: {language}")
        lang_start_time = time.time()

        try:
            word_list_data = generator.generate_word_list(language, args.count)
            filepath = generator.save_word_list(word_list_data, language)

            results[language] = {
                "metadata": word_list_data["metadata"],
                "filepath": filepath,
                "duration": time.time() - lang_start_time,
            }

            logger.info(f"Successfully generated {len(word_list_data['words'])} words for {language} in {results[language]['duration']:.1f}s")

        except Exception as e:
            logger.error(f"Failed to generate word list for {language}: {e}")
            results[language] = {
                "error": str(e),
                "duration": time.time() - lang_start_time,
            }

    total_duration = time.time() - total_start_time

    # Generate report
    report_path = generator.generate_report(results)

    # Print summary
    print("\n" + "=" * 60)
    print("WORD LIST GENERATION SUMMARY")
    print("=" * 60)

    successful = 0
    failed = 0

    for language, data in results.items():
        if "error" in data:
            print(f"❌ {language.upper()}: FAILED - {data['error']}")
            failed += 1
        else:
            print(f"✅ {language.upper()}: {data['metadata']['total_words']} words generated")
            successful += 1

    print(f"\nTotal time: {total_duration:.1f}s")
    print(f"Successful: {successful}, Failed: {failed}")

    if report_path:
        print(f"Report saved: {report_path}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
