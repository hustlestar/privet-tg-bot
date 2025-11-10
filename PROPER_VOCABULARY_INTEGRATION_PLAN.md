# Proper Vocabulary Integration Plan: Microservices Architecture

## What Went Wrong

❌ **Bad Approach (What I Did)**:
- Created wrapper services in `privet_api/services/word_learning/`
- These wrappers imported learn-words DAOs directly
- Created duplicate API endpoints in `privet_api/api/v1/endpoints/vocabulary.py`
- This created tight coupling and violated service boundaries

## Correct Approach: learn-words as a Standalone Microservice

✅ **Proper Architecture**:
```
┌──────────────────────────┐
│   learn-words Service    │
│   (Port 8001)            │
│                          │
│  ┌────────────────────┐  │
│  │  FastAPI App       │  │
│  │  /api/vocabulary/* │  │
│  └─────────┬──────────┘  │
│            ↓             │
│  ┌────────────────────┐  │
│  │  DAOs + Training   │  │
│  │  Logic             │  │
│  └─────────┬──────────┘  │
│            ↓             │
│  ┌────────────────────┐  │
│  │  PostgreSQL DB     │  │
│  └────────────────────┘  │
└──────────────────────────┘
            ↑
            │ HTTP REST calls
            │
┌───────────┴──────────────┐
│  privet_api Service      │
│  (Port 8000)             │
│                          │
│  ┌────────────────────┐  │
│  │  HTTP Client       │  │
│  │  to learn-words    │  │
│  └────────────────────┘  │
│            ↑             │
│            │             │
│  ┌─────────┴──────────┐  │
│  │  React UI          │  │
│  └────────────────────┘  │
└──────────────────────────┘
```

## Implementation Plan

### Phase 1: Create FastAPI app inside learn-words

**Location**: `learn-words/src/api/`

#### 1.1 Create API structure
```
learn-words/
└── src/
    └── api/
        ├── __init__.py
        ├── main.py              # FastAPI app
        ├── deps.py              # Dependencies (DB pool)
        ├── router.py            # Main router
        ├── schemas/             # Pydantic schemas
        │   ├── __init__.py
        │   ├── translation.py
        │   ├── vocabulary.py
        │   ├── training.py
        │   └── user.py
        └── endpoints/           # API endpoints
            ├── __init__.py
            ├── translation.py   # Translation endpoints
            ├── vocabulary.py    # Vocabulary management
            ├── training.py      # Training endpoints
            └── users.py         # User management
```

#### 1.2 Create main.py for API server
```python
# learn-words/src/api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.router import api_router
from src.database import init_pool, close_pool

app = FastAPI(
    title="Learn Words Vocabulary API",
    description="Vocabulary learning and training API",
    version="1.0.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

@app.on_event("startup")
async def startup():
    await init_pool()

@app.on_event("shutdown")
async def shutdown():
    await close_pool()
```

#### 1.3 Create endpoints that use existing DAOs

**Example**: `learn-words/src/api/endpoints/translation.py`
```python
from fastapi import APIRouter, Depends
from src.database import get_pool
from src.translation.translator import translator
from src.api.schemas.translation import (
    TranslationRequest,
    TranslationResponse
)

router = APIRouter()

@router.post("/translate", response_model=TranslationResponse)
async def translate_word(
    request: TranslationRequest,
    pool = Depends(get_pool)
):
    """Translate a word using existing translation service."""
    translation_data = await translator.translate_word(
        word=request.word,
        from_language=request.from_language,
        to_language=request.to_language,
        native_language=request.native_language
    )

    return TranslationResponse.from_translation_data(translation_data)
```

**Key points**:
- Uses existing `translator` from `src/translation/translator.py`
- Uses existing DAOs from `src/dao/`
- Uses existing training logic from `src/training.py`
- NO duplication, just exposing existing logic via HTTP

#### 1.4 Run API server separately

```bash
# Terminal 1: Run Telegram bot
cd learn-words
python main.py

# Terminal 2: Run API server
cd learn-words
uvicorn src.api.main:app --port 8001 --reload
```

### Phase 2: privet_api consumes learn-words API

#### 2.1 Create HTTP client in privet_api

**Location**: `privet_api/clients/vocabulary_client.py`

```python
import httpx
from typing import Optional, List, Dict, Any

class VocabularyClient:
    """HTTP client for learn-words vocabulary API."""

    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url)

    async def translate_word(
        self,
        word: str,
        from_lang: str,
        to_lang: str
    ) -> Dict[str, Any]:
        """Call learn-words translation API."""
        response = await self.client.post(
            "/api/v1/translate",
            json={
                "word": word,
                "from_language": from_lang,
                "to_language": to_lang
            }
        )
        response.raise_for_status()
        return response.json()

    async def get_user_vocabulary(
        self,
        user_id: int,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get user's vocabulary from learn-words API."""
        response = await self.client.get(
            f"/api/v1/vocabulary/{user_id}",
            params={"limit": limit}
        )
        response.raise_for_status()
        return response.json()

    # ... more methods for each learn-words endpoint
```

#### 2.2 Optional: Expose in privet_api if needed

If privet_api needs to provide vocabulary endpoints to its own clients:

```python
# privet_api/api/v1/endpoints/vocabulary.py (OPTIONAL)
from fastapi import APIRouter, Depends
from privet_api.clients.vocabulary_client import VocabularyClient

router = APIRouter()

@router.post("/translate")
async def translate_word(
    request: TranslationRequest,
    vocab_client: VocabularyClient = Depends(get_vocabulary_client)
):
    """Proxy to learn-words translation API."""
    return await vocab_client.translate_word(
        word=request.word,
        from_lang=request.from_language,
        to_lang=request.to_language
    )
```

**OR** just use the client directly in your frontend without privet_api as proxy.

### Phase 3: Frontend integration

#### 3.1 Generate TypeScript client from learn-words API

```bash
# Start learn-words API
cd learn-words
uvicorn src.api.main:app --port 8001

# Generate client
cd privet-ui
curl http://localhost:8001/openapi.json > openapi-vocabulary.json
npx @openapitools/openapi-generator-cli generate \
  -i openapi-vocabulary.json \
  -g typescript-axios \
  -o ./generated-client/vocabulary
```

#### 3.2 Create React hooks

```typescript
// privet-ui/apps/user-app/src/hooks/useVocabulary.ts
import { VocabularyApi, Configuration } from '@/generated-client/vocabulary';

const vocabularyApi = new VocabularyApi(
  new Configuration({ basePath: 'http://localhost:8001' })
);

export function useTranslation() {
  return useMutation({
    mutationFn: (params: { word: string; from: string; to: string }) =>
      vocabularyApi.translateWord(params),
  });
}

export function useVocabulary(userId: number) {
  return useQuery({
    queryKey: ['vocabulary', userId],
    queryFn: () => vocabularyApi.getUserVocabulary(userId),
  });
}
```

## Benefits of This Architecture

✅ **Proper Separation**: learn-words is a standalone microservice
✅ **Service Boundaries**: Clear HTTP API contract
✅ **No Coupling**: privet_api doesn't import learn-words internals
✅ **Independent Deployment**: Can deploy learn-words separately
✅ **Reusability**: Any client can consume learn-words API
✅ **Scalability**: Can scale learn-words independently
✅ **Testing**: Can test each service in isolation

## Implementation Steps

1. **Create learn-words API structure** (`src/api/`)
2. **Create Pydantic schemas** for requests/responses
3. **Create endpoints** that use existing DAOs and services
4. **Add CORS** for frontend access
5. **Run both services** (bot on 8000, API on 8001)
6. **Generate TypeScript client** from learn-words OpenAPI spec
7. **Create React hooks** using generated client
8. **Build UI components** for vocabulary features

## Timeline

- Phase 1 (learn-words API): **4-6 hours**
- Phase 2 (Client/integration): **2-3 hours**
- Phase 3 (Frontend): **4-6 hours**

**Total**: ~10-15 hours for complete implementation

## Notes

- The Telegram bot and API server can run simultaneously
- They share the same database pool
- Both use the same DAOs and business logic
- No code duplication, just different interfaces (Telegram vs HTTP)
