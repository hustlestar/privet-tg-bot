"""AI-powered grammar rule generation service."""

import logging
from typing import Dict, List, Optional, Any
import json
import asyncio

logger = logging.getLogger(__name__)


class GrammarRuleGenerator:
    """Service for generating comprehensive grammar rules using AI."""

    def __init__(self, ai_provider, grammar_repository):
        """
        Initialize grammar rule generator.

        Args:
            ai_provider: AI provider instance for content generation
            grammar_repository: Grammar repository for storing rules
        """
        self.ai_provider = ai_provider
        self.grammar_repo = grammar_repository

    # CEFR Level Definitions
    CEFR_LEVELS = {
        "A1": {
            "name": "Beginner",
            "description": "Basic expressions and simple sentences",
            "grammar_complexity": "Present tense, basic articles, simple pronouns"
        },
        "A2": {
            "name": "Elementary",
            "description": "Simple everyday situations",
            "grammar_complexity": "Past tense, basic comparatives, simple conjunctions"
        },
        "B1": {
            "name": "Intermediate",
            "description": "Main points on familiar topics",
            "grammar_complexity": "Future tense, conditionals, subjunctive basics"
        },
        "B2": {
            "name": "Upper Intermediate",
            "description": "Complex texts and abstract topics",
            "grammar_complexity": "Advanced tenses, complex conditionals, passive voice"
        },
        "C1": {
            "name": "Advanced",
            "description": "Sophisticated language use",
            "grammar_complexity": "Nuanced grammar, idiomatic expressions, advanced subjunctive"
        },
        "C2": {
            "name": "Mastery",
            "description": "Native-like proficiency",
            "grammar_complexity": "All grammatical structures, subtle distinctions"
        }
    }

    # Grammar Categories with Difficulty Progression
    GRAMMAR_CATEGORIES = {
        "verbs": {
            "priority": 1,
            "subcategories": [
                "present_tense",
                "past_tense",
                "future_tense",
                "conditional",
                "subjunctive",
                "imperative",
                "progressive",
                "perfect_tenses"
            ]
        },
        "nouns": {
            "priority": 2,
            "subcategories": [
                "gender",
                "number",
                "articles",
                "diminutives",
                "augmentatives"
            ]
        },
        "pronouns": {
            "priority": 3,
            "subcategories": [
                "personal",
                "possessive",
                "demonstrative",
                "relative",
                "reflexive",
                "object_pronouns"
            ]
        },
        "adjectives": {
            "priority": 4,
            "subcategories": [
                "agreement",
                "position",
                "comparatives",
                "superlatives"
            ]
        },
        "prepositions": {
            "priority": 5,
            "subcategories": [
                "location",
                "time",
                "direction",
                "compound_prepositions"
            ]
        },
        "adverbs": {
            "priority": 6,
            "subcategories": [
                "manner",
                "time",
                "frequency",
                "degree"
            ]
        },
        "sentence_structure": {
            "priority": 7,
            "subcategories": [
                "word_order",
                "questions",
                "negation",
                "complex_sentences",
                "clauses"
            ]
        }
    }

    async def generate_grammar_rule(
        self,
        language: str,
        category: str,
        subcategory: str,
        difficulty_level: str,
        native_language: str = "en"
    ) -> Dict[str, Any]:
        """
        Generate a single grammar rule using AI.

        Args:
            language: Target language (es, en, ru)
            category: Main category (verbs, nouns, etc.)
            subcategory: Specific subcategory
            difficulty_level: CEFR level (A1-C2)
            native_language: Language for explanations

        Returns:
            Grammar rule dictionary ready for database insertion
        """
        try:
            # Build rule code
            rule_code = f"{language}_{category}_{subcategory}_{difficulty_level.lower()}"

            # Check if rule already exists
            existing = await self.grammar_repo.get_rule_by_code(rule_code)
            if existing:
                logger.info(f"Rule {rule_code} already exists, skipping")
                return None

            # Generate rule content using AI
            prompt = self._build_generation_prompt(
                language=language,
                category=category,
                subcategory=subcategory,
                difficulty_level=difficulty_level,
                native_language=native_language
            )

            # Get AI response
            messages = [
                {"role": "system", "content": "You are an expert language teacher creating comprehensive grammar lessons."},
                {"role": "user", "content": prompt}
            ]

            response = await self.ai_provider.chat(messages)
            content = response.get("content", "")

            # Parse AI response
            rule_data = self._parse_ai_response(content, rule_code, language, category, difficulty_level)

            if not rule_data:
                logger.error(f"Failed to parse AI response for {rule_code}")
                return None

            # Create rule in database
            created_rule = await self.grammar_repo.create_rule(rule_data)
            logger.info(f"Successfully generated rule: {rule_code}")

            return dict(created_rule)

        except Exception as e:
            logger.error(f"Error generating grammar rule: {e}", exc_info=True)
            return None

    def _build_generation_prompt(
        self,
        language: str,
        category: str,
        subcategory: str,
        difficulty_level: str,
        native_language: str
    ) -> str:
        """Build comprehensive prompt for AI grammar generation."""

        lang_names = {
            "es": "Spanish",
            "en": "English",
            "ru": "Russian"
        }
        target_lang = lang_names.get(language, language)

        level_info = self.CEFR_LEVELS[difficulty_level]

        prompt = f"""Generate a comprehensive grammar rule for {target_lang} language learning.

**Target Audience**: {difficulty_level} ({level_info['name']}) level learners
**Category**: {category}
**Topic**: {subcategory}

Please provide the grammar rule in the following JSON format:

```json
{{
  "title_en": "Short, clear title in English",
  "title_es": "Título claro en español",
  "title_ru": "Четкое название на русском",
  "description_en": "Comprehensive explanation in English (3-5 paragraphs). Include:
    - Clear definition and purpose
    - When and how to use it
    - Common patterns and structures
    - Special cases and exceptions
    - Tips for remembering",
  "description_es": "Explicación completa en español (3-5 párrafos)",
  "description_ru": "Полное объяснение на русском (3-5 абзаца)",
  "examples": [
    {{
      "{language}": "Example sentence in {target_lang}",
      "en": "English translation",
      "es": "Traducción al español",
      "ru": "Перевод на русский",
      "explanation_en": "Why this example demonstrates the rule",
      "explanation_es": "Por qué este ejemplo demuestra la regla",
      "explanation_ru": "Почему этот пример демонстрирует правило"
    }},
    // Include 5-8 examples of varying complexity
  ],
  "tags": ["relevant", "searchable", "keywords"],
  "related_rules": ["related_rule_code_1", "related_rule_code_2"]
}}
```

**Requirements**:
1. Appropriate for {difficulty_level} level ({level_info['grammar_complexity']})
2. Examples must be practical and commonly used
3. Explanations should be clear and beginner-friendly
4. Include cultural context when relevant
5. Provide examples that build from simple to more complex
6. Use authentic, natural language in all translations
7. Highlight common mistakes learners make

Please respond ONLY with the JSON, no additional text."""

        return prompt

    def _parse_ai_response(
        self,
        content: str,
        rule_code: str,
        language: str,
        category: str,
        difficulty_level: str
    ) -> Optional[Dict[str, Any]]:
        """
        Parse AI response and construct grammar rule data.

        Args:
            content: AI response text
            rule_code: Unique rule code
            language: Target language
            category: Grammar category
            difficulty_level: CEFR level

        Returns:
            Grammar rule dictionary or None if parsing fails
        """
        try:
            # Extract JSON from response (handle markdown code blocks)
            content = content.strip()

            # Remove markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            # Parse JSON
            parsed = json.loads(content.strip())

            # Construct rule data
            rule_data = {
                "rule_code": rule_code,
                "language": language,
                "category": category,
                "difficulty_level": difficulty_level,
                "title_en": parsed.get("title_en", ""),
                "title_es": parsed.get("title_es"),
                "title_ru": parsed.get("title_ru"),
                "description_en": parsed.get("description_en", ""),
                "description_es": parsed.get("description_es"),
                "description_ru": parsed.get("description_ru"),
                "examples": parsed.get("examples", []),
                "tags": parsed.get("tags", []),
                "related_rules": parsed.get("related_rules", []),
            }

            # Validate required fields
            if not rule_data["title_en"] or not rule_data["description_en"]:
                logger.error(f"Missing required fields in AI response for {rule_code}")
                return None

            return rule_data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from AI response: {e}")
            logger.debug(f"AI response content: {content}")
            return None
        except Exception as e:
            logger.error(f"Error parsing AI response: {e}", exc_info=True)
            return None

    async def generate_category_rules(
        self,
        language: str,
        category: str,
        difficulty_levels: Optional[List[str]] = None,
        native_language: str = "en"
    ) -> Dict[str, Any]:
        """
        Generate all rules for a specific category.

        Args:
            language: Target language
            category: Grammar category
            difficulty_levels: List of CEFR levels to generate (default: all)
            native_language: Language for explanations

        Returns:
            Statistics about generated rules
        """
        if difficulty_levels is None:
            difficulty_levels = list(self.CEFR_LEVELS.keys())

        category_info = self.GRAMMAR_CATEGORIES.get(category)
        if not category_info:
            raise ValueError(f"Unknown category: {category}")

        subcategories = category_info["subcategories"]

        stats = {
            "category": category,
            "language": language,
            "total_attempted": 0,
            "total_created": 0,
            "total_skipped": 0,
            "total_failed": 0,
            "rules": []
        }

        # Generate rules for each subcategory and level
        for subcategory in subcategories:
            for level in difficulty_levels:
                stats["total_attempted"] += 1

                rule = await self.generate_grammar_rule(
                    language=language,
                    category=category,
                    subcategory=subcategory,
                    difficulty_level=level,
                    native_language=native_language
                )

                if rule:
                    stats["total_created"] += 1
                    stats["rules"].append(rule["rule_code"])
                elif rule is None:
                    stats["total_skipped"] += 1
                else:
                    stats["total_failed"] += 1

                # Small delay to avoid rate limits
                await asyncio.sleep(0.5)

        return stats

    async def generate_complete_grammar_library(
        self,
        language: str,
        native_language: str = "en",
        categories: Optional[List[str]] = None,
        difficulty_levels: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate a complete grammar library for a language.

        Args:
            language: Target language
            native_language: Language for explanations
            categories: List of categories to generate (default: all)
            difficulty_levels: List of CEFR levels (default: all)

        Returns:
            Comprehensive statistics
        """
        if categories is None:
            # Sort categories by priority
            categories = sorted(
                self.GRAMMAR_CATEGORIES.keys(),
                key=lambda c: self.GRAMMAR_CATEGORIES[c]["priority"]
            )

        if difficulty_levels is None:
            difficulty_levels = list(self.CEFR_LEVELS.keys())

        overall_stats = {
            "language": language,
            "native_language": native_language,
            "categories": [],
            "total_attempted": 0,
            "total_created": 0,
            "total_skipped": 0,
            "total_failed": 0,
        }

        for category in categories:
            logger.info(f"Generating rules for category: {category}")

            category_stats = await self.generate_category_rules(
                language=language,
                category=category,
                difficulty_levels=difficulty_levels,
                native_language=native_language
            )

            overall_stats["categories"].append(category_stats)
            overall_stats["total_attempted"] += category_stats["total_attempted"]
            overall_stats["total_created"] += category_stats["total_created"]
            overall_stats["total_skipped"] += category_stats["total_skipped"]
            overall_stats["total_failed"] += category_stats["total_failed"]

        logger.info(f"Grammar library generation complete: {overall_stats['total_created']} rules created")
        return overall_stats

    async def get_recommended_rules(
        self,
        user_id: int,
        language: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get personalized grammar rule recommendations for a user.

        Args:
            user_id: User ID
            language: Target language
            limit: Number of recommendations

        Returns:
            List of recommended grammar rules
        """
        # TODO: Integrate with user progress to determine level
        # For now, return rules appropriate for A1-A2 level

        try:
            # Get user's current level (simplified for now)
            user_level = "A1"  # This should come from user_progress or user_language_settings

            # Get rules for current level and one level up
            levels = [user_level]
            if user_level in ["A1", "A2", "B1", "B2", "C1"]:
                next_level = {
                    "A1": "A2",
                    "A2": "B1",
                    "B1": "B2",
                    "B2": "C1",
                    "C1": "C2"
                }
                levels.append(next_level[user_level])

            # Prioritize by category priority
            recommended_rules = []

            for category in sorted(
                self.GRAMMAR_CATEGORIES.keys(),
                key=lambda c: self.GRAMMAR_CATEGORIES[c]["priority"]
            ):
                for level in levels:
                    rules = await self.grammar_repo.get_rules_by_language(
                        language=language,
                        category=category,
                        difficulty_level=level,
                        limit=limit - len(recommended_rules)
                    )

                    recommended_rules.extend([dict(r) for r in rules])

                    if len(recommended_rules) >= limit:
                        break

                if len(recommended_rules) >= limit:
                    break

            return recommended_rules[:limit]

        except Exception as e:
            logger.error(f"Error getting recommended rules: {e}", exc_info=True)
            return []
