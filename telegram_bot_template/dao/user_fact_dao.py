"""DAO for user_facts table."""

from typing import Optional, Dict, Any, List
from datetime import datetime

from .base_dao import BaseDAO


class UserFactDAO(BaseDAO):
    """Data Access Object for user facts."""

    async def create_fact(
        self,
        user_id: int,
        fact_text: str,
        fact_summary: Optional[str] = None,
        source_message_id: Optional[int] = None,
        embedding: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        """Create a new user fact."""
        async with self._pool.acquire() as conn:
            # Convert embedding list to pgvector format if provided
            vector_embedding = None
            if embedding is not None:
                # Convert list to PostgreSQL array format for pgvector
                # Format: [1.0, 2.0, 3.0] -> '{1.0, 2.0, 3.0}'
                vector_embedding = "[" + ",".join(str(x) for x in embedding) + "]"
            
            fact = await conn.fetchrow(
                """
                INSERT INTO user_facts (user_id, fact_text, fact_summary, source_message_id, embedding)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING *
                """,
                user_id,
                fact_text,
                fact_summary,
                source_message_id,
                vector_embedding,
            )
            return dict(fact)

    async def get_fact(self, fact_id: int) -> Optional[Dict[str, Any]]:
        """Get fact by ID."""
        async with self._pool.acquire() as conn:
            fact = await conn.fetchrow(
                "SELECT * FROM user_facts WHERE id = $1", fact_id
            )
            return dict(fact) if fact else None

    async def get_user_facts(
        self, user_id: int, limit: int = 50, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get all facts for a user, newest first."""
        async with self._pool.acquire() as conn:
            facts = await conn.fetch(
                """
                SELECT * FROM user_facts 
                WHERE user_id = $1 
                ORDER BY created_at DESC 
                LIMIT $2 OFFSET $3
                """,
                user_id,
                limit,
                offset,
            )
            return [dict(fact) for fact in facts]

    async def search_similar_facts(
        self, user_id: int, query_embedding: List[float], limit: int = 5, threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Search for similar facts using vector similarity."""
        async with self._pool.acquire() as conn:
            # Convert query embedding to proper format
            vector_query = "[" + ",".join(str(x) for x in query_embedding) + "]"
            
            facts = await conn.fetch(
                """
                SELECT 
                    id,
                    fact_text,
                    fact_summary,
                    source_message_id,
                    created_at,
                    1 - (embedding <=> $1::vector) as similarity
                FROM user_facts 
                WHERE user_id = $2 
                AND 1 - (embedding <=> $1::vector) > $4
                ORDER BY embedding <=> $1::vector
                LIMIT $3
                """,
                vector_query,
                user_id,
                limit,
                threshold,
            )
            return [dict(fact) for fact in facts]

    async def get_facts_by_topic(
        self, user_id: int, topic_keywords: List[str], limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get facts related to specific topics using keyword search."""
        async with self._pool.acquire() as conn:
            # Create case-insensitive search pattern
            search_pattern = "%" + "%".join(topic_keywords).lower() + "%"
            
            facts = await conn.fetch(
                """
                SELECT * FROM user_facts 
                WHERE user_id = $1 
                AND LOWER(fact_text) LIKE $2
                ORDER BY created_at DESC 
                LIMIT $3
                """,
                user_id,
                search_pattern,
                limit,
            )
            return [dict(fact) for fact in facts]

    async def update_fact(
        self, fact_id: int, fact_text: str, fact_summary: Optional[str] = None
    ) -> bool:
        """Update a fact's text and summary."""
        async with self._pool.acquire() as conn:
            result = await conn.execute(
                """
                UPDATE user_facts 
                SET fact_text = $1, fact_summary = $2 
                WHERE id = $3
                """,
                fact_text,
                fact_summary,
                fact_id,
            )
            return result.split()[-1] == "1"

    async def delete_fact(self, fact_id: int) -> bool:
        """Delete a fact."""
        async with self._pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM user_facts WHERE id = $1", fact_id
            )
            return result.split()[-1] == "1"

    async def delete_user_facts(self, user_id: int) -> int:
        """Delete all facts for a user (GDPR compliance)."""
        async with self._pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM user_facts WHERE user_id = $1", user_id
            )
            return int(result.split()[-1])

    async def get_facts_for_context(
        self, user_id: int, max_facts: int = 10
    ) -> List[Dict[str, Any]]:
        """Get facts formatted for conversation context."""
        async with self._pool.acquire() as conn:
            facts = await conn.fetch(
                """
                SELECT 
                    fact_text,
                    fact_summary,
                    created_at
                FROM user_facts 
                WHERE user_id = $1 
                ORDER BY created_at DESC 
                LIMIT $2
                """,
                user_id,
                max_facts,
            )
            return [dict(fact) for fact in facts]