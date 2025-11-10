"""Conversation Manager - Central orchestrator for AI companion conversations."""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from telegram_bot_template.core.database import DatabaseManager
from telegram_bot_template.dao.user_dao import UserDAO
from telegram_bot_template.dao.conversation_message_dao import ConversationMessageDAO
from telegram_bot_template.dao.user_fact_dao import UserFactDAO
from telegram_bot_template.dao.user_profile_summary_dao import UserProfileSummaryDAO
from telegram_bot_template.services.rag_service import RAGService
from telegram_bot_template.services.information_extraction import InformationExtractionService
from telegram_bot_template.core.ai_provider import OpenRouterProvider, MockAIProvider
from telegram_bot_template.config.settings import BotConfig

logger = logging.getLogger(__name__)


class ConversationManager:
    """Orchestrates the conversation flow between all services."""

    def __init__(
        self,
        database_manager: DatabaseManager,
        rag_service: RAGService,
        ai_provider: Optional[OpenRouterProvider],
        config: BotConfig,
    ):
        """Initialize the conversation manager.
        
        Args:
            database_manager: Database connection manager
            rag_service: RAG service for memory retrieval
            ai_provider: AI provider for LLM calls
            config: Bot configuration
        """
        self.db = database_manager
        self.rag_service = rag_service
        self.ai_provider = ai_provider or MockAIProvider()
        self.config = config
        
        # Initialize DAOs
        self.user_dao = UserDAO(database_manager.pool)
        self.message_dao = ConversationMessageDAO(database_manager.pool)
        self.fact_dao = UserFactDAO(database_manager.pool)
        self.summary_dao = UserProfileSummaryDAO(database_manager.pool)
        
        # Initialize services
        self.info_extractor = InformationExtractionService(ai_provider)
        
        # Conversation state cache (in-memory for now)
        self.conversation_states: Dict[int, Dict[str, Any]] = {}
    
    async def process_message(
        self,
        user_id: int,
        message_text: str,
        sentiment_score: Optional[float] = None,
        is_voice: bool = False,
    ) -> str:
        """Process a user message and generate a response.
        
        Args:
            user_id: The user's ID
            message_text: The message content (transcribed if voice)
            sentiment_score: Optional sentiment score
            is_voice: Whether this was a voice message
            
        Returns:
            The AI response text
        """
        try:
            # Get or create conversation state
            state = self._get_conversation_state(user_id)
            
            # Retrieve relevant context from RAG
            context = await self._retrieve_context(user_id, message_text)
            
            # Get user profile summary if available
            profile = await self._get_user_profile(user_id)
            
            # Build the conversation prompt
            prompt = self._build_conversation_prompt(
                message_text=message_text,
                context=context,
                profile=profile,
                sentiment_score=sentiment_score,
                is_voice=is_voice,
                conversation_history=state.get("history", []),
            )
            
            # Get AI response
            response = await self.ai_provider.get_completion(prompt)
            
            # Update conversation state
            self._update_conversation_state(user_id, message_text, response)
            
            # Extract and store important facts (async, don't wait)
            # This runs in background to not delay response
            import asyncio
            asyncio.create_task(
                self._extract_and_store_facts(user_id, message_text, response)
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            return "I'm sorry, I encountered an error processing your message. Please try again."
    
    async def _retrieve_context(
        self,
        user_id: int,
        message_text: str,
        max_facts: int = 5,
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant context from RAG.
        
        Args:
            user_id: User ID
            message_text: Current message
            max_facts: Maximum number of facts to retrieve
            
        Returns:
            List of relevant facts
        """
        try:
            facts = await self.rag_service.retrieve_relevant_facts(
                user_id=user_id,
                query_text=message_text,  # Will be fixed in RAG service
                limit=max_facts,
            )
            return facts
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return []
    
    async def _get_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user profile summary.
        
        Args:
            user_id: User ID
            
        Returns:
            User profile data or None
        """
        try:
            summaries = await self.summary_dao.get_user_summaries(user_id)
            if summaries:
                # Combine recent summaries
                profile_data = {
                    "summaries": summaries[:3],  # Last 3 summaries
                    "last_updated": summaries[0].get("last_updated") if summaries else None,
                }
                return profile_data
            return None
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            return None
    
    def _build_conversation_prompt(
        self,
        message_text: str,
        context: List[Dict[str, Any]],
        profile: Optional[Dict[str, Any]],
        sentiment_score: Optional[float],
        is_voice: bool,
        conversation_history: List[Dict[str, str]],
    ) -> str:
        """Build the prompt for the LLM.
        
        Args:
            message_text: Current message
            context: Retrieved context facts
            profile: User profile data
            sentiment_score: Message sentiment
            is_voice: Whether this is a voice message
            conversation_history: Recent conversation history
            
        Returns:
            Formatted prompt
        """
        prompt = """You are a warm, empathetic AI companion engaged in a natural conversation.
Your personality traits:
- Friendly and supportive
- Good listener who remembers details
- Asks thoughtful follow-up questions
- Shows genuine interest in the user's life
- Maintains conversation continuity

"""
        
        # Add user profile if available
        if profile and profile.get("summaries"):
            prompt += "What you know about the user:\n"
            for summary in profile["summaries"][:2]:
                prompt += f"- {summary.get('summary_text', '')}\n"
            prompt += "\n"
        
        # Add retrieved context
        if context:
            prompt += "Relevant memories about this user:\n"
            for fact in context:
                prompt += f"- {fact.get('fact_text', '')}\n"
            prompt += "\n"
        
        # Add sentiment context
        if sentiment_score is not None:
            if sentiment_score > 0.5:
                prompt += "The user seems to be in a positive mood.\n"
            elif sentiment_score < -0.5:
                prompt += "The user seems to be feeling down or frustrated.\n"
            prompt += "\n"
        
        # Add conversation history
        if conversation_history:
            prompt += "Recent conversation:\n"
            for turn in conversation_history[-3:]:  # Last 3 turns
                prompt += f"User: {turn.get('user', '')}\n"
                prompt += f"You: {turn.get('assistant', '')}\n"
            prompt += "\n"
        
        # Add current message
        if is_voice:
            prompt += f"User said (voice message): {message_text}\n\n"
        else:
            prompt += f"User: {message_text}\n\n"
        
        prompt += """Respond naturally and personally. If you reference something from their past, 
do it naturally without saying "I remember" too often. Keep responses concise but warm.
If this is a voice conversation, keep your response suitable for text-to-speech (avoid complex formatting).

Your response:"""
        
        return prompt
    
    def _get_conversation_state(self, user_id: int) -> Dict[str, Any]:
        """Get or create conversation state for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Conversation state dictionary
        """
        if user_id not in self.conversation_states:
            self.conversation_states[user_id] = {
                "history": [],
                "last_message_time": None,
                "context_window": [],
            }
        return self.conversation_states[user_id]
    
    def _update_conversation_state(
        self,
        user_id: int,
        user_message: str,
        assistant_response: str,
    ) -> None:
        """Update conversation state after an exchange.
        
        Args:
            user_id: User ID
            user_message: User's message
            assistant_response: Assistant's response
        """
        state = self._get_conversation_state(user_id)
        
        # Add to history
        state["history"].append({
            "user": user_message,
            "assistant": assistant_response,
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        # Keep only last 10 exchanges
        if len(state["history"]) > 10:
            state["history"] = state["history"][-10:]
        
        # Update last message time
        state["last_message_time"] = datetime.utcnow()
        
        # Clear old states (cleanup)
        self._cleanup_old_states()
    
    def _cleanup_old_states(self) -> None:
        """Remove conversation states older than 1 hour."""
        current_time = datetime.utcnow()
        cutoff_time = current_time - timedelta(hours=1)
        
        users_to_remove = []
        for user_id, state in self.conversation_states.items():
            last_time = state.get("last_message_time")
            if last_time and last_time < cutoff_time:
                users_to_remove.append(user_id)
        
        for user_id in users_to_remove:
            del self.conversation_states[user_id]
    
    async def _extract_and_store_facts(
        self,
        user_id: int,
        user_message: str,
        assistant_response: str,
    ) -> None:
        """Extract and store facts from the conversation.
        
        Args:
            user_id: User ID
            user_message: User's message
            assistant_response: Assistant's response
        """
        try:
            # Extract facts from user message
            facts = await self.info_extractor.extract_facts(user_message)
            
            # Get existing facts to check for duplicates
            existing_facts = await self.fact_dao.get_user_facts(user_id, limit=100)
            existing_texts = [f.get("fact_text", "") for f in existing_facts]
            
            # Store new facts
            for fact in facts:
                if await self.info_extractor.should_store_fact(fact, existing_texts):
                    await self.rag_service.store_fact(
                        user_id=user_id,
                        fact_text=fact.get("fact", ""),
                        fact_summary=f"{fact.get('type', 'info')}: {fact.get('fact', '')}",
                    )
                    logger.info(f"Stored fact for user {user_id}: {fact.get('fact', '')[:50]}...")
            
        except Exception as e:
            logger.error(f"Error extracting and storing facts: {e}")
    
    async def generate_user_summary(self, user_id: int) -> Optional[str]:
        """Generate or update user profile summary.
        
        Args:
            user_id: User ID
            
        Returns:
            Generated summary text or None
        """
        try:
            # Get all user facts
            facts = await self.fact_dao.get_user_facts(user_id, limit=50)
            
            if not facts:
                return None
            
            # Group facts by type
            facts_text = "\n".join([f"- {f.get('fact_text', '')}" for f in facts])
            
            # Generate summary using LLM
            prompt = f"""Based on these facts about a user, create a concise profile summary:

{facts_text}

Create a natural, paragraph-form summary (2-3 sentences) that captures the key aspects of this person.
Focus on: personality, interests, life situation, and goals.

Summary:"""
            
            summary = await self.ai_provider.get_completion(prompt)
            
            # Store the summary
            await self.summary_dao.create_or_update_summary(
                user_id=user_id,
                summary_text=summary,
                summary_topic="general_profile",
            )
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating user summary: {e}")
            return None