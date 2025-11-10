"""Repository for conversation message operations."""

import json
from datetime import datetime
from typing import Optional, Dict, Any, List
import logging

from .base import BaseRepository

logger = logging.getLogger(__name__)


class ConversationRepository(BaseRepository):
    """Repository for conversation message operations."""

    async def create_message(
        self,
        user_id: int,
        message_text: Optional[str] = None,
        transcribed_text: Optional[str] = None,
        sentiment_score: Optional[float] = None,
        emotion: Optional[str] = None,
        is_voice: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a new conversation message."""
        async with self._pool.acquire() as conn:
            # Convert metadata to JSON string for JSONB field
            metadata_json = json.dumps(metadata) if metadata else None
            
            # Determine role (for now, all user messages)
            role = "user"
            
            message = await conn.fetchrow(
                """
                INSERT INTO conversation_messages 
                (user_id, message_text, transcribed_text, sentiment_score, 
                 raw_telegram_message, created_at)
                VALUES ($1, $2, $3, $4, $5::jsonb, $6)
                RETURNING *
                """,
                user_id,
                message_text,
                transcribed_text,
                sentiment_score,
                metadata_json,
                datetime.utcnow()
            )
            
            result = dict(message)
            # Add computed fields
            result['role'] = role
            result['is_voice'] = is_voice
            result['emotion'] = emotion
            
            return result

    async def get_message(self, message_id: int) -> Optional[Dict[str, Any]]:
        """Get message by ID."""
        async with self._pool.acquire() as conn:
            message = await conn.fetchrow(
                "SELECT * FROM conversation_messages WHERE id = $1", 
                message_id
            )
            return dict(message) if message else None

    async def get_user_messages(
        self, 
        user_id: int, 
        limit: int = 100, 
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get messages for a user with pagination."""
        async with self._pool.acquire() as conn:
            messages = await conn.fetch(
                """
                SELECT *,
                       COALESCE(message_text, transcribed_text) as content,
                       CASE 
                           WHEN transcribed_text IS NOT NULL THEN true 
                           ELSE false 
                       END as is_voice
                FROM conversation_messages 
                WHERE user_id = $1 
                ORDER BY created_at DESC 
                LIMIT $2 OFFSET $3
                """,
                user_id,
                limit,
                offset,
            )
            
            # Convert to dict and add required fields for the API schema
            result = []
            for msg in messages:
                msg_dict = dict(msg)
                
                # Determine role from metadata or default to user
                metadata = msg_dict.get('raw_telegram_message')
                if isinstance(metadata, str):
                    import json
                    try:
                        metadata = json.loads(metadata)
                    except (json.JSONDecodeError, TypeError):
                        metadata = {}
                elif not isinstance(metadata, dict):
                    metadata = {}
                
                # Check if this is an assistant message
                if metadata.get('role') == 'assistant':
                    msg_dict['role'] = 'assistant'
                else:
                    msg_dict['role'] = 'user'
                
                # Add emotion field if not present
                if 'emotion' not in msg_dict or msg_dict['emotion'] is None:
                    msg_dict['emotion'] = 'neutral'
                result.append(msg_dict)
            
            return result

    async def get_conversation_history(
        self, 
        user_id: int, 
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get formatted conversation history for context."""
        async with self._pool.acquire() as conn:
            messages = await conn.fetch(
                """
                SELECT 
                    id,
                    COALESCE(message_text, transcribed_text) as content,
                    sentiment_score,
                    created_at,
                    CASE 
                        WHEN transcribed_text IS NOT NULL THEN true 
                        ELSE false 
                    END as is_voice
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

    async def get_recent_messages(
        self, 
        user_id: int, 
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """Get recent messages within specified hours."""
        async with self._pool.acquire() as conn:
            messages = await conn.fetch(
                """
                SELECT * FROM conversation_messages 
                WHERE user_id = $1 
                AND created_at > NOW() - INTERVAL '%s hours'
                ORDER BY created_at DESC
                """ % hours,  # Safe since hours is an int
                user_id,
            )
            return [dict(msg) for msg in messages]

    async def delete_message(self, message_id: int) -> bool:
        """Delete a message."""
        result = await self.execute(
            "DELETE FROM conversation_messages WHERE id = $1", 
            message_id
        )
        return result.split()[-1] != "0"

    async def delete_user_messages(self, user_id: int) -> int:
        """Delete all messages for a user."""
        result = await self.execute(
            "DELETE FROM conversation_messages WHERE user_id = $1", 
            user_id
        )
        # Extract count from result like "DELETE 5"
        parts = result.split()
        return int(parts[-1]) if len(parts) > 1 else 0

    async def get_message_count(self, user_id: int) -> int:
        """Get total message count for a user."""
        count = await self.fetchval(
            "SELECT COUNT(*) FROM conversation_messages WHERE user_id = $1",
            user_id
        )
        return count or 0

    async def get_voice_message_count(self, user_id: int) -> int:
        """Get voice message count for a user."""
        count = await self.fetchval(
            """
            SELECT COUNT(*) FROM conversation_messages 
            WHERE user_id = $1 AND transcribed_text IS NOT NULL
            """,
            user_id
        )
        return count or 0

    async def update_sentiment(
        self, 
        message_id: int, 
        sentiment_score: float
    ) -> bool:
        """Update sentiment score for a message."""
        result = await self.execute(
            """
            UPDATE conversation_messages 
            SET sentiment_score = $1 
            WHERE id = $2
            """,
            sentiment_score,
            message_id
        )
        return result.split()[-1] != "0"