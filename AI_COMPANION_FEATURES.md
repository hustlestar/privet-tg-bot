# AI Language Companion - Feature Documentation

## 🎯 Overview

This Telegram bot is now a sophisticated AI language companion with voice conversation capabilities, emotional intelligence, and long-term memory. It builds personalized relationships with users through natural conversations.

## ✨ Core Features

### 1. 🎤 Voice Conversations
- **Speech-to-Text (STT)**: Transcribes voice messages using OpenAI Whisper
- **Text-to-Speech (TTS)**: Generates emotionally-aware voice responses using ElevenLabs
- **Emotional Voice Synthesis**: Adjusts voice tone based on conversation mood

### 2. 🧠 Intelligent Memory (RAG)
- **Vector Embeddings**: Uses pgvector for semantic similarity search
- **Fact Storage**: Automatically extracts and stores important information
- **Context Retrieval**: Recalls relevant memories during conversations
- **Profile Building**: Creates comprehensive user profiles over time

### 3. 💭 Emotional Intelligence
- **Sentiment Analysis**: Detects user emotions and mood
- **Empathetic Responses**: Adjusts response tone based on user's emotional state
- **Mood Tracking**: Monitors conversation mood trajectory
- **Voice Tone Mapping**: Selects appropriate voice emotions for TTS

### 4. 🔄 Conversation Management
- **Context Awareness**: Maintains conversation history and continuity
- **Information Extraction**: Identifies and categorizes important facts
- **Personalized Responses**: Uses stored memories to personalize interactions
- **Multi-turn Conversations**: Handles complex, ongoing dialogues

## 📋 Prerequisites

### Required API Keys
```env
# In your .env file:
TELEGRAM_BOT_TOKEN=your_bot_token           # Required
DATABASE_URL=postgresql+asyncpg://...       # Required
OPENAI_API_KEY=your_openai_key             # For STT (Whisper)
ELEVENLABS_API_KEY=your_elevenlabs_key     # For TTS
OPENROUTER_API_KEY=your_openrouter_key     # For LLM
```

### Database Setup
1. PostgreSQL with pgvector extension
2. Run migrations: `alembic upgrade head`
3. Verify with: `python check_database_health.py`

## 🚀 Quick Start

### 1. System Check
```bash
# Verify all components are ready
python test_full_system.py
```

### 2. Test Individual Components
```bash
# Test voice pipeline
python test_voice_pipeline.py

# Check database and pgvector
python check_database_health.py

# Test RAG service
python test_rag_service.py
```

### 3. Run the Bot
```bash
python -m telegram_bot_template
```

## 🎙️ Voice Conversation Flow

1. **User sends voice message** → Bot downloads audio file
2. **STT Processing** → Whisper transcribes to text
3. **Emotion Analysis** → NLP service analyzes sentiment and emotion
4. **Memory Retrieval** → RAG searches for relevant past conversations
5. **Context Building** → Combines memories, emotions, and history
6. **AI Response** → LLM generates personalized response
7. **Fact Extraction** → Important information saved to memory
8. **TTS Generation** → ElevenLabs creates emotional voice response
9. **Voice Reply** → Bot sends both text and voice responses

## 📊 Information Types Tracked

- **Personal Facts**: Name, age, location, occupation
- **Preferences**: Likes, dislikes, favorites
- **Memories**: Events, experiences, stories
- **Routines**: Daily habits, schedules
- **Relationships**: Family, friends, connections
- **Goals**: Aspirations, plans, objectives
- **Emotions**: Feelings, mood patterns
- **Skills**: Abilities, expertise areas
- **Health**: Wellness information
- **Context**: Current situations

## 🔧 Architecture Components

### Services
- `AudioService`: Handles STT and TTS operations
- `NLPService`: Emotion and sentiment analysis
- `RAGService`: Vector embeddings and similarity search
- `InformationExtractionService`: Fact extraction from conversations
- `ConversationManager`: Orchestrates all services

### Data Access Objects (DAO)
- `UserDAO`: User management
- `ConversationMessageDAO`: Message storage
- `UserFactDAO`: Fact storage with embeddings
- `UserProfileSummaryDAO`: Profile summaries

### Database Tables
- `users`: User information
- `conversation_messages`: Full conversation history
- `user_facts`: Extracted facts with vector embeddings
- `user_profile_summaries`: Generated user profiles

## 🎨 Emotional Voice Tones

The bot adjusts voice synthesis based on detected emotions:
- **Joy**: Cheerful and warm voice
- **Sadness**: Gentle and compassionate tone
- **Excitement**: Energetic and enthusiastic
- **Calm**: Steady and reassuring
- **Love**: Warm and affectionate
- **Frustration**: Patient and supportive

## 📈 Performance Considerations

- **Embedding Dimension**: 384 (using all-MiniLM-L6-v2)
- **Conversation History**: Keeps last 10 exchanges in memory
- **Fact Retrieval**: Returns top 5 most relevant facts
- **State Cleanup**: Clears inactive states after 1 hour
- **Vector Similarity Threshold**: 0.7 (configurable)

## 🔍 Monitoring & Debugging

### Logs to Watch
```python
# Key log patterns:
"Extracted X facts from conversation"
"Retrieved X relevant facts for user"
"Stored voice message X for user Y"
"Emotion: [detected_emotion]"
"Successfully generated audio with emotion"
```

### Health Checks
- Database connection status
- pgvector extension availability
- API key configuration
- Service initialization
- Embedding generation

## 🚧 Troubleshooting

### Voice Not Working
1. Check `OPENAI_API_KEY` for STT
2. Check `ELEVENLABS_API_KEY` for TTS
3. Verify audio file format compatibility

### Memory Not Working
1. Ensure pgvector extension is installed
2. Check embedding dimension matches (384)
3. Verify `OPENROUTER_API_KEY` for fact extraction

### No Intelligent Responses
1. Verify `OPENROUTER_API_KEY` is set
2. Check AI provider connection
3. Ensure conversation manager is initialized

## 🎯 Usage Examples

### Voice Message Interaction
1. User: *sends voice message* "Hi, I'm feeling a bit stressed about my exam tomorrow"
2. Bot: 
   - Detects stress/anxiety emotion
   - Retrieves past academic discussions
   - Responds with supportive tone
   - Stores exam information as a fact
   - Generates calming voice response

### Memory Recall
1. User: "What was that book I mentioned last week?"
2. Bot:
   - Searches vector embeddings for book-related facts
   - Retrieves relevant conversation context
   - Provides specific book information

### Emotional Support
1. User: *excited voice* "I got the job!"
2. Bot:
   - Detects joy/excitement
   - Responds with enthusiastic congratulations
   - Stores job achievement as important fact
   - Uses cheerful voice tone

## 🔮 Future Enhancements

- [ ] Multi-language support for voice
- [ ] Voice emotion detection (beyond text)
- [ ] Proactive check-ins based on patterns
- [ ] Voice cloning for personalized TTS
- [ ] Advanced memory consolidation
- [ ] Conversation summarization
- [ ] Mood trend analysis and insights

## 📝 Development Notes

- All services are async for optimal performance
- Facts are deduplicated before storage
- Conversation states are managed in-memory
- Background tasks handle fact extraction
- Voice files are cleaned up after processing

---

**Ready to build meaningful AI relationships through voice!** 🎙️🤖❤️