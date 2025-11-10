"""Repository for user facts operations."""

from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

from .base import BaseRepository

logger = logging.getLogger(__name__)


class FactRepository(BaseRepository):
    """Repository for user facts with vector embeddings."""

    async def create_fact(
        self,
        user_id: int,
        fact_text: str,
        fact_summary: Optional[str] = None,
        category: Optional[str] = None,
        source_message_id: Optional[int] = None,
        embedding: Optional[List[float]] = None,
        confidence: float = 1.0
    ) -> Dict[str, Any]:
        """Create a new user fact with optional embedding."""
        async with self._pool.acquire() as conn:
            # Convert embedding to pgvector format if provided
            vector_embedding = None
            if embedding is not None:
                # Format for pgvector: [1.0, 2.0, 3.0]
                vector_embedding = "[" + ",".join(str(x) for x in embedding) + "]"
            
            fact = await conn.fetchrow(
                """
                INSERT INTO user_facts 
                (user_id, fact_text, fact_summary, source_message_id, embedding, created_at)
                VALUES ($1, $2, $3, $4, $5::vector, $6)
                RETURNING *
                """,
                user_id,
                fact_text,
                fact_summary or fact_text[:200],
                source_message_id,
                vector_embedding,
                datetime.utcnow()
            )
            
            result = dict(fact)
            # Add additional fields
            result['category'] = category
            result['confidence'] = confidence
            
            return result

    async def get_fact(self, fact_id: int) -> Optional[Dict[str, Any]]:
        """Get fact by ID."""
        async with self._pool.acquire() as conn:
            fact = await conn.fetchrow(
                "SELECT * FROM user_facts WHERE id = $1",
                fact_id
            )
            return dict(fact) if fact else None

    async def get_user_facts(
        self,
        user_id: int,
        limit: int = 50,
        offset: int = 0,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get facts for a user with optional filtering."""
        async with self._pool.acquire() as conn:
            # Base query
            query = """
                SELECT * FROM user_facts 
                WHERE user_id = $1
            """
            params = [user_id]
            
            # Add category filter if provided (would need category column in DB)
            # For now, just use the base query
            
            query += " ORDER BY created_at DESC LIMIT $2 OFFSET $3"
            params.extend([limit, offset])
            
            facts = await conn.fetch(query, *params)
            return [dict(fact) for fact in facts]

    async def search_similar_facts(
        self,
        user_id: int,
        query_embedding: List[float],
        limit: int = 5,
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Search for similar facts using vector similarity."""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"Searching similar facts for user {user_id} with threshold {threshold}, limit {limit}")
        logger.debug(f"Query embedding dimension: {len(query_embedding)}")
        
        async with self._pool.acquire() as conn:
            # First check if user has any facts with embeddings
            count_result = await conn.fetchval(
                "SELECT COUNT(*) FROM user_facts WHERE user_id = $1 AND embedding IS NOT NULL",
                user_id
            )
            logger.info(f"User {user_id} has {count_result} facts with embeddings")
            
            if count_result == 0:
                logger.warning(f"No facts with embeddings found for user {user_id}")
                return []
            
            # Convert query embedding to pgvector format
            vector_query = "[" + ",".join(str(x) for x in query_embedding) + "]"
            
            logger.debug("Executing vector similarity search query")
            facts = await conn.fetch(
                """
                SELECT 
                    f.*,
                    1 - (embedding <=> $1::vector) as similarity
                FROM user_facts f
                WHERE user_id = $2 
                AND embedding IS NOT NULL
                AND 1 - (embedding <=> $1::vector) > $4
                ORDER BY embedding <=> $1::vector
                LIMIT $3
                """,
                vector_query,
                user_id,
                limit,
                threshold,
            )
            
            logger.info(f"Vector search returned {len(facts)} results")
            if facts:
                logger.debug(f"Top similarity score: {facts[0]['similarity']:.4f}")
            
            return [dict(fact) for fact in facts]

    async def search_facts_by_text(
        self,
        user_id: int,
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search facts by text content."""
        async with self._pool.acquire() as conn:
            # Use ILIKE for case-insensitive search
            search_pattern = f"%{query}%"
            
            facts = await conn.fetch(
                """
                SELECT * FROM user_facts 
                WHERE user_id = $1 
                AND (fact_text ILIKE $2 OR fact_summary ILIKE $2)
                ORDER BY created_at DESC
                LIMIT $3
                """,
                user_id,
                search_pattern,
                limit
            )
            return [dict(fact) for fact in facts]

    async def delete_fact(self, fact_id: int) -> bool:
        """Delete a fact."""
        result = await self.execute(
            "DELETE FROM user_facts WHERE id = $1",
            fact_id
        )
        return result.split()[-1] != "0"

    async def delete_user_facts(self, user_id: int) -> int:
        """Delete all facts for a user."""
        result = await self.execute(
            "DELETE FROM user_facts WHERE user_id = $1",
            user_id
        )
        parts = result.split()
        return int(parts[-1]) if len(parts) > 1 else 0

    async def update_fact_embedding(
        self,
        fact_id: int,
        embedding: List[float]
    ) -> bool:
        """Update the embedding for a fact."""
        vector_embedding = "[" + ",".join(str(x) for x in embedding) + "]"
        
        result = await self.execute(
            """
            UPDATE user_facts 
            SET embedding = $1::vector 
            WHERE id = $2
            """,
            vector_embedding,
            fact_id
        )
        return result.split()[-1] != "0"

    async def get_facts_without_embeddings(
        self,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get facts that don't have embeddings yet."""
        async with self._pool.acquire() as conn:
            facts = await conn.fetch(
                """
                SELECT * FROM user_facts 
                WHERE embedding IS NULL 
                LIMIT $1
                """,
                limit
            )
            return [dict(fact) for fact in facts]

    async def get_fact_count(self, user_id: int) -> int:
        """Get total fact count for a user."""
        count = await self.fetchval(
            "SELECT COUNT(*) FROM user_facts WHERE user_id = $1",
            user_id
        )
        return count or 0

    async def get_recent_facts(
        self,
        user_id: int,
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """Get recent facts within specified hours."""
        async with self._pool.acquire() as conn:
            facts = await conn.fetch(
                """
                SELECT * FROM user_facts 
                WHERE user_id = $1 
                AND created_at > NOW() - INTERVAL '%s hours'
                ORDER BY created_at DESC
                """ % hours,
                user_id
            )
            return [dict(fact) for fact in facts]