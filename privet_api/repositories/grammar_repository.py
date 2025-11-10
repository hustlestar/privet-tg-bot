"""Repository for grammar rules operations."""

import asyncpg
from typing import Optional, List, Dict, Any
import logging

from .base import BaseRepository

logger = logging.getLogger(__name__)


class GrammarRepository(BaseRepository):
    """Repository for grammar rules data access."""

    async def create_rule(
        self,
        rule_code: str,
        language: str,
        category: str,
        difficulty_level: str,
        title_en: str,
        description_en: str,
        title_es: Optional[str] = None,
        title_ru: Optional[str] = None,
        description_es: Optional[str] = None,
        description_ru: Optional[str] = None,
        examples: Optional[List[Dict[str, Any]]] = None,
        tags: Optional[List[str]] = None,
        related_rules: Optional[List[str]] = None,
        order_index: int = 0,
    ) -> Optional[asyncpg.Record]:
        """Create a new grammar rule."""
        query = """
            INSERT INTO grammar_rules (
                rule_code, language, category, difficulty_level,
                title_en, title_es, title_ru,
                description_en, description_es, description_ru,
                examples, tags, related_rules, order_index,
                created_at, updated_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, NOW(), NOW())
            RETURNING *
        """
        try:
            import json
            examples_json = json.dumps(examples) if examples else None

            return await self.fetchrow(
                query,
                rule_code,
                language,
                category,
                difficulty_level,
                title_en,
                title_es,
                title_ru,
                description_en,
                description_es,
                description_ru,
                examples_json,
                tags,
                related_rules,
                order_index,
            )
        except Exception as e:
            logger.error(f"Error creating grammar rule: {e}", exc_info=True)
            return None

    async def get_rule_by_code(self, rule_code: str) -> Optional[asyncpg.Record]:
        """Get a grammar rule by its code."""
        query = "SELECT * FROM grammar_rules WHERE rule_code = $1 AND is_active = TRUE"
        try:
            return await self.fetchrow(query, rule_code)
        except Exception as e:
            logger.error(f"Error fetching grammar rule: {e}", exc_info=True)
            return None

    async def get_rules_by_language(
        self,
        language: str,
        category: Optional[str] = None,
        difficulty_level: Optional[str] = None,
        offset: int = 0,
        limit: int = 50,
    ) -> List[asyncpg.Record]:
        """Get grammar rules for a language with optional filtering."""
        conditions = ["language = $1", "is_active = TRUE"]
        params: List[Any] = [language]
        param_count = 1

        if category:
            param_count += 1
            conditions.append(f"category = ${param_count}")
            params.append(category)

        if difficulty_level:
            param_count += 1
            conditions.append(f"difficulty_level = ${param_count}")
            params.append(difficulty_level)

        param_count += 1
        offset_param = f"${param_count}"
        params.append(offset)

        param_count += 1
        limit_param = f"${param_count}"
        params.append(limit)

        query = f"""
            SELECT * FROM grammar_rules
            WHERE {' AND '.join(conditions)}
            ORDER BY order_index ASC, created_at ASC
            OFFSET {offset_param} LIMIT {limit_param}
        """
        try:
            return await self.fetch(query, *params)
        except Exception as e:
            logger.error(f"Error fetching grammar rules: {e}", exc_info=True)
            return []

    async def count_rules(
        self,
        language: str,
        category: Optional[str] = None,
        difficulty_level: Optional[str] = None,
    ) -> int:
        """Count grammar rules with optional filtering."""
        conditions = ["language = $1", "is_active = TRUE"]
        params: List[Any] = [language]

        if category:
            conditions.append(f"category = $2")
            params.append(category)

        if difficulty_level:
            param_idx = 3 if category else 2
            conditions.append(f"difficulty_level = ${param_idx}")
            params.append(difficulty_level)

        query = f"""
            SELECT COUNT(*) FROM grammar_rules
            WHERE {' AND '.join(conditions)}
        """
        try:
            return await self.fetchval(query, *params) or 0
        except Exception as e:
            logger.error(f"Error counting grammar rules: {e}", exc_info=True)
            return 0

    async def search_rules(
        self,
        language: str,
        search_query: str,
        limit: int = 20,
    ) -> List[asyncpg.Record]:
        """Search grammar rules by title or tags."""
        query = """
            SELECT * FROM grammar_rules
            WHERE language = $1
              AND is_active = TRUE
              AND (
                title_en ILIKE $2
                OR title_es ILIKE $2
                OR title_ru ILIKE $2
                OR $3 = ANY(tags)
              )
            ORDER BY order_index ASC
            LIMIT $4
        """
        try:
            search_pattern = f"%{search_query}%"
            return await self.fetch(query, language, search_pattern, search_query, limit)
        except Exception as e:
            logger.error(f"Error searching grammar rules: {e}", exc_info=True)
            return []

    async def get_categories(self, language: str) -> List[str]:
        """Get all unique categories for a language."""
        query = """
            SELECT DISTINCT category FROM grammar_rules
            WHERE language = $1 AND is_active = TRUE
            ORDER BY category
        """
        try:
            rows = await self.fetch(query, language)
            return [row['category'] for row in rows]
        except Exception as e:
            logger.error(f"Error fetching categories: {e}", exc_info=True)
            return []

    async def update_rule(
        self,
        rule_code: str,
        **fields,
    ) -> Optional[asyncpg.Record]:
        """Update a grammar rule."""
        if not fields:
            return await self.get_rule_by_code(rule_code)

        # Build SET clause dynamically
        set_clauses = []
        params = []
        param_count = 1

        for field, value in fields.items():
            if value is not None:
                set_clauses.append(f"{field} = ${param_count}")
                params.append(value)
                param_count += 1

        if not set_clauses:
            return await self.get_rule_by_code(rule_code)

        set_clauses.append(f"updated_at = NOW()")
        params.append(rule_code)

        query = f"""
            UPDATE grammar_rules
            SET {', '.join(set_clauses)}
            WHERE rule_code = ${param_count}
            RETURNING *
        """
        try:
            return await self.fetchrow(query, *params)
        except Exception as e:
            logger.error(f"Error updating grammar rule: {e}", exc_info=True)
            return None

    async def delete_rule(self, rule_code: str) -> bool:
        """Soft delete a grammar rule."""
        query = """
            UPDATE grammar_rules
            SET is_active = FALSE, updated_at = NOW()
            WHERE rule_code = $1
        """
        try:
            result = await self.execute(query, rule_code)
            return result == "UPDATE 1"
        except Exception as e:
            logger.error(f"Error deleting grammar rule: {e}", exc_info=True)
            return False
