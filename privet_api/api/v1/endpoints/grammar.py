"""Grammar rules endpoints for language learning."""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel

from privet_api.api.deps import get_db_pool, get_ai_provider
from asyncpg import Pool
from privet_api.repositories.grammar_repository import GrammarRepository
from privet_api.services.grammar import GrammarRuleGenerator
from privet_api.services.ai import BaseAIProvider
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


# AI-Powered Grammar Generation Endpoints

class GenerateRuleRequest(BaseModel):
    """Request to generate a single grammar rule."""
    language: str
    category: str
    subcategory: str
    difficulty_level: str
    native_language: str = "en"


class GenerateCategoryRequest(BaseModel):
    """Request to generate rules for an entire category."""
    language: str
    category: str
    difficulty_levels: Optional[List[str]] = None
    native_language: str = "en"


class GenerateLibraryRequest(BaseModel):
    """Request to generate a complete grammar library."""
    language: str
    native_language: str = "en"
    categories: Optional[List[str]] = None
    difficulty_levels: Optional[List[str]] = None


@router.post("/generate/rule", response_model=ResponseSchema)
async def generate_grammar_rule(
    request: GenerateRuleRequest,
    db_pool: Pool = Depends(get_db_pool),
    ai_provider: BaseAIProvider = Depends(get_ai_provider),
):
    """Generate a single grammar rule using AI.

    This endpoint uses AI to create a comprehensive grammar rule with:
    - Multi-language titles and descriptions
    - 5-8 practical examples with translations
    - Tags for searchability
    - Related rule suggestions
    - Appropriate for specified CEFR level

    Example categories and subcategories:
    - verbs: present_tense, past_tense, future_tense, conditional, subjunctive
    - nouns: gender, number, articles, diminutives
    - pronouns: personal, possessive, demonstrative, relative
    - adjectives: agreement, position, comparatives, superlatives
    """
    grammar_repo = GrammarRepository(db_pool)
    generator = GrammarRuleGenerator(ai_provider, grammar_repo)

    try:
        rule = await generator.generate_grammar_rule(
            language=request.language,
            category=request.category,
            subcategory=request.subcategory,
            difficulty_level=request.difficulty_level,
            native_language=request.native_language
        )

        if not rule:
            return ResponseSchema(
                success=False,
                data=None,
                message="Failed to generate grammar rule or rule already exists"
            )

        return ResponseSchema(
            success=True,
            data=rule,
            message=f"Grammar rule '{rule['rule_code']}' generated successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating grammar rule: {str(e)}"
        )


@router.post("/generate/category", response_model=ResponseSchema)
async def generate_category_rules(
    request: GenerateCategoryRequest,
    db_pool: Pool = Depends(get_db_pool),
    ai_provider: BaseAIProvider = Depends(get_ai_provider),
):
    """Generate all grammar rules for a specific category.

    This will create rules for all subcategories within the specified category,
    across the specified difficulty levels.

    Available categories:
    - verbs (8 subcategories)
    - nouns (5 subcategories)
    - pronouns (6 subcategories)
    - adjectives (4 subcategories)
    - prepositions (4 subcategories)
    - adverbs (4 subcategories)
    - sentence_structure (5 subcategories)

    This can take several minutes to complete depending on the number of rules.
    """
    grammar_repo = GrammarRepository(db_pool)
    generator = GrammarRuleGenerator(ai_provider, grammar_repo)

    try:
        stats = await generator.generate_category_rules(
            language=request.language,
            category=request.category,
            difficulty_levels=request.difficulty_levels,
            native_language=request.native_language
        )

        return ResponseSchema(
            success=True,
            data=stats,
            message=f"Generated {stats['total_created']} rules for category '{request.category}'"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating category rules: {str(e)}"
        )


@router.post("/generate/library", response_model=ResponseSchema)
async def generate_grammar_library(
    request: GenerateLibraryRequest,
    db_pool: Pool = Depends(get_db_pool),
    ai_provider: BaseAIProvider = Depends(get_ai_provider),
):
    """Generate a complete grammar library for a language.

    ⚠️ WARNING: This is a long-running operation that may take 30+ minutes
    and consume significant AI API credits.

    This will generate hundreds of grammar rules covering:
    - All 7 categories
    - All subcategories within each
    - All 6 CEFR levels (A1, A2, B1, B2, C1, C2)

    Total rules generated: ~200+ rules per language

    Use `/generate/category` for more targeted generation.

    Recommended approach:
    1. Start with A1-A2 levels only
    2. Focus on high-priority categories (verbs, nouns)
    3. Generate gradually as needed
    """
    grammar_repo = GrammarRepository(db_pool)
    generator = GrammarRuleGenerator(ai_provider, grammar_repo)

    try:
        stats = await generator.generate_complete_grammar_library(
            language=request.language,
            native_language=request.native_language,
            categories=request.categories,
            difficulty_levels=request.difficulty_levels
        )

        return ResponseSchema(
            success=True,
            data=stats,
            message=f"Grammar library generated: {stats['total_created']} rules created"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating grammar library: {str(e)}"
        )


@router.get("/recommend/{user_id}", response_model=ResponseSchema)
async def get_recommended_rules(
    user_id: int,
    language: str = Query(..., description="Target language"),
    limit: int = Query(10, ge=1, le=50, description="Number of recommendations"),
    db_pool: Pool = Depends(get_db_pool),
    ai_provider: BaseAIProvider = Depends(get_ai_provider),
):
    """Get personalized grammar rule recommendations for a user.

    Returns grammar rules appropriate for the user's current level,
    prioritized by:
    1. User's current CEFR level
    2. Category importance (verbs > nouns > pronouns > etc.)
    3. Learning progress

    The system analyzes user progress to determine their level and
    suggests rules that are:
    - Appropriate for their current level
    - Slightly challenging (includes some next-level rules)
    - Prioritized by practical importance
    """
    grammar_repo = GrammarRepository(db_pool)
    generator = GrammarRuleGenerator(ai_provider, grammar_repo)

    try:
        recommended_rules = await generator.get_recommended_rules(
            user_id=user_id,
            language=language,
            limit=limit
        )

        return ResponseSchema(
            success=True,
            data={"recommendations": recommended_rules},
            message=f"Retrieved {len(recommended_rules)} recommended grammar rules"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting recommendations: {str(e)}"
        )


@router.get("/metadata", response_model=ResponseSchema)
async def get_grammar_metadata():
    """Get grammar generation metadata.

    Returns information about:
    - CEFR levels and their characteristics
    - Available categories and subcategories
    - Category priorities for learning
    - Estimated rule counts
    """
    from privet_api.services.grammar import GrammarRuleGenerator

    return ResponseSchema(
        success=True,
        data={
            "cefr_levels": GrammarRuleGenerator.CEFR_LEVELS,
            "categories": GrammarRuleGenerator.GRAMMAR_CATEGORIES,
            "total_possible_rules": sum(
                len(cat["subcategories"]) * 6  # 6 CEFR levels
                for cat in GrammarRuleGenerator.GRAMMAR_CATEGORIES.values()
            )
        },
        message="Grammar generation metadata retrieved successfully"
    )
