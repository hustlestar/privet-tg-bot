"""Conversation management endpoints."""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from asyncpg import Pool
import time

from privet_api.api.deps import (
    get_db_pool,
    get_conversation_manager,
    get_conversation_repository,
    get_nlp_service
)
from privet_api.models.schemas.conversation import (
    ConversationRequest,
    ConversationResponse,
    ConversationMessage,
    ConversationHistory,
    EmotionAnalysis
)

router = APIRouter()


@router.post("/process", response_model=ConversationResponse)
async def process_conversation(
    request: ConversationRequest,
    background_tasks: BackgroundTasks,
    conversation_manager = Depends(get_conversation_manager)
) -> ConversationResponse:
    """Process a conversation message and generate a response."""
    
    start_time = time.time()
    
    try:
        # Process the message through conversation manager
        result = await conversation_manager.process_message(
            user_id=request.user_id,
            message_text=request.message,
            sentiment_score=request.sentiment_score,
            emotion=request.emotion,
            is_voice=request.is_voice,
            metadata=request.metadata
        )
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        return ConversationResponse(
            response_text=result.get("response", ""),
            emotion=result.get("emotion", "neutral"),
            facts_extracted=result.get("metadata", {}).get("facts_count", 0),
            context_used=result.get("metadata", {}).get("context_used", False),
            processing_time_ms=processing_time_ms
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing conversation: {str(e)}"
        )


@router.get("/{user_id}/history", response_model=ConversationHistory)
async def get_conversation_history(
    user_id: int,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    conversation_repo = Depends(get_conversation_repository)
) -> ConversationHistory:
    """Get conversation history for a user."""
    
    try:
        # Get total count
        total = await conversation_repo.get_message_count(user_id)
        
        # Get messages
        messages = await conversation_repo.get_user_messages(
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        
        # Get date range
        date_range = None
        if messages:
            date_range = {
                "start": messages[-1].get("created_at"),
                "end": messages[0].get("created_at")
            }
        
        return ConversationHistory(
            user_id=user_id,
            messages=[ConversationMessage(**msg) for msg in messages],
            total_messages=total,
            date_range=date_range
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching conversation history: {str(e)}"
        )


@router.post("/{user_id}/analyze-emotion", response_model=EmotionAnalysis)
async def analyze_emotion(
    user_id: int,
    text: str,
    nlp_service = Depends(get_nlp_service)
) -> EmotionAnalysis:
    """Analyze emotion in text."""
    
    try:
        # Analyze emotion using NLP service
        analysis = await nlp_service.analyze_emotion(text)
        
        # Map emotion types to emotion scores
        emotion_map = {
            "joy": "happy",
            "sadness": "sad",
            "anger": "angry",
            "fear": "fearful",
            "surprise": "surprised",
            "neutral": "neutral"
        }
        
        emotions = {
            "neutral": 0.0,
            "happy": 0.0,
            "sad": 0.0,
            "angry": 0.0,
            "surprised": 0.0,
            "fearful": 0.0,
            "disgusted": 0.0
        }
        
        # Set the primary emotion score
        primary = emotion_map.get(analysis.primary_emotion.value, "neutral")
        emotions[primary] = analysis.confidence
        
        return EmotionAnalysis(
            text=text,
            sentiment_score=analysis.sentiment_score,
            primary_emotion=primary,
            confidence=analysis.confidence,
            emotions=emotions,
            voice_tone_suggestion=analysis.voice_tone_suggestion
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing emotion: {str(e)}"
        )


@router.delete("/{user_id}/messages/{message_id}")
async def delete_message(
    user_id: int,
    message_id: int,
    conversation_repo = Depends(get_conversation_repository)
) -> dict:
    """Delete a specific conversation message."""
    
    try:
        # Check if message exists
        message = await conversation_repo.get_message(message_id)
        if not message or message.get("user_id") != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )
        
        # Delete the message
        deleted = await conversation_repo.delete_message(message_id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )
        
        return {"message": f"Message {message_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting message: {str(e)}"
        )