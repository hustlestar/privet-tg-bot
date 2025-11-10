"""Grammar rules endpoints for language learning."""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel

from privet_api.api.deps import get_db_pool
from asyncpg import Pool
from privet_api.repositories.grammar_repository import GrammarRepository
from privet_api.models.schemas.base import ResponseSchema

router = APIRouter()


class GrammarRuleCreate(BaseModel):
    """Schema for creating a grammar rule."""
    rule_code: str
    language: str
    category: str
    difficulty_level: str
    title_en: str
    description_en: str
    title_es: Optional[str] = None
    title_ru: Optional[str] = None
    description_es: Optional[str] = None
    description_ru: Optional[str] = None
    examples: Optional[List[dict]] = None
    tags: Optional[List[str]] = None
    related_rules: Optional[List[str]] = None
    order_index: int = 0


class GrammarRuleResponse(BaseModel):
    """Schema for grammar rule response."""
    id: int
    rule_code: str
    language: str
    category: str
    difficulty_level: str
    title_en: str
    title_es: Optional[str]
    title_ru: Optional[str]
    description_en: str
    description_es: Optional[str]
    description_ru: Optional[str]
    examples: Optional[List[dict]]
    tags: Optional[List[str]]
    related_rules: Optional[List[str]]
    order_index: int
    is_active: bool


@router.post("/rules", response_model=ResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_grammar_rule(
    rule_data: GrammarRuleCreate,
    db_pool: Pool = Depends(get_db_pool),
):
    """Create a new grammar rule."""
    grammar_repo = GrammarRepository(db_pool)

    try:
        rule = await grammar_repo.create_rule(
            rule_code=rule_data.rule_code,
            language=rule_data.language,
            category=rule_data.category,
            difficulty_level=rule_data.difficulty_level,
            title_en=rule_data.title_en,
            description_en=rule_data.description_en,
            title_es=rule_data.title_es,
            title_ru=rule_data.title_ru,
            description_es=rule_data.description_es,
            description_ru=rule_data.description_ru,
            examples=rule_data.examples,
            tags=rule_data.tags,
            related_rules=rule_data.related_rules,
            order_index=rule_data.order_index,
        )

        if not rule:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Grammar rule with code '{rule_data.rule_code}' already exists"
            )

        return ResponseSchema(
            success=True,
            data=dict(rule),
            message="Grammar rule created successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating grammar rule: {str(e)}"
        )


@router.get("/rules/{rule_code}", response_model=ResponseSchema)
async def get_grammar_rule(
    rule_code: str,
    db_pool: Pool = Depends(get_db_pool),
):
    """Get a specific grammar rule by code."""
    grammar_repo = GrammarRepository(db_pool)

    try:
        rule = await grammar_repo.get_rule_by_code(rule_code)

        if not rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Grammar rule '{rule_code}' not found"
            )

        return ResponseSchema(
            success=True,
            data=dict(rule),
            message="Grammar rule retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching grammar rule: {str(e)}"
        )


@router.get("/rules", response_model=ResponseSchema)
async def get_grammar_rules(
    language: str = Query(..., description="Language code (es, en, ru)"),
    category: Optional[str] = Query(None, description="Filter by category"),
    difficulty_level: Optional[str] = Query(None, description="Filter by difficulty (A1-C2)"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(50, ge=1, le=100, description="Pagination limit"),
    db_pool: Pool = Depends(get_db_pool),
):
    """Get grammar rules for a language with pagination and filtering."""
    grammar_repo = GrammarRepository(db_pool)

    try:
        rules = await grammar_repo.get_rules_by_language(
            language=language,
            category=category,
            difficulty_level=difficulty_level,
            offset=offset,
            limit=limit,
        )

        total = await grammar_repo.count_rules(
            language=language,
            category=category,
            difficulty_level=difficulty_level,
        )

        return ResponseSchema(
            success=True,
            data={
                "items": [dict(rule) for rule in rules],
                "total": total,
                "offset": offset,
                "limit": limit,
            },
            message=f"Retrieved {len(rules)} grammar rules"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching grammar rules: {str(e)}"
        )


@router.get("/rules/search", response_model=ResponseSchema)
async def search_grammar_rules(
    language: str = Query(..., description="Language code"),
    q: str = Query(..., description="Search query"),
    limit: int = Query(20, ge=1, le=100),
    db_pool: Pool = Depends(get_db_pool),
):
    """Search grammar rules by title or tags."""
    grammar_repo = GrammarRepository(db_pool)

    try:
        rules = await grammar_repo.search_rules(
            language=language,
            search_query=q,
            limit=limit,
        )

        return ResponseSchema(
            success=True,
            data={"items": [dict(rule) for rule in rules]},
            message=f"Found {len(rules)} matching rules"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching grammar rules: {str(e)}"
        )


@router.get("/categories", response_model=ResponseSchema)
async def get_grammar_categories(
    language: str = Query(..., description="Language code"),
    db_pool: Pool = Depends(get_db_pool),
):
    """Get all available grammar categories for a language."""
    grammar_repo = GrammarRepository(db_pool)

    try:
        categories = await grammar_repo.get_categories(language)

        return ResponseSchema(
            success=True,
            data={"categories": categories},
            message=f"Retrieved {len(categories)} categories"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching categories: {str(e)}"
        )
