"""Memory and RAG management endpoints."""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from asyncpg import Pool

from privet_api.api.deps import (
    get_db_pool,
    get_rag_service
)
from privet_api.models.schemas.memory import (
    UserFact,
    FactCreate,
    FactSearch,
    FactSearchResult,
    ProfileSummary,
    ProfileSummaryCreate,
    MemoryContext,
    MemoryStats
)

router = APIRouter()


@router.post("/facts", response_model=UserFact)
async def create_fact(
    fact_data: FactCreate,
    db_pool: Pool = Depends(get_db_pool)
) -> UserFact:
    """Store a new fact for a user."""
    
    # TODO: Integrate with RAG service for embedding generation
    # rag_service = get_rag_service()
    # fact_id = await rag_service.store_fact(
    #     user_id=fact_data.user_id
    #     fact_text=fact_data.fact_text
    #     fact_summary=fact_data.fact_summary
    # )
    
    async with db_pool.acquire() as conn:
        # For now, store without embedding
        fact = await conn.fetchrow(
            """
            INSERT INTO user_facts (user_id, fact_text, fact_summary, source_message_id, created_at)
            VALUES ($1, $2, $3, $4, NOW())
            RETURNING *
            """,
            fact_data.user_id,
            fact_data.fact_text,
            fact_data.fact_summary or fact_data.fact_text[:200],
            fact_data.source_message_id
        )
        
        return UserFact(**dict(fact))


@router.post("/facts/search", response_model=List[FactSearchResult])
async def search_facts(
    search_params: FactSearch,
    rag_service = Depends(get_rag_service),
    db_pool: Pool = Depends(get_db_pool)
) -> List[FactSearchResult]:
    """Search for relevant facts using semantic similarity."""
    
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"Searching facts for user {search_params.user_id} with query: '{search_params.query}'")
    logger.info(f"Search parameters: limit={search_params.limit}, min_similarity={search_params.min_similarity}")
    
    try:
        # Try vector search first if RAG service is available
        if rag_service and rag_service._openai_client:
            logger.info("Using vector similarity search with embeddings")
            
            # Get relevant facts using embeddings
            relevant_facts = await rag_service.retrieve_relevant_facts(
                user_id=search_params.user_id,
                query_text=search_params.query,
                limit=search_params.limit,
                threshold=search_params.min_similarity
            )
            
            logger.info(f"Vector search returned {len(relevant_facts)} results")
            
            results = []
            for fact_data in relevant_facts:
                # Extract similarity score if present
                similarity = fact_data.pop('similarity', 0.9) if isinstance(fact_data, dict) else 0.9
                
                # Create the fact object with remaining data
                results.append(FactSearchResult(
                    fact=UserFact(**fact_data),
                    similarity=similarity,
                    relevance_reason="Vector similarity"
                ))
            
            if results:
                logger.info(f"Returning {len(results)} vector search results")
                return results
            else:
                logger.info("No vector search results, falling back to text search")
        else:
            logger.warning("RAG service not available or no OpenAI client, using text search")
    except Exception as e:
        logger.error(f"Vector search failed: {e}, falling back to text search")
    
    # Fallback to text search
    logger.info("Using text-based search as fallback")
    async with db_pool.acquire() as conn:
        facts = await conn.fetch(
            """
            SELECT * FROM user_facts 
            WHERE user_id = $1 
            AND (fact_text ILIKE $2 OR fact_summary ILIKE $2)
            LIMIT $3
            """,
            search_params.user_id,
            f"%{search_params.query}%",
            search_params.limit
        )
        
        logger.info(f"Text search returned {len(facts)} results")
        
        results = []
        for fact in facts:
            results.append(FactSearchResult(
                fact=UserFact(**dict(fact)),
                similarity=0.8,  # Mock similarity for text match
                relevance_reason="Text match"
            ))
        
        return results


@router.get("/facts/{user_id}", response_model=List[UserFact])
async def get_user_facts(
    user_id: int,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    category: Optional[str] = None,
    db_pool: Pool = Depends(get_db_pool)
) -> List[UserFact]:
    """Get all facts for a user."""
    
    async with db_pool.acquire() as conn:
        query = """
            SELECT * FROM user_facts 
            WHERE user_id = $1
        """
        params = [user_id]
        
        if category:
            query += " AND category = $2"
            params.append(category)
        
        query += " ORDER BY created_at DESC LIMIT $%d OFFSET $%d" % (
            len(params) + 1,
            len(params) + 2
        )
        params.extend([limit, offset])
        
        facts = await conn.fetch(query, *params)
        
        return [UserFact(**dict(fact)) for fact in facts]


@router.delete("/facts/{fact_id}")
async def delete_fact(
    fact_id: int,
    db_pool: Pool = Depends(get_db_pool)
) -> dict:
    """Delete a specific fact."""
    
    async with db_pool.acquire() as conn:
        result = await conn.execute(
            "DELETE FROM user_facts WHERE id = $1",
            fact_id
        )
        
        if result == "DELETE 0":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fact not found"
            )
        
        return {"message": f"Fact {fact_id} deleted successfully"}


@router.post("/summaries/generate", response_model=ProfileSummary)
async def generate_profile_summary(
    request: ProfileSummaryCreate,
    background_tasks: BackgroundTasks,
    db_pool: Pool = Depends(get_db_pool)
) -> ProfileSummary:
    """Generate or update user profile summary."""
    
    # TODO: Integrate with conversation manager
    # conversation_manager = get_conversation_manager()
    # summary_text = await conversation_manager.generate_user_summary(request.user_id)
    
    async with db_pool.acquire() as conn:
        # Check for existing summary
        existing = await conn.fetchrow(
            """
            SELECT * FROM user_profile_summaries 
            WHERE user_id = $1 AND summary_topic = $2
            """,
            request.user_id,
            request.summary_topic
        )
        
        if existing and not request.force_regenerate:
            return ProfileSummary(**dict(existing))
        
        # Generate new summary (mock for now)
        summary_text = f"Generated profile summary for user {request.user_id} on topic {request.summary_topic}"
        
        if existing:
            # Update existing
            summary = await conn.fetchrow(
                """
                UPDATE user_profile_summaries 
                SET summary_text = $1, last_updated = NOW()
                WHERE user_id = $2 AND summary_topic = $3
                RETURNING *
                """,
                summary_text,
                request.user_id,
                request.summary_topic
            )
        else:
            # Create new
            summary = await conn.fetchrow(
                """
                INSERT INTO user_profile_summaries 
                (user_id, summary_text, summary_topic, last_updated, created_at)
                VALUES ($1, $2, $3, NOW(), NOW())
                RETURNING *
                """,
                request.user_id,
                summary_text,
                request.summary_topic
            )
        
        return ProfileSummary(**dict(summary))


@router.get("/summaries/{user_id}", response_model=List[ProfileSummary])
async def get_profile_summaries(
    user_id: int,
    db_pool: Pool = Depends(get_db_pool)
) -> List[ProfileSummary]:
    """Get all profile summaries for a user."""
    
    async with db_pool.acquire() as conn:
        summaries = await conn.fetch(
            """
            SELECT * FROM user_profile_summaries 
            WHERE user_id = $1
            ORDER BY last_updated DESC
            """,
            user_id
        )
        
        return [ProfileSummary(**dict(summary)) for summary in summaries]


@router.get("/context/{user_id}", response_model=MemoryContext)
async def get_memory_context(
    user_id: int,
    query: Optional[str] = None,
    db_pool: Pool = Depends(get_db_pool)
) -> MemoryContext:
    """Get complete memory context for a user."""
    
    # TODO: Integrate with RAG service
    # rag_service = get_rag_service()
    # context = await rag_service.retrieve_context(
    #     user_id=user_id
    #     query=query or ""
    # )
    
    async with db_pool.acquire() as conn:
        # Get recent messages
        messages = await conn.fetch(
            """
            SELECT * FROM conversation_messages 
            WHERE user_id = $1
            ORDER BY created_at DESC
            LIMIT 10
            """,
            user_id
        )
        
        # Get profile summaries
        summaries = await conn.fetch(
            """
            SELECT * FROM user_profile_summaries 
            WHERE user_id = $1
            ORDER BY last_updated DESC
            LIMIT 3
            """,
            user_id
        )
        
        # Mock relevant facts for now
        relevant_facts = []
        
        from datetime import datetime
        
        return MemoryContext(
            user_id=user_id,
            relevant_facts=relevant_facts,
            profile_summaries=[ProfileSummary(**dict(s)) for s in summaries],
            recent_messages=[dict(m) for m in messages],
            context_timestamp=datetime.utcnow()
        )


@router.get("/stats/{user_id}", response_model=MemoryStats)
async def get_memory_stats(
    user_id: int,
    db_pool: Pool = Depends(get_db_pool)
) -> MemoryStats:
    """Get memory statistics for a user."""
    
    async with db_pool.acquire() as conn:
        # Get fact counts
        total_facts = await conn.fetchval(
            "SELECT COUNT(*) FROM user_facts WHERE user_id = $1",
            user_id
        )
        
        # Get facts by category (if category column exists)
        # For now, mock categories
        fact_categories = {
            "personal": 10,
            "preferences": 5,
            "memories": 8
        }
        
        # Get summary count
        summaries_count = await conn.fetchval(
            "SELECT COUNT(*) FROM user_profile_summaries WHERE user_id = $1",
            user_id
        )
        
        # Get last fact date
        last_fact_date = await conn.fetchval(
            "SELECT MAX(created_at) FROM user_facts WHERE user_id = $1",
            user_id
        )
        
        # Calculate memory density
        message_count = await conn.fetchval(
            "SELECT COUNT(*) FROM conversation_messages WHERE user_id = $1",
            user_id
        )
        memory_density = (total_facts or 0) / max(message_count or 1, 1)
        
        return MemoryStats(
            user_id=user_id,
            total_facts=total_facts or 0,
            fact_categories=fact_categories,
            profile_summaries_count=summaries_count or 0,
            memory_density=memory_density,
            last_fact_date=last_fact_date,
            storage_size_bytes=None  # Would calculate actual storage
        )