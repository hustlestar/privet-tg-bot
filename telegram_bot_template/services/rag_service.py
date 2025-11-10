"""RAG (Retrieval-Augmented Generation) Service for personalized memory."""

import logging
import asyncio
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from datetime import datetime
from openai import AsyncOpenAI

from telegram_bot_template.dao.user_fact_dao import UserFactDAO
from telegram_bot_template.dao.user_profile_summary_dao import UserProfileSummaryDAO
from telegram_bot_template.dao.conversation_message_dao import ConversationMessageDAO

logger = logging.getLogger(__name__)


class RAGService:
    """RAG service for managing vector embeddings and similarity search."""

    def __init__(
        self,
        database_pool,
        openai_api_key: Optional[str] = None,
        embedding_model: str = "text-embedding-3-small",
        embedding_dimension: int = 1536,  # OpenAI text-embedding-3-small default dimension
        similarity_threshold: float = 0.7,
    ):
        """Initialize RAG service with OpenAI embeddings.
        
        Args:
            database_pool: Database connection pool
            openai_api_key: OpenAI API key for embeddings
            embedding_model: OpenAI embedding model name
            embedding_dimension: Vector embedding dimension (1536 for text-embedding-3-small)
            similarity_threshold: Minimum similarity score for relevant facts
        """
        self._pool = database_pool
        self._user_fact_dao = UserFactDAO(database_pool)
        self._user_profile_summary_dao = UserProfileSummaryDAO(database_pool)
        self._conversation_message_dao = ConversationMessageDAO(database_pool)
        
        # Initialize OpenAI client for embeddings
        if openai_api_key:
            self._openai_client = AsyncOpenAI(api_key=openai_api_key)
        else:
            # Try to get from environment
            self._openai_client = AsyncOpenAI()
        
        self._embedding_model = embedding_model
        self._embedding_dimension = embedding_dimension
        self._similarity_threshold = similarity_threshold
        
        logger.info(
            f"RAG Service initialized with OpenAI model: {embedding_model}, "
            f"dimension: {embedding_dimension}"
        )

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate vector embedding for text using OpenAI with retry logic.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                # Generate embedding using OpenAI API
                response = await self._openai_client.embeddings.create(
                    model=self._embedding_model,
                    input=text,
                    dimensions=self._embedding_dimension,  # Optional: specify dimension for models that support it
                    timeout=30 + (attempt * 10)  # Increase timeout with retries
                )
                
                # Extract embedding vector
                vector = response.data[0].embedding
                
                # Ensure correct dimension
                if len(vector) != self._embedding_dimension:
                    logger.warning(
                        f"Embedding dimension mismatch: expected {self._embedding_dimension}, "
                        f"got {len(vector)}"
                    )
                
                return vector
                
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)
                    logger.warning(f"OpenAI embedding attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    logger.error(f"Error generating OpenAI embedding after {max_retries} attempts: {e}")
                    # Return zero vector as fallback
                    return [0.0] * self._embedding_dimension

    async def retrieve_relevant_facts(
        self,
        user_id: int,
        query_text: str,
        limit: int = 5,
        threshold: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant facts for a user based on query.
        
        Args:
            user_id: User ID
            query_text: Query text to search for
            limit: Maximum number of facts to return
            threshold: Minimum similarity threshold
            
        Returns:
            List of relevant facts with scores
        """
        try:
            # Use configured threshold if not provided
            threshold = threshold or self._similarity_threshold
            
            # Generate query embedding
            query_embedding = await self.generate_embedding(query_text)
            
            # Search for similar facts
            facts = await self._user_fact_dao.search_similar_facts(
                user_id=user_id,
                query_embedding=query_embedding,
                limit=limit,
                threshold=threshold,
            )
            
            logger.info(f"Retrieved {len(facts)} relevant facts for user {user_id}")
            return facts
            
        except Exception as e:
            logger.error(f"Error retrieving relevant facts: {e}")
            return []
    
    async def store_fact(
        self,
        user_id: int,
        fact_text: str,
        fact_summary: Optional[str] = None,
        source_message_id: Optional[int] = None,
    ) -> int:
        """Store a new fact with vector embedding.
        
        Args:
            user_id: User ID
            fact_text: Full fact text
            fact_summary: Optional summary of the fact
            source_message_id: Optional source message ID
            
        Returns:
            ID of the stored fact
        """
        try:
            # Generate embedding
            embedding = await self.generate_embedding(fact_text)
            
            # Store fact with embedding
            fact = await self._user_fact_dao.create_fact(
                user_id=user_id,
                fact_text=fact_text,
                fact_summary=fact_summary or fact_text[:200] + "...",
                source_message_id=source_message_id,
                embedding=embedding,
            )
            
            logger.info(f"Stored fact {fact['id']} for user {user_id}")
            return fact["id"]
            
        except Exception as e:
            logger.error(f"Error storing fact: {e}")
            raise


    async def retrieve_context(
        self,
        user_id: int,
        query: str,
        max_facts: int = 5,
        max_summaries: int = 3,
        max_messages: int = 10,
    ) -> Dict[str, Any]:
        """Retrieve comprehensive context for conversation.
        
        Args:
            user_id: User ID
            query: Current conversation query
            max_facts: Maximum number of facts to include
            max_summaries: Maximum number of profile summaries
            max_messages: Maximum number of recent messages
            
        Returns:
            Dictionary containing all relevant context
        """
        try:
            # Retrieve relevant facts
            facts = await self.retrieve_relevant_facts(
                user_id=user_id,
                query=query,
                limit=max_facts,
            )
            
            # Retrieve profile summaries
            summaries = await self._user_profile_summary_dao.get_profile_context(
                user_id=user_id,
                max_summaries=max_summaries,
            )
            
            # Retrieve recent conversation history
            messages = await self._conversation_message_dao.get_user_conversation_history(
                user_id=user_id,
                limit=max_messages,
            )
            
            # Format context
            context = {
                "relevant_facts": facts,
                "user_summaries": summaries,
                "recent_conversation": messages,
                "context_timestamp": datetime.utcnow().isoformat(),
            }
            
            logger.info(
                f"Retrieved context for user {user_id}: "
                f"{len(facts)} facts, {len(summaries)} summaries, {len(messages)} messages"
            )
            
            return context
            
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return {}

    async def format_context_for_llm(
        self, context: Dict[str, Any]
    ) -> str:
        """Format retrieved context for LLM prompt.
        
        Args:
            context: Retrieved context dictionary
            
        Returns:
            Formatted context string for LLM
        """
        try:
            formatted_parts = []
            
            # Add user summaries
            if context.get("user_summaries"):
                formatted_parts.append("=== User Profile Summary ===")
                for summary in context["user_summaries"]:
                    formatted_parts.append(
                        f"[{summary['summary_topic']}]: {summary['summary_text']}"
                    )
            
            # Add relevant facts
            if context.get("relevant_facts"):
                formatted_parts.append("\n=== Relevant User Facts ===")
                for fact in context["relevant_facts"]:
                    formatted_parts.append(f"- {fact['fact_text']}")
                    if fact.get("fact_summary") != fact["fact_text"]:
                        formatted_parts.append(f"  Summary: {fact['fact_summary']}")
            
            # Add recent conversation context
            if context.get("recent_conversation"):
                formatted_parts.append("\n=== Recent Conversation ===")
                for msg in context["recent_conversation"][:3]:  # Last 3 messages
                    formatted_parts.append(
                        f"[{msg['created_at'].strftime('%Y-%m-%d %H:%M')}]: "
                        f"{msg['content'][:100]}..."
                    )
            
            return "\n".join(formatted_parts)
            
        except Exception as e:
            logger.error(f"Error formatting context: {e}")
            return ""

    async def handle_message(
        self,
        user_id: int,
        message_text: str,
        source_message_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Process a new message and extract/store facts.
        
        Args:
            user_id: User ID
            message_text: Message content
            source_message_id: Optional source message ID
            
        Returns:
            Dictionary with processing results
        """
        try:
            # TODO: Integrate with Information Extraction Service
            # For now, we'll do simple keyword-based extraction
            
            facts_extracted = []
            
            # Simple keyword-based fact extraction
            keywords = [
                "i like", "i love", "i enjoy", "my favorite", "i prefer",
                "i work", "i study", "i live", "from", "born in",
                "my hobby", "i play", "i do", "i have", "my",
            ]
            
            lower_text = message_text.lower()
            for keyword in keywords:
                if keyword in lower_text:
                    # Extract sentence around keyword
                    start = max(0, lower_text.find(keyword) - 30)
                    end = min(len(message_text), lower_text.find(keyword) + 100)
                    fact = message_text[start:end].strip()
                    
                    fact_id = await self.store_fact(
                        user_id=user_id,
                        fact_text=fact,
                        source_message_id=source_message_id,
                    )
                    facts_extracted.append({
                        "fact_id": fact_id,
                        "fact_text": fact,
                        "keyword": keyword,
                    })
            
            return {
                "message_processed": True,
                "facts_extracted": facts_extracted,
                "facts_count": len(facts_extracted),
            }
            
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            return {"message_processed": False, "error": str(e)}

    async def get_user_memory_stats(self, user_id: int) -> Dict[str, Any]:
        """Get memory statistics for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with memory statistics
        """
        try:
            # Get facts count
            facts = await self._user_fact_dao.get_user_facts(user_id, limit=1000)
            
            # Get summaries
            summaries = await self._user_profile_summary_dao.get_user_summaries(user_id)
            
            # Get message count
            messages = await self._conversation_message_dao.get_user_messages(
                user_id, limit=1000
            )
            
            return {
                "user_id": user_id,
                "facts_stored": len(facts),
                "profile_summaries": len(summaries),
                "total_messages": len(messages),
                "memory_density": len(facts) / max(len(messages), 1),
                "last_fact_date": max(
                    [f["created_at"] for f in facts] or [datetime.utcnow()]
                ).isoformat() if facts else None,
            }
            
        except Exception as e:
            logger.error(f"Error getting memory stats: {e}")
            return {"error": str(e)}

    async def search_facts_by_keywords(
        self, user_id: int, keywords: List[str], limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search for facts by keywords.
        
        Args:
            user_id: User ID
            keywords: List of keywords to search for
            limit: Maximum results to return
            
        Returns:
            List of matching facts
        """
        try:
            return await self._user_fact_dao.get_facts_by_topic(
                user_id=user_id,
                topic_keywords=keywords,
                limit=limit,
            )
            
        except Exception as e:
            logger.error(f"Error searching facts by keywords: {e}")
            return []

    async def cleanup_old_facts(
        self, user_id: int, days_to_keep: int = 365
    ) -> int:
        """Clean up old facts (GDPR compliance).
        
        Args:
            user_id: User ID
            days_to_keep: Number of days to keep facts
            
        Returns:
            Number of facts deleted
        """
        try:
            # This would require implementing date-based deletion in UserFactDAO
            # For now, return 0 as placeholder
            logger.info(
                f"Cleanup old facts requested for user {user_id}, "
                f"keeping last {days_to_keep} days"
            )
            return 0
            
        except Exception as e:
            logger.error(f"Error cleaning up facts: {e}")
            return 0