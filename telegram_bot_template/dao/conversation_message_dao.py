"""DAO for conversation_messages table."""

import json
from datetime import datetime
from typing import Optional, Dict, Any, List

from .base_dao import BaseDAO


class ConversationMessageDAO(BaseDAO):
    """Data Access Object for conversation messages."""

    async def create_message(
        self,
        user_id: int,
        message_text: Optional[str] = None,
        transcribed_text: Optional[str] = None,
        sentiment_score: Optional[float] = None,
        raw_telegram_message: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a new conversation message."""
        async with self._pool.acquire() as conn:
            # Convert dict to JSON string for JSONB field
            raw_message_json = json.dumps(raw_telegram_message) if raw_telegram_message else None
            
            message = await conn.fetchrow(
                """
                INSERT INTO conversation_messages 
                (user_id, message_text, transcribed_text, sentiment_score, raw_telegram_message)
                VALUES ($1, $2, $3, $4, $5::jsonb)
                RETURNING *
                """,
                user_id,
                message_text,
                transcribed_text,
                sentiment_score,
                raw_message_json,
            )
            return dict(message)

    async def get_message(self, message_id: int) -> Optional[Dict[str, Any]]:
        """Get message by ID."""
        async with self._pool.acquire() as conn:
            message = await conn.fetchrow(
                "SELECT * FROM conversation_messages WHERE id = $1", message_id
            )
            return dict(message) if message else None

    async def get_user_messages(
        self, user_id: int, limit: int = 100, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get all messages for a user, newest first."""
        async with self._pool.acquire() as conn:
            messages = await conn.fetch(
                """
                SELECT * FROM conversation_messages 
                WHERE user_id = $1 
                ORDER BY created_at DESC 
                LIMIT $2 OFFSET $3
                """,
                user_id,
                limit,
                offset,
            )
            return [dict(msg) for msg in messages]

    async def get_messages_for_fact_extraction(
        self, user_id: int, since_hours: int = 24
    ) -> List[Dict[str, Any]]:
        """Get messages suitable for fact extraction (last N hours)."""
        async with self._pool.acquire() as conn:
            messages = await conn.fetch(
                """
                SELECT * FROM conversation_messages 
                WHERE user_id = $1 
                AND created_at > NOW() - INTERVAL '%s hours'
                AND (message_text IS NOT NULL OR transcribed_text IS NOT NULL)
                ORDER BY created_at ASC
                """,
                since_hours,
                user_id,
            )
            return [dict(msg) for msg in messages]

    async def delete_message(self, message_id: int) -> bool:
        """Delete a message."""
        async with self._pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM conversation_messages WHERE id = $1", message_id
            )
            return result.split()[-1] == "1"

    async def get_user_conversation_history(
        self, user_id: int, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get formatted conversation history for RAG context."""
        async with self._pool.acquire() as conn:
            messages = await conn.fetch(
                """
                SELECT 
                    id,
                    COALESCE(message_text, transcribed_text) as content,
                    sentiment_score,
                    created_at
                FROM conversation_messages 
                WHERE user_id = $1 
                AND (message_text IS NOT NULL OR transcribed_text IS NOT NULL)
                ORDER BY created_at DESC 
                LIMIT $2
                """,
                user_id,
                limit,
            )
            return [dict(msg) for msg in messages]