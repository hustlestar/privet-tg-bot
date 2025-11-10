"""RAG (Retrieval-Augmented Generation) Service for personalized memory."""

import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from openai import AsyncOpenAI

from privet_api.repositories.fact_repository import FactRepository
from privet_api.repositories.profile_repository import ProfileRepository
from privet_api.repositories.conversation_repository import ConversationRepository

logger = logging.getLogger(__name__)


class RAGService:
    """RAG service for managing vector embeddings and similarity search."""

    def __init__(
        self,
        fact_repository: FactRepository,
        profile_repository: ProfileRepository,
        conversation_repository: ConversationRepository,
        openai_api_key: Optional[str] = None,
        embedding_model: str = "text-embedding-3-small",
        embedding_dimension: int = 1536,
        similarity_threshold: float = 0.7,
    ):
        """Initialize RAG service with OpenAI embeddings.
        
        Args:
            fact_repository: Repository for fact operations
            profile_repository: Repository for profile operations
            conversation_repository: Repository for conversation operations
            openai_api_key: OpenAI API key for embeddings
            embedding_model: OpenAI embedding model name
            embedding_dimension: Vector embedding dimension (1536 for text-embedding-3-small)
            similarity_threshold: Minimum similarity score for relevant facts
        """
        self._fact_repo = fact_repository
        self._profile_repo = profile_repository
        self._conversation_repo = conversation_repository
        
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
        
        if not self._openai_client:
            logger.warning("OpenAI client not initialized, returning zero vector")
            return [0.0] * self._embedding_dimension
        
        logger.info(f"Generating embedding for text: '{text[:100]}...' (length: {len(text)} chars)")
        
        for attempt in range(max_retries):
            try:
                # Generate embedding using OpenAI API
                logger.debug(f"Calling OpenAI embeddings API (attempt {attempt + 1}/{max_retries})")
                response = await self._openai_client.embeddings.create(
                    model=self._embedding_model,
                    input=text,
                    dimensions=self._embedding_dimension,
                    timeout=30 + (attempt * 10)
                )
                
                # Extract embedding vector
                vector = response.data[0].embedding
                
                logger.info(f"Successfully generated embedding: dimension={len(vector)}, model={self._embedding_model}")
                logger.debug(f"Embedding vector sample (first 5 values): {vector[:5] if vector else 'None'}")
                
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
            
            logger.info(f"Starting fact retrieval for user {user_id}, query: '{query_text[:100]}...'")
            logger.info(f"Search params: limit={limit}, threshold={threshold}")
            
            # Generate query embedding
            query_embedding = await self.generate_embedding(query_text)
            
            # Check if we got a valid embedding
            if not query_embedding or all(v == 0.0 for v in query_embedding):
                logger.warning("Got zero embedding vector, search may not work properly")
            
            # Search for similar facts
            logger.debug("Calling fact repository search_similar_facts")
            facts = await self._fact_repo.search_similar_facts(
                user_id=user_id,
                query_embedding=query_embedding,
                limit=limit,
                threshold=threshold,
            )
            
            logger.info(f"Retrieved {len(facts)} relevant facts for user {user_id}")
            if facts:
                logger.debug(f"Top result similarity: {facts[0].get('similarity', 'N/A') if facts and isinstance(facts[0], dict) else 'N/A'}")
            
            return facts
            
        except Exception as e:
            logger.error(f"Error retrieving relevant facts: {e}")
            return []
    
    async def store_fact(
        self,
        user_id: int,
        fact_text: str,
        fact_summary: Optional[str] = None,
        category: Optional[str] = None,
        source_message_id: Optional[int] = None,
        confidence: float = 1.0,
    ) -> int:
        """Store a new fact with vector embedding.
        
        Args:
            user_id: User ID
            fact_text: Full fact text
            fact_summary: Optional summary of the fact
            category: Optional category for the fact
            source_message_id: Optional source message ID
            confidence: Confidence score for the fact
            
        Returns:
            ID of the stored fact
        """
        try:
            # Generate embedding
            embedding = await self.generate_embedding(fact_text)
            
            # Store fact with embedding
            fact = await self._fact_repo.create_fact(
                user_id=user_id,
                fact_text=fact_text,
                fact_summary=fact_summary or fact_text[:200],
                category=category,
                source_message_id=source_message_id,
                embedding=embedding,
                confidence=confidence,
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
                query_text=query,
                limit=max_facts,
            )
            
            # Retrieve profile summaries
            summaries = await self._profile_repo.get_profile_context(
                user_id=user_id,
                max_summaries=max_summaries,
            )
            
            # Retrieve recent conversation history
            messages = await self._conversation_repo.get_conversation_history(
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
                    if fact.get("fact_summary") and fact.get("fact_summary") != fact["fact_text"]:
                        formatted_parts.append(f"  Summary: {fact['fact_summary']}")
            
            # Add recent conversation context
            if context.get("recent_conversation"):
                formatted_parts.append("\n=== Recent Conversation ===")
                for msg in context["recent_conversation"][:3]:  # Last 3 messages
                    content = msg.get('content', msg.get('message_text', ''))
                    if content:
                        timestamp = msg.get('created_at')
                        if timestamp:
                            if isinstance(timestamp, str):
                                formatted_parts.append(f"[{timestamp}]: {content[:100]}...")
                            else:
                                formatted_parts.append(
                                    f"[{timestamp.strftime('%Y-%m-%d %H:%M')}]: {content[:100]}..."
                                )
                        else:
                            formatted_parts.append(f"{content[:100]}...")
            
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
            facts = await self._fact_repo.get_user_facts(user_id, limit=1000)
            
            # Get summaries
            summaries = await self._profile_repo.get_user_summaries(user_id)
            
            # Get message count  
            message_count = await self._conversation_repo.get_message_count(user_id)
            
            # Calculate stats
            last_fact_date = None
            if facts:
                last_fact_date = max(
                    [f.get("created_at", datetime.utcnow()) for f in facts]
                ).isoformat()
            
            return {
                "user_id": user_id,
                "facts_stored": len(facts),
                "profile_summaries": len(summaries),
                "total_messages": message_count,
                "memory_density": len(facts) / max(message_count, 1),
                "last_fact_date": last_fact_date,
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
            # Join keywords for text search
            query = " ".join(keywords)
            return await self._fact_repo.search_facts_by_text(
                user_id=user_id,
                query=query,
                limit=limit,
            )
            
        except Exception as e:
            logger.error(f"Error searching facts by keywords: {e}")
            return []

    async def update_user_profile_summary(
        self,
        user_id: int,
        summary_text: str,
        summary_topic: str = "general",
    ) -> Dict[str, Any]:
        """Update or create a user profile summary.
        
        Args:
            user_id: User ID
            summary_text: Summary text
            summary_topic: Topic of the summary
            
        Returns:
            Created or updated summary
        """
        try:
            return await self._profile_repo.create_or_update_summary(
                user_id=user_id,
                summary_text=summary_text,
                summary_topic=summary_topic,
            )
        except Exception as e:
            logger.error(f"Error updating profile summary: {e}")
            raise

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
            # Get facts older than days_to_keep
            recent_facts = await self._fact_repo.get_recent_facts(
                user_id=user_id,
                hours=days_to_keep * 24
            )
            
            # Get all facts
            all_facts = await self._fact_repo.get_user_facts(
                user_id=user_id,
                limit=10000
            )
            
            # Find facts to delete
            recent_ids = {f['id'] for f in recent_facts}
            deleted_count = 0
            
            for fact in all_facts:
                if fact['id'] not in recent_ids:
                    if await self._fact_repo.delete_fact(fact['id']):
                        deleted_count += 1
            
            logger.info(
                f"Cleaned up {deleted_count} old facts for user {user_id}, "
                f"keeping last {days_to_keep} days"
            )
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up facts: {e}")
            return 0