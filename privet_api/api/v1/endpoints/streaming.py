"""Streaming chat endpoints with Server-Sent Events (SSE)."""

import asyncio
import json
import logging
from typing import AsyncGenerator
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from privet_api.api.deps import get_conversation_manager, get_ai_provider
from privet_api.services.conversation.conversation_manager import ConversationManager
from privet_api.services.ai.ai_provider import BaseAIProvider

logger = logging.getLogger(__name__)

router = APIRouter()


class StreamingChatRequest(BaseModel):
    """Request schema for streaming chat."""
    user_id: int
    message: str
    target_language: str = "es"
    native_language: str = "en"
    include_word_metadata: bool = True
    include_grammar_hints: bool = True


async def generate_sse_stream(
    user_id: int,
    message: str,
    target_language: str,
    native_language: str,
    include_word_metadata: bool,
    include_grammar_hints: bool,
    conversation_manager: ConversationManager,
    ai_provider: BaseAIProvider,
) -> AsyncGenerator[str, None]:
    """Generate Server-Sent Events stream for chat responses.

    Yields SSE-formatted messages with word metadata and grammar hints.
    """
    try:
        # Send initial connection event
        yield f"event: connected\ndata: {json.dumps({'status': 'connected'})}\n\n"

        # Get conversation context
        context = await conversation_manager.get_conversation_context(user_id, limit=5)

        # Build messages for AI
        messages = []
        for msg in context:
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })

        # Add current user message
        messages.append({"role": "user", "content": message})

        # Stream response from AI provider
        full_response = ""
        word_buffer = ""

        async for chunk in ai_provider.stream_chat(messages):
            content = chunk.get("content", "")

            if not content:
                continue

            full_response += content

            # Accumulate characters into words
            for char in content:
                if char.isspace() or char in ".,;:!?¿¡":
                    # End of word - send word event with metadata
                    if word_buffer.strip() and include_word_metadata:
                        word = word_buffer.strip()

                        # TODO: Look up word metadata (translation, etc.)
                        # For now, send word without metadata
                        word_data = {
                            "word": word,
                            "translation": None,  # TODO: integrate with word service
                            "is_known": False,
                        }

                        yield f"event: word\ndata: {json.dumps(word_data)}\n\n"

                    # Send the non-word character
                    if char in ".,;:!?¿¡":
                        yield f"event: punct\ndata: {json.dumps({'text': char})}\n\n"
                    elif char.isspace():
                        yield f"event: space\ndata: {json.dumps({'text': char})}\n\n"

                    word_buffer = ""
                else:
                    word_buffer += char

            # Small delay to prevent overwhelming the client
            await asyncio.sleep(0.01)

        # Send any remaining word
        if word_buffer.strip() and include_word_metadata:
            word = word_buffer.strip()
            word_data = {
                "word": word,
                "translation": None,
                "is_known": False,
            }
            yield f"event: word\ndata: {json.dumps(word_data)}\n\n"

        # Save message to database
        await conversation_manager.save_message(
            user_id=user_id,
            role="user",
            content=message
        )
        await conversation_manager.save_message(
            user_id=user_id,
            role="assistant",
            content=full_response
        )

        # Send completion event
        yield f"event: done\ndata: {json.dumps({'message': 'Stream complete', 'total_words': len(full_response.split())})}\n\n"

    except Exception as e:
        logger.error(f"Error in SSE stream: {e}", exc_info=True)
        error_data = {
            "error": str(e),
            "type": "stream_error"
        }
        yield f"event: error\ndata: {json.dumps(error_data)}\n\n"


@router.post("/chat")
async def stream_chat(
    request: StreamingChatRequest,
    conversation_manager: ConversationManager = Depends(get_conversation_manager),
    ai_provider: BaseAIProvider = Depends(get_ai_provider),
):
    """Stream chat response with Server-Sent Events.

    Returns a stream of events:
    - `connected`: Initial connection established
    - `word`: Individual word with metadata (translation, known status)
    - `punct`: Punctuation character
    - `space`: Space character
    - `grammar`: Grammar hint (if enabled)
    - `done`: Stream completed
    - `error`: Error occurred

    Usage:
    ```javascript
    const eventSource = new EventSource('/api/v1/streaming/chat');

    eventSource.addEventListener('word', (e) => {
      const data = JSON.parse(e.data);
      console.log('Word:', data.word, 'Translation:', data.translation);
    });

    eventSource.addEventListener('done', (e) => {
      console.log('Stream complete');
      eventSource.close();
    });
    ```
    """
    return StreamingResponse(
        generate_sse_stream(
            user_id=request.user_id,
            message=request.message,
            target_language=request.target_language,
            native_language=request.native_language,
            include_word_metadata=request.include_word_metadata,
            include_grammar_hints=request.include_grammar_hints,
            conversation_manager=conversation_manager,
            ai_provider=ai_provider,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )


@router.get("/chat/test")
async def test_sse():
    """Test SSE connection with a simple counter stream."""

    async def test_stream():
        for i in range(10):
            yield f"data: {json.dumps({'count': i, 'message': f'Test message {i}'})}\n\n"
            await asyncio.sleep(0.5)
        yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(
        test_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
