# 🎯 Learn-Words Integration Plan: Telegram Bot → API → UI

## Executive Summary

**Goal**: Expose the learn-words Telegram bot functionality via FastAPI endpoints and integrate with React UI using our automated client generation workflow.

**What We Have**:
- ✅ **Telegram Bot** (`learn-words/`): Fully functional with 97 files, 21K+ lines
- ✅ **Frontend Components**: Interactive word, vocabulary list, review system (already built)
- ✅ **Client Generation**: Automated OpenAPI → TypeScript workflow
- ✅ **Database Schema**: PostgreSQL tables for words, users, training

**What We'll Build**:
- 🔨 API wrapper endpoints in FastAPI
- 🔨 Shared service layer for both Telegram bot and API
- 🔨 TypeScript client auto-generation
- 🔨 Frontend integration with existing components

---

## 📊 Learn-Words Architecture Analysis

### Database Schema (Already Exists)

```sql
-- Core Tables
words
├─ id, word, from_language, to_language
├─ short_translation (quick lookup)
├─ medium_data (JSON: word, meaning, example)
├─ long_data (JSON: translations[], meanings[], examples[], context)
├─ synonyms_native, synonyms_learning
└─ word_type, created_at

users
├─ user_id, learning_language, interface_language
├─ response_mode (short/medium/long)
├─ explanation_language (native/learning/mixed)
├─ plan (free/plus/pro)
└─ notification_times, timezone, is_blocked

user_word_stats
├─ user_id, word_id
├─ total_attempts, correct_answers
├─ is_marked_known, is_hidden
├─ repetition_level, next_review_at
└─ last_seen, added_at

training_attempts
├─ id, user_id, word_id, training_type
├─ is_correct, answered_text, correct_answer
└─ created_at
```

### Key Features to Expose

1. **Translation System** (3 detail levels)
   - Short: Just translation
   - Medium: Translation + meaning + example
   - Long: Multiple translations, meanings, examples, context

2. **Vocabulary Management**
   - Add words (single or from sentence parsing)
   - Mark as known
   - Hide/unhide words
   - Get user vocabulary list

3. **Training System** (Smart priority algorithm)
   - Direct Translation (learning → native)
   - Multiple Choice (4 options)
   - Reverse Translation (native → learning)
   - Prioritizes low success rate + few attempts + time since last seen

4. **Spaced Repetition**
   - Repetition levels (0-5)
   - Next review date calculation
   - Due words tracking

5. **Statistics & Progress**
   - Total words, success rate
   - Training attempts
   - Progress tracking

---

## 🏗️ Integration Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    TELEGRAM BOT                         │
│              (Existing - Keep Running)                  │
└──────────────────┬──────────────────────────────────────┘
                   │
                   │ Uses shared services
                   ↓
┌─────────────────────────────────────────────────────────┐
│             SHARED SERVICE LAYER (NEW)                  │
│  /privet_api/services/word_learning/                    │
│  ├── word_service.py        - Word CRUD                │
│  ├── translation_service.py - Translation logic        │
│  ├── training_service.py    - Training exercises       │
│  ├── user_service.py        - User management          │
│  └── stats_service.py       - Progress tracking        │
└──────────────────┬──────────────────────────────────────┘
                   │
                   │ Used by both
            ┌──────┴──────┐
            │             │
            ↓             ↓
   ┌────────────┐  ┌─────────────────┐
   │  Telegram  │  │  FastAPI        │
   │  Handlers  │  │  Endpoints      │
   └────────────┘  └────────┬────────┘
                            │
                     OpenAPI Spec
                            │
                            ↓
                   ┌────────────────┐
                   │ generate_api_  │
                   │ client.py      │
                   └────────┬───────┘
                            │
                            ↓
                   ┌────────────────┐
                   │  TypeScript    │
                   │  Client        │
                   │ (generated)    │
                   └────────┬───────┘
                            │
                            ↓
                   ┌────────────────┐
                   │  React UI      │
                   │  (existing     │
                   │   components)  │
                   └────────────────┘
```

---

## 📋 Implementation Plan

### Phase 1: Extract Core Logic (Day 1)

**Create shared services** from Telegram bot DAOs:

```
/privet_api/services/word_learning/
├── __init__.py
├── word_service.py           ← Extract from WordDao
├── translation_service.py    ← Extract from translator.py
├── training_service.py       ← Extract from TrainingDao
├── user_service.py           ← Extract from UserDao
└── stats_service.py          ← New - aggregate stats
```

**Tasks**:
- [ ] Create `word_service.py` - Wrap WordDao methods
- [ ] Create `translation_service.py` - Use existing translator logic
- [ ] Create `training_service.py` - Wrap TrainingDao + priority algorithm
- [ ] Create `user_service.py` - Wrap UserDao
- [ ] Create `stats_service.py` - Aggregate user statistics

### Phase 2: Create API Endpoints (Day 1-2)

**Create REST API** in `/privet_api/api/v1/endpoints/vocabulary.py`:

```python
# Words Management
POST   /api/v1/vocabulary/translate          # Translate word (3 levels)
GET    /api/v1/vocabulary/words/{user_id}    # Get user vocabulary
POST   /api/v1/vocabulary/words              # Add word
PUT    /api/v1/vocabulary/words/{word_id}    # Update word (mark known, hide)
DELETE /api/v1/vocabulary/words/{word_id}    # Delete word

# Training
GET    /api/v1/vocabulary/training/{user_id}/next   # Get next word for training
POST   /api/v1/vocabulary/training/attempt          # Record training attempt
GET    /api/v1/vocabulary/training/{user_id}/due    # Get due words (spaced repetition)

# Statistics
GET    /api/v1/vocabulary/stats/{user_id}           # User progress stats
GET    /api/v1/vocabulary/stats/{user_id}/word/{word_id}  # Word-specific stats

# Sentence Parsing (Bonus)
POST   /api/v1/vocabulary/parse-sentence            # Extract words from sentence
```

**Pydantic Schemas** in `/privet_api/models/schemas/vocabulary.py`:

```python
class TranslateRequest:
    word: str
    from_language: str
    to_language: str
    detail_level: Literal["short", "medium", "long"]
    native_language: Optional[str]

class WordResponse:
    id: int
    word: str
    from_language: str
    to_language: str
    short_translation: str
    medium_data: Optional[dict]  # {word, meaning, example}
    long_data: Optional[dict]    # {translations[], meanings[], examples[], context}
    synonyms_native: List[str]
    synonyms_learning: List[str]
    word_type: Optional[str]

class UserWordStatsResponse:
    word_id: int
    word: str
    translation: str
    total_attempts: int
    correct_answers: int
    success_rate: float
    is_marked_known: bool
    is_hidden: bool
    last_seen: Optional[datetime]
    next_review_at: Optional[datetime]
    repetition_level: int

class TrainingQuestionResponse:
    word_id: int
    word: str
    training_type: str  # "A", "B", "C"
    options: Optional[List[str]]  # For multiple choice
    hint: Optional[str]

class TrainingAttemptRequest:
    user_id: int
    word_id: int
    training_type: str
    user_answer: str
    is_correct: bool

class UserStatsResponse:
    total_words: int
    known_words: int
    learning_words: int
    total_attempts: int
    correct_attempts: int
    overall_success_rate: float
    words_due_today: int
    streak_days: int
```

### Phase 3: Update Telegram Bot to Use Shared Services (Day 2)

**Refactor bot handlers** to use new service layer:

```python
# Before (Direct DAO usage)
from src.dao.word_dao import WordDao
word_dao = WordDao(pool)
word = await word_dao.get_word(word, from_lang, to_lang)

# After (Shared service)
from privet_api.services.word_learning import WordService
word_service = WordService(pool)
word = await word_service.get_word(word, from_lang, to_lang)
```

**Tasks**:
- [ ] Update `vocabulary_handlers.py` → use `WordService`
- [ ] Update `training_handlers.py` → use `TrainingService`
- [ ] Update `command_handlers.py` → use `UserService`
- [ ] Test Telegram bot still works

### Phase 4: Generate TypeScript Client (Day 2)

**Run client generator**:

```bash
# Start backend
python -m privet_api.main

# Generate client (in another terminal)
python generate_api_client.py
```

**Verify output**:
```
generated-client/
├── api/
│   └── vocabulary-api.ts    ← New API client
├── models/
│   ├── translate-request.ts
│   ├── word-response.ts
│   ├── user-word-stats-response.ts
│   ├── training-question-response.ts
│   └── user-stats-response.ts
```

### Phase 5: Integrate Frontend (Day 2-3)

**Update React hooks** to use generated client:

```typescript
// apps/user-app/src/hooks/useVocabulary.ts
import { VocabularyApi, Configuration } from '@privet/api-client';

const vocabularyApi = new VocabularyApi(
  new Configuration({ basePath: process.env.NEXT_PUBLIC_API_URL })
);

// Add word
export function useAddWord() {
  return useMutation({
    mutationFn: async ({ userId, word, fromLanguage, toLanguage }) => {
      const response = await vocabularyApi.addWord({
        addWordRequest: { userId, word, fromLanguage, toLanguage }
      });
      return response.data;
    }
  });
}

// Get vocabulary list
export function useUserVocabulary(userId: number) {
  return useQuery({
    queryKey: ['vocabulary', userId],
    queryFn: async () => {
      const response = await vocabularyApi.getUserVocabulary({ userId });
      return response.data;
    }
  });
}

// Get next training word
export function useNextTrainingWord(userId: number) {
  return useQuery({
    queryKey: ['training', 'next', userId],
    queryFn: async () => {
      const response = await vocabularyApi.getNextTrainingWord({ userId });
      return response.data;
    },
    enabled: !!userId
  });
}

// Record training attempt
export function useRecordAttempt() {
  return useMutation({
    mutationFn: async (attempt) => {
      const response = await vocabularyApi.recordTrainingAttempt({
        trainingAttemptRequest: attempt
      });
      return response.data;
    }
  });
}

// Get user stats
export function useUserStats(userId: number) {
  return useQuery({
    queryKey: ['vocabulary', 'stats', userId],
    queryFn: async () => {
      const response = await vocabularyApi.getUserStats({ userId });
      return response.data;
    }
  });
}
```

**Wire up components**:

```typescript
// apps/user-app/src/app/vocabulary/page.tsx
export default function VocabularyPage() {
  const userId = 1; // From auth context

  const { data: vocabulary } = useUserVocabulary(userId);
  const { data: stats } = useUserStats(userId);
  const addWord = useAddWord();

  return (
    <div>
      <VocabularyStats stats={stats} />
      <VocabularyList
        words={vocabulary}
        onAdd={(word) => addWord.mutate(word)}
      />
    </div>
  );
}

// apps/user-app/src/app/training/page.tsx
export default function TrainingPage() {
  const userId = 1;

  const { data: question } = useNextTrainingWord(userId);
  const recordAttempt = useRecordAttempt();

  const handleAnswer = async (answer: string) => {
    await recordAttempt.mutateAsync({
      userId,
      wordId: question.word_id,
      trainingType: question.training_type,
      userAnswer: answer,
      isCorrect: answer === question.correct_answer
    });

    // Refetch next question
    queryClient.invalidateQueries(['training', 'next', userId]);
  };

  return (
    <TrainingExercise
      question={question}
      onAnswer={handleAnswer}
    />
  );
}
```

### Phase 6: Testing & Validation (Day 3)

**Test scenarios**:
- [ ] Telegram bot adds word → appears in web UI
- [ ] Web UI adds word → appears in Telegram bot
- [ ] Training in Telegram → stats update in web UI
- [ ] Training in web UI → stats update in Telegram
- [ ] Mark as known in Telegram → reflected in web UI
- [ ] Hide word in web UI → not shown in Telegram training
- [ ] Spaced repetition: due words appear correctly in both
- [ ] Translation caching: same word doesn't hit AI twice
- [ ] Performance: Load 1000+ words, test speed

---

## 🔑 Key Implementation Details

### 1. Database Connection Sharing

**Both systems use same database**:

```python
# learn-words bot (existing)
from src.database import Database
db = Database(config.DATABASE_URL)
pool = await db.get_pool()

# FastAPI (privet_api)
from privet_api.core.database import DatabaseManager
db_manager = DatabaseManager(settings.database_url)
await db_manager.setup()
pool = db_manager.pool

# Both use asyncpg.Pool → same PostgreSQL instance
```

**No database migration needed** - tables already exist!

### 2. Translation Service Integration

**Reuse existing AI provider**:

```python
# learn-words/src/translation/translator.py
class Translator:
    async def translate(self, word, from_lang, to_lang, detail_level):
        # OpenAI API call
        # Caching logic
        # 3 detail levels

# Wrap in service
# privet_api/services/word_learning/translation_service.py
from learn_words.src.translation.translator import Translator

class TranslationService:
    def __init__(self, pool, ai_provider):
        self.translator = Translator(pool, ai_provider)

    async def translate_word(self, word, from_lang, to_lang, detail_level):
        return await self.translator.translate(word, from_lang, to_lang, detail_level)
```

### 3. Training Algorithm (Priority-Based)

**Already implemented in learn-words** `TrainingDao.get_word_for_training()`:

```sql
-- Smart priority calculation
priority_score =
    (1 - success_rate) * 100         -- Prioritize low success rate
    + (10 - total_attempts) * 10     -- Prioritize less practiced words
    + days_since_last_seen * 5       -- Time bonus
    - (is_marked_known ? 30 : 0)     -- Reduce priority for known words
```

**Just expose via API**:
```python
@router.get("/training/{user_id}/next")
async def get_next_training_word(user_id: int):
    training_service = TrainingService(pool)
    word, stats = await training_service.get_word_for_training(user_id)
    return TrainingQuestionResponse(...)
```

### 4. Spaced Repetition

**Already implemented** in `src/repetition.py`:

```python
def get_next_review_date(repetition_level: int, is_correct: bool) -> datetime:
    """Calculate next review date based on SM-2 algorithm variant."""
    if is_correct:
        repetition_level += 1
    else:
        repetition_level = max(0, repetition_level - 1)

    intervals = [0, 1, 3, 7, 14, 30]  # days
    days = intervals[min(repetition_level, len(intervals)-1)]
    return datetime.now() + timedelta(days=days)
```

**Expose via API**:
```python
@router.get("/training/{user_id}/due")
async def get_due_words(user_id: int):
    """Get words due for review based on spaced repetition."""
    training_service = TrainingService(pool)
    due_words = await training_service.get_due_words(user_id)
    return due_words
```

---

## 🎨 Frontend Components Mapping

**Already built** (just need to wire up):

| Component | Purpose | API Endpoint |
|-----------|---------|--------------|
| `InteractiveWord` | Hover/click word with translation | `POST /vocabulary/translate` |
| `VocabularyList` | User's word list | `GET /vocabulary/words/{user_id}` |
| `VocabularyReview` | Flashcard system | `GET /training/{user_id}/next` + `POST /training/attempt` |
| `VocabularyStats` | Progress dashboard | `GET /vocabulary/stats/{user_id}` |

**New components needed**:

```typescript
// apps/user-app/src/components/training/TrainingExercise.tsx
export function TrainingExercise({ question, onAnswer }) {
  // Render based on training_type
  if (question.training_type === 'A') {
    return <DirectTranslationExercise />;
  } else if (question.training_type === 'B') {
    return <MultipleChoiceExercise options={question.options} />;
  } else {
    return <ReverseTranslationExercise />;
  }
}

// apps/user-app/src/components/vocabulary/SentenceParser.tsx
export function SentenceParser({ onWordSelect }) {
  // Parse sentence and make words clickable
  // POST /vocabulary/parse-sentence
  // User selects words to add
}
```

---

## 📊 Success Metrics

After integration is complete:

1. **Dual Interface**:
   - Telegram bot works as before
   - Web UI has full vocabulary functionality

2. **Data Consistency**:
   - Same vocabulary appears in both interfaces
   - Training progress syncs in real-time
   - Statistics match across platforms

3. **Performance**:
   - Translation caching reduces API costs by 90%+
   - Web UI loads vocabulary in <500ms
   - Training exercises respond instantly

4. **User Experience**:
   - Seamless switch between Telegram and web
   - All features available in both interfaces
   - Progress tracking unified

---

## 🚀 Quick Start Commands

```bash
# Phase 1: Setup
cd /home/user/privet-tg-bot

# Phase 2: Create services (manual implementation)
mkdir -p privet_api/services/word_learning
# ... create service files

# Phase 3: Start backend
python -m privet_api.main

# Phase 4: Generate TypeScript client
python generate_api_client.py

# Phase 5: Install in frontend
cd privet-ui
npm install --legacy-peer-deps

# Phase 6: Start frontend
cd apps/user-app
npm run dev

# Phase 7: Test integration
# Open http://localhost:3000/vocabulary
```

---

## 📝 Next Steps

**Ready to start?** Let me know and I'll:

1. ✅ Create the shared service layer
2. ✅ Build the API endpoints
3. ✅ Generate the TypeScript client
4. ✅ Wire up the frontend components
5. ✅ Test the complete integration

**Estimated timeline**: 3-4 days for full integration

Would you like me to start with Phase 1 (extracting core logic into shared services)?
