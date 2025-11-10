#!/usr/bin/env python3
"""
Script to seed the grammar rules database with AI-generated content.

Usage:
    python scripts/seed_grammar.py --language es --levels A1 A2 --categories verbs nouns
    python scripts/seed_grammar.py --language es --full  # Generate complete library (WARNING: expensive!)
    python scripts/seed_grammar.py --language es --starter  # Generate starter pack (A1-A2, high priority)
"""

import asyncio
import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from privet_api.core.config import settings
from privet_api.core.database import DatabaseManager
from privet_api.repositories.grammar_repository import GrammarRepository
from privet_api.services.grammar import GrammarRuleGenerator
from privet_api.services.ai.ai_provider import OpenRouterProvider
from privet_api.repositories.api_usage_repository import APIUsageRepository
from privet_api.services.expense_tracker import ExpenseTracker


STARTER_PACK = {
    "categories": ["verbs", "nouns", "pronouns", "adjectives"],
    "levels": ["A1", "A2"],
    "description": "Essential grammar for beginners (A1-A2)"
}

INTERMEDIATE_PACK = {
    "categories": ["verbs", "nouns", "pronouns", "adjectives", "prepositions"],
    "levels": ["B1", "B2"],
    "description": "Intermediate grammar (B1-B2)"
}

ADVANCED_PACK = {
    "categories": None,  # All categories
    "levels": ["C1", "C2"],
    "description": "Advanced grammar (C1-C2)"
}


async def seed_grammar(
    language: str,
    categories: list = None,
    levels: list = None,
    full: bool = False,
    starter: bool = False,
    intermediate: bool = False,
    advanced: bool = False,
):
    """Seed grammar rules database."""

    # Determine what to generate
    if starter:
        categories = STARTER_PACK["categories"]
        levels = STARTER_PACK["levels"]
        print(f"🌱 Generating STARTER PACK: {STARTER_PACK['description']}")
    elif intermediate:
        categories = INTERMEDIATE_PACK["categories"]
        levels = INTERMEDIATE_PACK["levels"]
        print(f"📚 Generating INTERMEDIATE PACK: {INTERMEDIATE_PACK['description']}")
    elif advanced:
        categories = ADVANCED_PACK["categories"]
        levels = ADVANCED_PACK["levels"]
        print(f"🎓 Generating ADVANCED PACK: {ADVANCED_PACK['description']}")
    elif full:
        categories = None
        levels = None
        print("⚠️  WARNING: Generating FULL LIBRARY - this will take 30+ minutes and consume significant API credits!")
        response = input("Are you sure you want to continue? (yes/no): ")
        if response.lower() != "yes":
            print("Cancelled.")
            return

    # Initialize database
    print(f"\n🔧 Connecting to database...")
    db_manager = DatabaseManager(settings.database_url)
    await db_manager.setup()

    # Initialize services
    grammar_repo = GrammarRepository(db_manager.pool)
    api_usage_repo = APIUsageRepository(db_manager.pool)
    expense_tracker = ExpenseTracker(api_usage_repo)

    ai_provider = OpenRouterProvider(
        api_key=settings.openrouter_api_key,
        model=settings.openrouter_model,
        expense_tracker=expense_tracker
    )

    generator = GrammarRuleGenerator(ai_provider, grammar_repo)

    # Generate grammar library
    print(f"\n🤖 Starting AI-powered grammar generation for {language.upper()}...")
    print(f"   Categories: {categories or 'ALL'}")
    print(f"   Levels: {levels or 'ALL (A1-C2)'}")
    print(f"   This may take a while...\n")

    try:
        stats = await generator.generate_complete_grammar_library(
            language=language,
            native_language="en",
            categories=categories,
            difficulty_levels=levels
        )

        print("\n" + "="*60)
        print("✅ GRAMMAR GENERATION COMPLETE!")
        print("="*60)
        print(f"Language: {language.upper()}")
        print(f"Total Attempted: {stats['total_attempted']}")
        print(f"✓ Created: {stats['total_created']}")
        print(f"⊝ Skipped (already exist): {stats['total_skipped']}")
        print(f"✗ Failed: {stats['total_failed']}")

        print("\n📊 By Category:")
        for cat_stats in stats['categories']:
            print(f"  - {cat_stats['category']}: {cat_stats['total_created']} created, "
                  f"{cat_stats['total_skipped']} skipped, {cat_stats['total_failed']} failed")

        # Get API usage stats
        print("\n💰 API Usage:")
        usage = await api_usage_repo.get_total_usage()
        if usage:
            print(f"  Total API calls: {usage.get('total_calls', 0)}")
            print(f"  Total cost: ${usage.get('total_cost', 0):.2f}")

        print("\n" + "="*60)

    except Exception as e:
        print(f"\n❌ Error during generation: {e}")
        raise
    finally:
        await db_manager.close()


async def list_existing_rules(language: str):
    """List existing grammar rules."""
    db_manager = DatabaseManager(settings.database_url)
    await db_manager.setup()

    grammar_repo = GrammarRepository(db_manager.pool)

    try:
        # Get all rules for language
        rules = await grammar_repo.get_rules_by_language(language, limit=1000)

        if not rules:
            print(f"No grammar rules found for {language}")
            return

        # Group by category and level
        by_category = {}
        for rule in rules:
            cat = rule['category']
            level = rule['difficulty_level']

            if cat not in by_category:
                by_category[cat] = {}
            if level not in by_category[cat]:
                by_category[cat][level] = []

            by_category[cat][level].append(rule['rule_code'])

        print(f"\n📚 Existing Grammar Rules for {language.upper()}")
        print("="*60)

        for category, levels in sorted(by_category.items()):
            print(f"\n{category.upper()}:")
            for level in ["A1", "A2", "B1", "B2", "C1", "C2"]:
                if level in levels:
                    count = len(levels[level])
                    print(f"  {level}: {count} rules")

        print(f"\nTotal: {len(rules)} rules")
        print("="*60)

    finally:
        await db_manager.close()


def main():
    parser = argparse.ArgumentParser(
        description="Seed grammar rules database with AI-generated content"
    )

    parser.add_argument(
        "--language",
        "-l",
        required=True,
        choices=["es", "en", "ru"],
        help="Target language to generate rules for"
    )

    parser.add_argument(
        "--categories",
        "-c",
        nargs="+",
        choices=["verbs", "nouns", "pronouns", "adjectives", "prepositions", "adverbs", "sentence_structure"],
        help="Specific categories to generate (default: all)"
    )

    parser.add_argument(
        "--levels",
        nargs="+",
        choices=["A1", "A2", "B1", "B2", "C1", "C2"],
        help="Specific CEFR levels to generate (default: all)"
    )

    parser.add_argument(
        "--full",
        action="store_true",
        help="Generate complete library (all categories, all levels) - WARNING: expensive!"
    )

    parser.add_argument(
        "--starter",
        action="store_true",
        help="Generate starter pack (A1-A2, essential categories)"
    )

    parser.add_argument(
        "--intermediate",
        action="store_true",
        help="Generate intermediate pack (B1-B2, common categories)"
    )

    parser.add_argument(
        "--advanced",
        action="store_true",
        help="Generate advanced pack (C1-C2, all categories)"
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="List existing rules for the language"
    )

    args = parser.parse_args()

    # Check for conflicting options
    pack_options = sum([args.full, args.starter, args.intermediate, args.advanced])
    if pack_options > 1:
        parser.error("Can only specify one of: --full, --starter, --intermediate, --advanced")

    if args.list:
        asyncio.run(list_existing_rules(args.language))
    else:
        asyncio.run(seed_grammar(
            language=args.language,
            categories=args.categories,
            levels=args.levels,
            full=args.full,
            starter=args.starter,
            intermediate=args.intermediate,
            advanced=args.advanced
        ))


if __name__ == "__main__":
    main()
