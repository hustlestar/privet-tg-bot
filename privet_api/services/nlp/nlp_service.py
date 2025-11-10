"""NLP Service for emotion analysis, sentiment detection, and conversation insights."""

import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class EmotionType(Enum):
    """Emotion categories for analysis."""
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    LOVE = "love"
    NEUTRAL = "neutral"
    EXCITEMENT = "excitement"
    GRATITUDE = "gratitude"
    FRUSTRATION = "frustration"
    ANXIETY = "anxiety"
    CONTENTMENT = "contentment"


@dataclass
class EmotionAnalysis:
    """Result of emotion analysis."""
    primary_emotion: EmotionType
    confidence: float
    sentiment_score: float  # -1 (negative) to 1 (positive)
    intensity: float  # 0 (low) to 1 (high)
    emotional_keywords: List[str]
    voice_tone_suggestion: str  # For TTS


class NLPService:
    """Service for natural language processing and emotional analysis."""

    def __init__(self):
        """Initialize the NLP service."""
        # Emotion keywords for pattern matching
        self.emotion_patterns = {
            EmotionType.JOY: [
                "happy", "joy", "glad", "pleased", "delighted", "cheerful",
                "😊", "😄", "😃", "🙂", "wonderful", "great", "amazing"
            ],
            EmotionType.SADNESS: [
                "sad", "unhappy", "depressed", "down", "blue", "crying",
                "😢", "😭", "😞", "disappointed", "heartbroken", "lonely"
            ],
            EmotionType.ANGER: [
                "angry", "mad", "furious", "annoyed", "irritated", "frustrated",
                "😠", "😡", "🤬", "hate", "upset", "pissed"
            ],
            EmotionType.FEAR: [
                "scared", "afraid", "terrified", "worried", "anxious", "nervous",
                "😨", "😰", "frightened", "panic", "alarmed"
            ],
            EmotionType.LOVE: [
                "love", "adore", "cherish", "❤️", "💕", "😍", "care",
                "affection", "fond", "devoted"
            ],
            EmotionType.EXCITEMENT: [
                "excited", "thrilled", "eager", "enthusiastic", "pumped",
                "🎉", "🎊", "can't wait", "looking forward"
            ],
            EmotionType.GRATITUDE: [
                "thank", "grateful", "appreciate", "thankful", "🙏",
                "blessed", "gratitude"
            ],
            EmotionType.FRUSTRATION: [
                "frustrated", "stuck", "confused", "lost", "overwhelmed",
                "😤", "struggling", "difficult"
            ],
        }
        
        # Sentiment indicators
        self.positive_indicators = [
            "good", "great", "excellent", "wonderful", "amazing", "fantastic",
            "love", "like", "enjoy", "happy", "pleased", "satisfied",
            "thank", "appreciate", "excited", "hope", "looking forward"
        ]
        
        self.negative_indicators = [
            "bad", "terrible", "awful", "hate", "dislike", "angry", "sad",
            "disappointed", "frustrated", "worried", "scared", "annoyed",
            "problem", "issue", "wrong", "fail", "can't", "won't", "don't"
        ]
        
        # Intensity modifiers
        self.intensity_modifiers = {
            "very": 1.3,
            "really": 1.3,
            "extremely": 1.5,
            "super": 1.4,
            "so": 1.2,
            "quite": 1.1,
            "somewhat": 0.8,
            "a bit": 0.7,
            "slightly": 0.6,
            "not very": 0.4,
            "not really": 0.3,
        }

    async def analyze_emotion(self, text: str) -> EmotionAnalysis:
        """Analyze the emotional content of text.
        
        Args:
            text: Text to analyze
            
        Returns:
            EmotionAnalysis object with results
        """
        text_lower = text.lower()
        
        # Detect emotions
        emotion_scores = self._detect_emotions(text_lower)
        primary_emotion = max(emotion_scores, key=emotion_scores.get)
        confidence = emotion_scores[primary_emotion]
        
        # Calculate sentiment
        sentiment_score = self._calculate_sentiment(text_lower)
        
        # Calculate intensity
        intensity = self._calculate_intensity(text_lower)
        
        # Extract emotional keywords
        keywords = self._extract_emotional_keywords(text_lower)
        
        # Suggest voice tone for TTS
        voice_tone = self._suggest_voice_tone(primary_emotion, intensity)
        
        return EmotionAnalysis(
            primary_emotion=primary_emotion,
            confidence=confidence,
            sentiment_score=sentiment_score,
            intensity=intensity,
            emotional_keywords=keywords,
            voice_tone_suggestion=voice_tone,
        )
    
    def _detect_emotions(self, text: str) -> Dict[EmotionType, float]:
        """Detect emotions in text.
        
        Args:
            text: Lowercase text to analyze
            
        Returns:
            Dictionary of emotion scores
        """
        scores = {emotion: 0.0 for emotion in EmotionType}
        
        for emotion, keywords in self.emotion_patterns.items():
            for keyword in keywords:
                if keyword in text:
                    scores[emotion] += 1.0
        
        # Normalize scores
        total = sum(scores.values())
        if total > 0:
            scores = {k: v / total for k, v in scores.items()}
        else:
            scores[EmotionType.NEUTRAL] = 1.0
        
        return scores
    
    def _calculate_sentiment(self, text: str) -> float:
        """Calculate sentiment score.
        
        Args:
            text: Lowercase text to analyze
            
        Returns:
            Sentiment score from -1 to 1
        """
        positive_count = sum(1 for word in self.positive_indicators if word in text)
        negative_count = sum(1 for word in self.negative_indicators if word in text)
        
        # Check for negations
        negation_words = ["not", "no", "never", "neither", "none", "nobody"]
        has_negation = any(neg in text for neg in negation_words)
        
        if has_negation:
            # Flip sentiment if negation is present
            positive_count, negative_count = negative_count, positive_count
        
        # Calculate score
        total = positive_count + negative_count
        if total == 0:
            return 0.0
        
        sentiment = (positive_count - negative_count) / total
        return max(-1.0, min(1.0, sentiment))
    
    def _calculate_intensity(self, text: str) -> float:
        """Calculate emotional intensity.
        
        Args:
            text: Lowercase text to analyze
            
        Returns:
            Intensity score from 0 to 1
        """
        base_intensity = 0.5
        
        # Check for intensity modifiers
        for modifier, multiplier in self.intensity_modifiers.items():
            if modifier in text:
                base_intensity *= multiplier
        
        # Check for exclamation marks
        exclamation_count = text.count("!")
        if exclamation_count > 0:
            base_intensity *= (1 + 0.1 * min(exclamation_count, 3))
        
        # Check for caps (original text needed)
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        if caps_ratio > 0.3:
            base_intensity *= 1.2
        
        return max(0.0, min(1.0, base_intensity))
    
    def _extract_emotional_keywords(self, text: str) -> List[str]:
        """Extract emotional keywords from text.
        
        Args:
            text: Lowercase text to analyze
            
        Returns:
            List of emotional keywords found
        """
        keywords = []
        
        # Check all emotion patterns
        for emotion_keywords in self.emotion_patterns.values():
            for keyword in emotion_keywords:
                if keyword in text and keyword not in keywords:
                    keywords.append(keyword)
        
        # Add sentiment indicators
        for word in self.positive_indicators + self.negative_indicators:
            if word in text and word not in keywords:
                keywords.append(word)
        
        return keywords[:10]  # Limit to 10 keywords
    
    def _suggest_voice_tone(self, emotion: EmotionType, intensity: float) -> str:
        """Suggest voice tone for TTS based on emotion.
        
        Args:
            emotion: Primary emotion
            intensity: Emotional intensity
            
        Returns:
            Voice tone suggestion string
        """
        tone_map = {
            EmotionType.JOY: "cheerful and warm",
            EmotionType.SADNESS: "gentle and compassionate",
            EmotionType.ANGER: "calm and understanding",
            EmotionType.FEAR: "reassuring and steady",
            EmotionType.LOVE: "warm and affectionate",
            EmotionType.EXCITEMENT: "energetic and enthusiastic",
            EmotionType.GRATITUDE: "appreciative and sincere",
            EmotionType.FRUSTRATION: "patient and supportive",
            EmotionType.NEUTRAL: "friendly and conversational",
        }
        
        base_tone = tone_map.get(emotion, "friendly")
        
        if intensity > 0.7:
            return f"very {base_tone}"
        elif intensity < 0.3:
            return f"slightly {base_tone}"
        else:
            return base_tone
    
    async def analyze_conversation_mood(
        self,
        messages: List[str],
    ) -> Dict[str, Any]:
        """Analyze the overall mood of a conversation.
        
        Args:
            messages: List of messages in chronological order
            
        Returns:
            Dictionary with mood analysis
        """
        if not messages:
            return {
                "overall_sentiment": 0.0,
                "mood_trajectory": "stable",
                "dominant_emotion": EmotionType.NEUTRAL.value,
            }
        
        # Analyze each message
        analyses = []
        for msg in messages:
            analysis = await self.analyze_emotion(msg)
            analyses.append(analysis)
        
        # Calculate overall sentiment
        overall_sentiment = sum(a.sentiment_score for a in analyses) / len(analyses)
        
        # Determine mood trajectory
        if len(analyses) >= 2:
            recent_sentiment = sum(a.sentiment_score for a in analyses[-2:]) / 2
            earlier_sentiment = sum(a.sentiment_score for a in analyses[:-2]) / max(len(analyses) - 2, 1)
            
            if recent_sentiment > earlier_sentiment + 0.3:
                trajectory = "improving"
            elif recent_sentiment < earlier_sentiment - 0.3:
                trajectory = "declining"
            else:
                trajectory = "stable"
        else:
            trajectory = "stable"
        
        # Find dominant emotion
        emotion_counts = {}
        for analysis in analyses:
            emotion = analysis.primary_emotion
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        dominant_emotion = max(emotion_counts, key=emotion_counts.get)
        
        return {
            "overall_sentiment": overall_sentiment,
            "mood_trajectory": trajectory,
            "dominant_emotion": dominant_emotion.value,
            "emotion_distribution": {
                k.value: v / len(analyses) for k, v in emotion_counts.items()
            },
        }
    
    def get_empathetic_response_modifier(
        self,
        emotion: EmotionType,
        sentiment: float,
    ) -> str:
        """Get a modifier for making responses more empathetic.
        
        Args:
            emotion: User's emotion
            sentiment: Sentiment score
            
        Returns:
            Text to add to prompt for empathetic response
        """
        if emotion == EmotionType.SADNESS:
            return "Respond with compassion and understanding. Acknowledge their feelings."
        elif emotion == EmotionType.ANGER:
            return "Stay calm and validate their frustration without escalating."
        elif emotion == EmotionType.FEAR:
            return "Be reassuring and supportive. Help them feel safe."
        elif emotion == EmotionType.JOY:
            return "Share in their happiness and enthusiasm."
        elif emotion == EmotionType.FRUSTRATION:
            return "Show patience and offer helpful suggestions if appropriate."
        elif sentiment < -0.3:
            return "Be supportive and understanding of their difficulties."
        elif sentiment > 0.3:
            return "Match their positive energy while being genuine."
        else:
            return "Be friendly and engaged in the conversation."