"""Conversation Manager - Central orchestrator for AI companion conversations."""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from privet_api.repositories.user_repository import UserRepository
from privet_api.repositories.conversation_repository import ConversationRepository
from privet_api.repositories.fact_repository import FactRepository
from privet_api.repositories.profile_repository import ProfileRepository
from privet_api.services.rag.rag_service import RAGService

logger = logging.getLogger(__name__)


class ConversationManager:
    """Orchestrates the conversation flow between all services."""

    def __init__(
        self,
        user_repository: UserRepository,
        conversation_repository: ConversationRepository,
        fact_repository: FactRepository,
        profile_repository: ProfileRepository,
        rag_service: RAGService,
        ai_provider: Any,  # Will be replaced with proper AI service
    ):
        """Initialize the conversation manager.
        
        Args:
            user_repository: User data repository
            conversation_repository: Conversation data repository
            fact_repository: Fact data repository
            profile_repository: Profile data repository
            rag_service: RAG service for memory retrieval
            ai_provider: AI provider for LLM calls
        """
        self.user_repo = user_repository
        self.conversation_repo = conversation_repository
        self.fact_repo = fact_repository
        self.profile_repo = profile_repository
        self.rag_service = rag_service
        self.ai_provider = ai_provider
        
        # Conversation state cache (in-memory for now)
        self.conversation_states: Dict[int, Dict[str, Any]] = {}
    
    async def process_message(
        self,
        user_id: int,
        message_text: str,
        sentiment_score: Optional[float] = None,
        emotion: Optional[str] = None,
        is_voice: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Process a user message and generate a response.
        
        Args:
            user_id: The user's ID
            message_text: The message content (transcribed if voice)
            sentiment_score: Optional sentiment score
            emotion: Optional detected emotion
            is_voice: Whether this was a voice message
            metadata: Additional message metadata
            
        Returns:
            Response dictionary with text and metadata
        """
        try:
            # Store the incoming message
            message = await self.conversation_repo.create_message(
                user_id=user_id,
                message_text=message_text if not is_voice else None,
                transcribed_text=message_text if is_voice else None,
                sentiment_score=sentiment_score,
                emotion=emotion,
                is_voice=is_voice,
                metadata=metadata,
            )
            
            # Get or create conversation state
            state = self._get_conversation_state(user_id)
            
            # Retrieve comprehensive context
            context = await self.rag_service.retrieve_context(
                user_id=user_id,
                query=message_text,
                max_facts=5,
                max_summaries=3,
                max_messages=10,
            )
            
            # Format context for LLM
            formatted_context = await self.rag_service.format_context_for_llm(context)
            
            # Build the conversation prompt
            prompt = self._build_conversation_prompt(
                message_text=message_text,
                formatted_context=formatted_context,
                sentiment_score=sentiment_score,
                emotion=emotion,
                is_voice=is_voice,
                conversation_history=state.get("history", []),
            )
            
            # Get AI response
            response_text = await self.ai_provider.get_completion(prompt)
            
            # Store the AI response
            ai_message = await self.conversation_repo.create_message(
                user_id=user_id,
                message_text=response_text,
                metadata={"role": "assistant"},
            )
            
            # Update conversation state
            self._update_conversation_state(user_id, message_text, response_text)
            
            # Extract and store facts asynchronously
            import asyncio
            asyncio.create_task(
                self._extract_and_store_facts(user_id, message_text)
            )
            
            # Check if profile summary needs updating
            if await self.profile_repo.needs_update(user_id):
                asyncio.create_task(self.generate_user_summary(user_id))
            
            return {
                "response": response_text,
                "message_id": ai_message["id"],
                "emotion": self._determine_response_emotion(sentiment_score, emotion),
                "metadata": {
                    "facts_count": len(context.get("relevant_facts", [])),
                    "context_used": bool(formatted_context),
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            return {
                "response": "I'm sorry, I encountered an error processing your message. Please try again.",
                "error": str(e)
            }
    
    def _build_conversation_prompt(
        self,
        message_text: str,
        formatted_context: str,
        sentiment_score: Optional[float],
        emotion: Optional[str],
        is_voice: bool,
        conversation_history: List[Dict[str, str]],
    ) -> str:
        """Build the prompt for the LLM.
        
        Args:
            message_text: Current message
            formatted_context: Pre-formatted context from RAG
            sentiment_score: Message sentiment
            emotion: Detected emotion
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
        
        # Add formatted context if available
        if formatted_context:
            prompt += formatted_context + "\n\n"
        
        # Add emotional context
        if sentiment_score is not None or emotion:
            prompt += "Emotional context:\n"
            if emotion:
                prompt += f"- User's emotion: {emotion}\n"
            if sentiment_score is not None:
                if sentiment_score > 0.5:
                    prompt += "- The user seems to be in a positive mood.\n"
                elif sentiment_score < -0.5:
                    prompt += "- The user seems to be feeling down or frustrated.\n"
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
    
    def _determine_response_emotion(
        self,
        sentiment_score: Optional[float],
        user_emotion: Optional[str]
    ) -> str:
        """Determine appropriate emotion for response.
        
        Args:
            sentiment_score: User's sentiment score
            user_emotion: User's detected emotion
            
        Returns:
            Emotion string for TTS
        """
        if user_emotion:
            # Mirror or complement user emotion
            emotion_map = {
                "happy": "cheerful",
                "sad": "empathetic",
                "angry": "calm",
                "excited": "enthusiastic",
                "neutral": "friendly",
                "anxious": "reassuring",
            }
            return emotion_map.get(user_emotion, "friendly")
        
        if sentiment_score is not None:
            if sentiment_score > 0.5:
                return "cheerful"
            elif sentiment_score < -0.5:
                return "empathetic"
        
        return "friendly"
    
    async def _extract_and_store_facts(
        self,
        user_id: int,
        message_text: str,
    ) -> None:
        """Extract and store facts from the message.
        
        Args:
            user_id: User ID
            message_text: User's message
        """
        try:
            # Use RAG service to process and store facts
            result = await self.rag_service.handle_message(
                user_id=user_id,
                message_text=message_text,
            )
            
            if result.get("facts_extracted"):
                logger.info(
                    f"Extracted {result['facts_count']} facts for user {user_id}"
                )
            
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
            facts = await self.fact_repo.get_user_facts(user_id, limit=50)
            
            if not facts:
                return None
            
            # Get recent messages for additional context
            messages = await self.conversation_repo.get_recent_messages(
                user_id=user_id,
                hours=24
            )
            
            # Build facts text
            facts_text = "\n".join([f"- {f.get('fact_text', '')}" for f in facts])
            
            # Build messages context
            messages_text = "\n".join([
                f"- {m.get('message_text', m.get('transcribed_text', ''))}"
                for m in messages[:10]
            ])
            
            # Generate summary using LLM
            prompt = f"""Based on these facts and recent conversations about a user, create a concise profile summary:

Facts:
{facts_text}

Recent messages:
{messages_text}

Create a natural, paragraph-form summary (2-3 sentences) that captures the key aspects of this person.
Focus on: personality, interests, life situation, and goals.

Summary:"""
            
            summary = await self.ai_provider.get_completion(prompt)
            
            # Store the summary
            stored_summary = await self.profile_repo.create_or_update_summary(
                user_id=user_id,
                summary_text=summary,
                summary_topic="general",
            )
            
            logger.info(f"Generated profile summary for user {user_id}")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating user summary: {e}")
            return None
    
    async def get_conversation_stats(self, user_id: int) -> Dict[str, Any]:
        """Get conversation statistics for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Statistics dictionary
        """
        try:
            # Get message counts
            total_messages = await self.conversation_repo.get_message_count(user_id)
            voice_messages = await self.conversation_repo.get_voice_message_count(user_id)
            
            # Get memory stats from RAG
            memory_stats = await self.rag_service.get_user_memory_stats(user_id)
            
            # Get profile summary count
            summary_count = await self.profile_repo.get_summary_count(user_id)
            
            return {
                "user_id": user_id,
                "total_messages": total_messages,
                "voice_messages": voice_messages,
                "text_messages": total_messages - voice_messages,
                "facts_stored": memory_stats.get("facts_stored", 0),
                "profile_summaries": summary_count,
                "memory_density": memory_stats.get("memory_density", 0),
                "last_interaction": self._get_conversation_state(user_id).get("last_message_time"),
            }
            
        except Exception as e:
            logger.error(f"Error getting conversation stats: {e}")
            return {"error": str(e)}