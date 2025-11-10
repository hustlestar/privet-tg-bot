# Language Learning API Documentation

## Overview

Complete API for AI-driven language learning platform with:
- **Streaming Chat** with word-by-word metadata
- **Grammar Rules** database and browsing
- **Pronunciation Practice** with voice recognition
- **Progress Tracking** with XP, levels, streaks, and achievements
- **Pronunciation Caching** for cost optimization

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

All endpoints require:
- `X-API-Key` header for authentication
- `X-User-ID` header for user-specific operations (optional)

---

## Streaming Chat

### POST /streaming/chat

Stream chat responses word-by-word with optional vocabulary metadata.

**Server-Sent Events (SSE) endpoint** - keeps connection open and streams events.

#### Request Body

```json
{
  "user_id": 1,
  "message": "¿Cómo estás?",
  "target_language": "es",
  "native_language": "en",
  "include_word_metadata": true,
  "include_grammar_hints": false
}
```

#### SSE Events

**Event: connected**
```
event: connected
data: {"status": "connected"}
```

**Event: word** (if `include_word_metadata: true`)
```
event: word
data: {
  "word": "Hola",
  "translation": "Hello",
  "part_of_speech": "interjection",
  "difficulty": "A1"
}
```

**Event: chunk** (text content)
```
event: chunk
data: {"content": "¡Hola! Estoy bien, "}
```

**Event: complete**
```
event: complete
data: {
  "full_response": "¡Hola! Estoy bien, gracias.",
  "word_count": 5
}
```

**Event: error**
```
event: error
data: {"error": "Error message"}
```

#### Example Client Code (JavaScript)

```javascript
const eventSource = new EventSource('http://localhost:8000/api/v1/streaming/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'your-api-key'
  },
  body: JSON.stringify({
    user_id: 1,
    message: "¿Cómo estás?",
    target_language: "es",
    native_language: "en",
    include_word_metadata: true
  })
});

eventSource.addEventListener('word', (e) => {
  const data = JSON.parse(e.data);
  console.log('Word metadata:', data);
});

eventSource.addEventListener('chunk', (e) => {
  const data = JSON.parse(e.data);
  console.log('Text:', data.content);
});

eventSource.addEventListener('complete', (e) => {
  const data = JSON.parse(e.data);
  console.log('Complete response:', data.full_response);
  eventSource.close();
});
```

---

## Grammar Rules

### POST /grammar/rules

Create a new grammar rule.

#### Request Body

```json
{
  "rule_code": "es_present_regular_ar",
  "language": "es",
  "category": "verbs",
  "difficulty_level": "A1",
  "title_en": "Present Tense: Regular -AR Verbs",
  "title_es": "Presente: Verbos Regulares -AR",
  "title_ru": "Настоящее время: правильные глаголы на -AR",
  "description_en": "Regular -AR verbs in Spanish follow a predictable conjugation pattern...",
  "description_es": "Los verbos regulares -AR en español siguen un patrón predecible...",
  "description_ru": "Правильные испанские глаголы на -AR следуют предсказуемому образцу...",
  "examples": [
    {
      "spanish": "Yo hablo español",
      "english": "I speak Spanish",
      "russian": "Я говорю по-испански"
    },
    {
      "spanish": "Tú hablas inglés",
      "english": "You speak English",
      "russian": "Ты говоришь по-английски"
    }
  ],
  "tags": ["verbs", "present", "regular", "ar-verbs"],
  "related_rules": ["es_present_regular_er", "es_present_regular_ir"],
  "order_index": 1
}
```

#### Response

```json
{
  "success": true,
  "data": {
    "id": 1,
    "rule_code": "es_present_regular_ar",
    "language": "es",
    "category": "verbs",
    "difficulty_level": "A1",
    "title_en": "Present Tense: Regular -AR Verbs",
    ...
  },
  "message": "Grammar rule created successfully"
}
```

### GET /grammar/rules/{rule_code}

Get a specific grammar rule by code.

#### Response

```json
{
  "success": true,
  "data": {
    "id": 1,
    "rule_code": "es_present_regular_ar",
    "language": "es",
    ...
  },
  "message": "Grammar rule retrieved successfully"
}
```

### GET /grammar/rules

Get grammar rules with filtering and pagination.

#### Query Parameters

- `language` (required): Language code (es, en, ru)
- `category` (optional): Filter by category
- `difficulty_level` (optional): Filter by CEFR level (A1-C2)
- `offset` (optional): Pagination offset (default: 0)
- `limit` (optional): Items per page (default: 50, max: 100)

#### Example

```
GET /grammar/rules?language=es&category=verbs&difficulty_level=A1&limit=20
```

#### Response

```json
{
  "success": true,
  "data": {
    "items": [...],
    "total": 50,
    "offset": 0,
    "limit": 20
  },
  "message": "Retrieved 20 grammar rules"
}
```

### GET /grammar/rules/search

Search grammar rules by title or tags.

#### Query Parameters

- `language` (required): Language code
- `q` (required): Search query
- `limit` (optional): Max results (default: 20)

#### Example

```
GET /grammar/rules/search?language=es&q=presente&limit=10
```

### GET /grammar/categories

Get all available categories for a language.

#### Query Parameters

- `language` (required): Language code

#### Response

```json
{
  "success": true,
  "data": {
    "categories": ["verbs", "nouns", "adjectives", "articles", "pronouns"]
  },
  "message": "Retrieved 5 categories"
}
```

---

## Pronunciation & TTS

### POST /pronunciation/synthesize

Generate pronunciation audio with intelligent caching.

#### Request Body

```json
{
  "text": "Hola",
  "language_code": "es",
  "voice_id": null,
  "use_cache": true
}
```

#### Response

```json
{
  "text": "Hola",
  "language_code": "es",
  "audio_data": "base64_encoded_mp3_data...",
  "audio_format": "mp3",
  "from_cache": true,
  "cache_id": 123,
  "voice_id": "alloy",
  "provider": "openai"
}
```

### POST /pronunciation/synthesize/audio

Same as `/synthesize` but returns raw audio file directly.

#### Response Headers

- `Content-Type`: audio/mpeg
- `X-From-Cache`: true/false
- `X-Cache-ID`: Cache entry ID (if cached)

### POST /pronunciation/cache/bulk

Pre-cache pronunciation for multiple words.

#### Request Body

```json
{
  "words": ["hola", "gracias", "por favor", "adiós"],
  "language_code": "es",
  "voice_id": null
}
```

#### Query Parameters

- `language_code` (required): Language code
- `voice_id` (optional): Voice override

#### Response

```json
{
  "success": true,
  "data": {
    "total": 4,
    "cached": 3,
    "skipped": 1,
    "failed": 0
  },
  "message": "Bulk cache completed: 3 cached, 1 skipped, 0 failed"
}
```

### GET /pronunciation/cache/stats

Get cache statistics.

#### Query Parameters

- `language_code` (optional): Filter by language

#### Response

```json
{
  "success": true,
  "data": {
    "total_entries": 1250,
    "total_size_bytes": 12500000,
    "total_size_mb": 11.92,
    "total_cache_hits": 45000,
    "average_hits_per_entry": 36,
    "by_language": {
      "es": {"count": 800, "hits": 30000},
      "en": {"count": 350, "hits": 12000},
      "ru": {"count": 100, "hits": 3000}
    }
  },
  "message": "Cache statistics retrieved successfully"
}
```

### DELETE /pronunciation/cache/cleanup

Clean up old, rarely used cache entries.

#### Query Parameters

- `days` (optional): Delete entries older than this (default: 90)

#### Response

```json
{
  "success": true,
  "data": {
    "deleted_count": 25,
    "days_threshold": 90
  },
  "message": "Cleaned up 25 old cache entries"
}
```

---

## Voice Recognition & Assessment

### POST /pronunciation/assess

Assess pronunciation quality by comparing user's audio to expected text.

**Uses Whisper STT** to transcribe audio, then compares to expected text.

#### Form Data

- `audio_file`: Audio file (multipart/form-data)
  - Max size: 10MB
  - Formats: ogg, mp3, wav, webm, m4a
- `expected_text`: The text user should pronounce
- `language`: Language code (default: "en")

#### Response

```json
{
  "success": true,
  "accuracy_score": 95,
  "transcribed_text": "Hello how are you",
  "expected_text": "Hello, how are you?",
  "is_correct": true,
  "feedback": "Excellent pronunciation! Very close to perfect.",
  "issues": ["Minor differences detected, but overall very good"],
  "language": "en"
}
```

#### Accuracy Thresholds

- **90-100**: Excellent
- **80-89**: Good (acceptable)
- **60-79**: Fair (needs practice)
- **0-59**: Poor (needs significant practice)

### POST /pronunciation/assess/word

Simplified assessment for single word pronunciation.

#### Form Data

- `audio_file`: Audio file
- `word`: The word to assess
- `language`: Language code (default: "en")

#### Response

```json
{
  "success": true,
  "word": "Hola",
  "accuracy_score": 88,
  "transcribed_text": "Ola",
  "expected_text": "Hola",
  "is_correct": true,
  "feedback": "Good pronunciation! A few small improvements needed.",
  "issues": ["Said 'Ola' instead of 'Hola'"],
  "attempts_recommended": 0,
  "language": "es"
}
```

---

## Progress Tracking

### GET /progress/{user_id}

Get user's current progress.

#### Response

```json
{
  "success": true,
  "data": {
    "user_id": 1,
    "total_xp": 2500,
    "current_level": 5,
    "xp_to_next_level": 300,
    "current_streak": 7,
    "longest_streak": 12,
    "total_study_time_seconds": 14400,
    "total_sessions": 48,
    "last_activity_date": "2025-11-10T10:30:00Z",
    "created_at": "2025-11-01T08:00:00Z",
    "updated_at": "2025-11-10T10:30:00Z"
  },
  "message": "User progress retrieved successfully"
}
```

### GET /progress/{user_id}/stats

Get comprehensive user statistics including analytics.

#### Response

```json
{
  "success": true,
  "data": {
    "user_id": 1,
    "total_xp": 2500,
    "current_level": 5,
    "xp_to_next_level": 300,
    "current_streak": 7,
    "longest_streak": 12,
    "total_study_time_seconds": 14400,
    "total_sessions": 48,
    "last_activity_date": "2025-11-10T10:30:00Z",
    "avg_session_duration": 300,
    "created_at": "2025-11-01T08:00:00Z"
  },
  "message": "User statistics retrieved successfully"
}
```

### POST /progress/xp/add

Add XP to user and handle level-ups automatically.

#### Request Body

```json
{
  "user_id": 1,
  "xp_amount": 50,
  "activity_type": "conversation"
}
```

#### Response

```json
{
  "success": true,
  "data": {
    "user_id": 1,
    "total_xp": 2550,
    "current_level": 5,
    "xp_to_next_level": 250,
    ...
  },
  "message": "Added 50 XP. Current level: 5"
}
```

#### Level System

Uses power curve for level progression:
- Level 1 → 2: 100 XP
- Level 2 → 3: 200 XP
- Level 3 → 4: 300 XP
- Maximum level: 100

### POST /progress/session/record

Record a completed learning session.

#### Request Body

```json
{
  "user_id": 1,
  "session_type": "conversation",
  "duration_seconds": 300,
  "xp_earned": 50
}
```

#### Session Types

- `conversation`: Chat-based learning
- `grammar`: Grammar rule practice
- `pronunciation`: Pronunciation practice
- `review`: Spaced repetition review

#### Response

```json
{
  "success": true,
  "data": {
    "session": {
      "id": 49,
      "user_id": 1,
      "session_type": "conversation",
      "duration_seconds": 300,
      "xp_earned": 50,
      ...
    },
    "progress": {
      "total_xp": 2550,
      "current_level": 5,
      "current_streak": 8,
      ...
    }
  },
  "message": "Session recorded: 300s, 50 XP earned"
}
```

---

## Achievements

### GET /progress/achievements/available

Get all available achievements.

#### Response

```json
{
  "success": true,
  "data": {
    "achievements": [
      {
        "id": 1,
        "achievement_code": "first_session",
        "title_en": "First Steps",
        "title_es": "Primeros Pasos",
        "title_ru": "Первые Шаги",
        "description_en": "Complete your first learning session",
        "description_es": "Completa tu primera sesión de aprendizaje",
        "description_ru": "Завершите первую учебную сессию",
        "icon": "🎯",
        "xp_reward": 10,
        "category": "milestone",
        "difficulty": "bronze",
        "is_active": true
      },
      ...
    ]
  },
  "message": "Retrieved 25 available achievements"
}
```

#### Achievement Categories

- `streak`: Daily streak achievements
- `session`: Session-based achievements
- `milestone`: Learning milestones
- `special`: Special/rare achievements

#### Difficulty Tiers

- `bronze`: Easy achievements
- `silver`: Moderate achievements
- `gold`: Difficult achievements
- `platinum`: Very difficult/rare achievements

### GET /progress/achievements/{user_id}

Get achievements earned by user.

#### Response

```json
{
  "success": true,
  "data": {
    "achievements": [
      {
        "id": 1,
        "achievement_code": "first_session",
        "title_en": "First Steps",
        ...,
        "earned_at": "2025-11-01T09:00:00Z",
        "earned_metadata": {
          "session_id": 1,
          "session_type": "conversation"
        }
      },
      ...
    ]
  },
  "message": "User has earned 8 achievements"
}
```

### POST /progress/achievements/award

Award an achievement to a user.

#### Request Body

```json
{
  "user_id": 1,
  "achievement_code": "week_streak",
  "metadata": {
    "streak_length": 7,
    "date": "2025-11-10"
  }
}
```

#### Response (newly awarded)

```json
{
  "success": true,
  "data": {
    "newly_awarded": true,
    "achievement": {
      "id": 5,
      "achievement_code": "week_streak",
      "title_en": "Week Warrior",
      "xp_reward": 100,
      ...
    },
    "xp_awarded": 100
  },
  "message": "Achievement 'Week Warrior' awarded! +100 XP"
}
```

#### Response (already had it)

```json
{
  "success": true,
  "data": {
    "newly_awarded": false
  },
  "message": "User already has this achievement"
}
```

---

## Leaderboard

### GET /progress/leaderboard

Get ranked leaderboard.

#### Query Parameters

- `metric` (optional): Ranking metric (default: "total_xp")
  - `total_xp`: Total experience points
  - `current_level`: Current level
  - `longest_streak`: Longest daily streak
  - `total_study_time_seconds`: Total study time
- `limit` (optional): Number of users (default: 100, max: 1000)

#### Example

```
GET /progress/leaderboard?metric=current_level&limit=50
```

#### Response

```json
{
  "success": true,
  "data": {
    "metric": "current_level",
    "entries": [
      {
        "user_id": 42,
        "first_name": "Maria",
        "last_name": "Garcia",
        "username": "maria_g",
        "total_xp": 15000,
        "current_level": 12,
        "longest_streak": 45,
        "total_study_time_seconds": 86400,
        "current_streak": 30
      },
      ...
    ],
    "total_count": 50
  },
  "message": "Leaderboard retrieved: top 50 users by current_level"
}
```

---

## Cost Optimization

### Pronunciation Caching

The pronunciation cache provides **99% cost reduction** for TTS:

**Without caching:**
- 50,000 TTS requests × $0.015/1K = **$750**

**With caching (1% new, 99% cached):**
- 500 new TTS requests × $0.015/1K = **$7.50**

#### Best Practices

1. **Pre-cache common words** using `/pronunciation/cache/bulk`
2. **Always use `use_cache: true`** in synthesis requests
3. **Monitor cache stats** with `/pronunciation/cache/stats`
4. **Clean up periodically** with `/pronunciation/cache/cleanup`

#### Cache Key

Cached by: `(normalized_word, language_code, voice_id)`
- "Hola", "hola", " HOLA " → Same cache entry

---

## Database Tables

### Grammar Rules
- Multi-language support (EN, ES, RU)
- CEFR difficulty levels (A1-C2)
- JSONB examples with translations
- Categorized and searchable

### User Progress
- XP and level tracking
- Daily streak system
- Total study time
- Session count

### Achievements
- Multi-language descriptions
- XP rewards
- Category and difficulty tiers
- User achievement tracking

### Pronunciation Cache
- Base64 audio storage
- Usage tracking
- Language-specific voices
- Automatic deduplication

### Learning Sessions
- Session type tracking
- XP and duration
- JSONB metadata
- User analytics

---

## Error Handling

All endpoints return consistent error responses:

```json
{
  "success": false,
  "error": "Error message describing what went wrong"
}
```

### HTTP Status Codes

- `200 OK`: Success
- `201 Created`: Resource created
- `400 Bad Request`: Invalid input
- `404 Not Found`: Resource not found
- `409 Conflict`: Duplicate resource
- `413 Request Entity Too Large`: File too large
- `415 Unsupported Media Type`: Invalid file type
- `500 Internal Server Error`: Server error

---

## Rate Limits

Current implementation has no rate limits, but consider implementing:

- **TTS requests**: 100/minute per user
- **Chat streaming**: 20/minute per user
- **Progress updates**: 200/minute per user

---

## WebSocket vs SSE

We use **Server-Sent Events (SSE)** for streaming chat instead of WebSocket:

**Advantages:**
- ✅ Simpler protocol (HTTP)
- ✅ Auto-reconnect built-in
- ✅ Works through proxies
- ✅ No CORS preflight for GET
- ✅ Event ID tracking

**Trade-offs:**
- ❌ Unidirectional (server → client only)
- ✅ Perfect for chat streaming use case
