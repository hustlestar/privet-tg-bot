"""Service for extracting and classifying important information from conversations."""

import logging
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from enum import Enum

from telegram_bot_template.core.ai_provider import OpenRouterProvider, MockAIProvider

logger = logging.getLogger(__name__)


class InformationType(Enum):
    """Types of information that can be extracted."""
    PERSONAL_FACT = "personal_fact"  # Name, age, location, occupation
    PREFERENCE = "preference"  # Likes, dislikes, favorites
    MEMORY = "memory"  # Events, experiences, stories
    ROUTINE = "routine"  # Daily habits, schedules
    RELATIONSHIP = "relationship"  # Family, friends, connections
    GOAL = "goal"  # Aspirations, plans, objectives
    EMOTION = "emotion"  # Feelings, mood, emotional state
    SKILL = "skill"  # Abilities, expertise, knowledge areas
    HEALTH = "health"  # Medical info, conditions, wellness
    CONTEXT = "context"  # Current situation, environment


class InformationExtractionService:
    """Extract and classify important information from user conversations."""

    def __init__(self, ai_provider: Optional[OpenRouterProvider] = None):
        """Initialize the information extraction service.
        
        Args:
            ai_provider: AI provider for LLM-based extraction
        """
        self.ai_provider = ai_provider or MockAIProvider()
        
    async def extract_facts(
        self,
        conversation_text: str,
        user_context: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Extract important facts from a conversation.
        
        Args:
            conversation_text: The text to extract facts from
            user_context: Optional context about the user
            
        Returns:
            List of extracted facts with metadata
        """
        try:
            # Build extraction prompt
            prompt = self._build_extraction_prompt(conversation_text, user_context)
            
            # Call LLM for extraction
            response = await self.ai_provider.get_completion(prompt)
            
            # Parse the response
            facts = self._parse_extraction_response(response)
            
            logger.info(f"Extracted {len(facts)} facts from conversation")
            return facts
            
        except Exception as e:
            logger.error(f"Error extracting facts: {e}")
            return []
    
    def _build_extraction_prompt(
        self,
        conversation_text: str,
        user_context: Optional[str] = None,
    ) -> str:
        """Build a prompt for fact extraction.
        
        Args:
            conversation_text: The conversation text
            user_context: Optional user context
            
        Returns:
            Formatted prompt for the LLM
        """
        prompt = """You are an AI assistant specialized in extracting important information from conversations.
Your task is to identify and extract key facts, memories, and preferences from the user's message.

IMPORTANT: Only extract information that is:
1. Explicitly stated by the user
2. Personal and specific to the user
3. Worth remembering for future conversations
4. Not already known from the context

For each piece of information, classify it into one of these categories:
- personal_fact: Name, age, location, occupation, identity
- preference: Likes, dislikes, favorites, opinions
- memory: Events, experiences, stories from the past
- routine: Daily habits, schedules, regular activities
- relationship: Family, friends, social connections
- goal: Aspirations, plans, objectives, desires
- emotion: Current feelings, mood, emotional state
- skill: Abilities, expertise, knowledge areas
- health: Medical info, conditions, wellness
- context: Current situation, environment, temporary state

"""
        
        if user_context:
            prompt += f"Known context about the user:\n{user_context}\n\n"
        
        prompt += f"""User's message:
{conversation_text}

Extract facts in JSON format:
{{
    "facts": [
        {{
            "type": "category_name",
            "fact": "The specific fact or information",
            "confidence": 0.0-1.0,
            "importance": "low/medium/high",
            "temporal": true/false (is this temporary or permanent?)
        }}
    ]
}}

If no important facts are found, return: {{"facts": []}}

JSON Response:"""
        
        return prompt
    
    def _parse_extraction_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse the LLM response into structured facts.
        
        Args:
            response: Raw LLM response
            
        Returns:
            List of parsed facts
        """
        try:
            # Try to extract JSON from the response
            # Handle cases where LLM adds extra text
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                data = json.loads(json_str)
                
                facts = []
                for fact_data in data.get("facts", []):
                    # Validate and clean the fact
                    fact = {
                        "type": fact_data.get("type", "context"),
                        "fact": fact_data.get("fact", ""),
                        "confidence": float(fact_data.get("confidence", 0.5)),
                        "importance": fact_data.get("importance", "medium"),
                        "temporal": fact_data.get("temporal", False),
                        "extracted_at": datetime.utcnow().isoformat(),
                    }
                    
                    # Only include facts with content and reasonable confidence
                    if fact["fact"] and fact["confidence"] >= 0.3:
                        facts.append(fact)
                
                return facts
            else:
                logger.warning("No valid JSON found in extraction response")
                return []
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse extraction response as JSON: {e}")
            return []
        except Exception as e:
            logger.error(f"Error parsing extraction response: {e}")
            return []
    
    async def classify_importance(
        self,
        fact_text: str,
        fact_type: str,
    ) -> Tuple[str, float]:
        """Classify the importance of a fact.
        
        Args:
            fact_text: The fact to classify
            fact_type: The type of fact
            
        Returns:
            Tuple of (importance_level, confidence_score)
        """
        # Simple heuristic-based importance classification
        # Can be enhanced with ML models later
        
        high_importance_types = {
            "personal_fact", "relationship", "health", "goal"
        }
        medium_importance_types = {
            "preference", "skill", "routine", "memory"
        }
        
        if fact_type in high_importance_types:
            return ("high", 0.8)
        elif fact_type in medium_importance_types:
            return ("medium", 0.7)
        else:
            return ("low", 0.6)
    
    async def should_store_fact(
        self,
        fact: Dict[str, Any],
        existing_facts: List[str],
    ) -> bool:
        """Determine if a fact should be stored.
        
        Args:
            fact: The fact to evaluate
            existing_facts: List of existing fact texts for comparison
            
        Returns:
            True if the fact should be stored
        """
        # Check importance threshold
        if fact.get("importance") == "low" and fact.get("confidence", 0) < 0.5:
            return False
        
        # Check for duplicates (simple text similarity for now)
        fact_text = fact.get("fact", "").lower()
        for existing in existing_facts:
            if fact_text in existing.lower() or existing.lower() in fact_text:
                logger.debug(f"Skipping duplicate fact: {fact_text[:50]}...")
                return False
        
        return True
    
    async def summarize_facts(
        self,
        facts: List[Dict[str, Any]],
    ) -> str:
        """Create a summary of extracted facts.
        
        Args:
            facts: List of facts to summarize
            
        Returns:
            Natural language summary
        """
        if not facts:
            return "No significant information extracted."
        
        # Group facts by type
        facts_by_type = {}
        for fact in facts:
            fact_type = fact.get("type", "other")
            if fact_type not in facts_by_type:
                facts_by_type[fact_type] = []
            facts_by_type[fact_type].append(fact.get("fact", ""))
        
        # Build summary
        summary_parts = []
        type_descriptions = {
            "personal_fact": "Personal details",
            "preference": "Preferences",
            "memory": "Memories",
            "routine": "Routines",
            "relationship": "Relationships",
            "goal": "Goals",
            "emotion": "Emotional state",
            "skill": "Skills",
            "health": "Health information",
            "context": "Context",
        }
        
        for fact_type, fact_list in facts_by_type.items():
            type_desc = type_descriptions.get(fact_type, fact_type.replace("_", " ").title())
            facts_text = ", ".join(fact_list[:3])  # Limit to first 3 for brevity
            if len(fact_list) > 3:
                facts_text += f" (and {len(fact_list) - 3} more)"
            summary_parts.append(f"{type_desc}: {facts_text}")
        
        return " | ".join(summary_parts)