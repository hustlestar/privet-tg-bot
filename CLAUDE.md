# Claude Development Guide - Privet Bot Project

## Project Overview
AI-powered Telegram bot with FastAPI backend and React frontend for both users and administrators.

## Architecture

### Backend (FastAPI)
- **Location**: `/privet_api/`
- **Main file**: `privet_api/main.py`
- **Port**: 8000
- **OpenAPI Docs**: http://localhost:8000/docs

### Frontend (React Monorepo)
- **Location**: `/privet-ui/`
- **Structure**: Turborepo monorepo with 2 separate apps + shared package
- **User App Port**: 3000
- **Admin App Port**: 3001

## Frontend Structure

```
privet-ui/
├── apps/
│   ├── user-app/      # User-facing chat interface (port 3000)
│   └── admin-app/     # Admin CRM dashboard (port 3001)
├── packages/
│   └── shared/        # Shared components, hooks, utils
└── generated-client/  # Auto-generated TypeScript API client
```

## API Client Generation

### Generate TypeScript Client from OpenAPI
```bash
# Automated (starts backend, extracts spec, generates client)
python generate_api_client.py

# Manual (if backend already running)
python extract_openapi_spec.py
npx @openapitools/openapi-generator-cli generate \
  -i openapi.json \
  -g typescript-axios \
  -o generated-client
```

### Generated Client Usage
The client is installed as a local npm package in shared:
```json
"@privet/api-client": "file:../../../generated-client"
```

## Tech Stack

### Core Technologies
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Animations**: Framer Motion
- **State Management**: 
  - Zustand (global state)
  - TanStack Query (server state)
- **UI Components**: Radix UI
- **Icons**: Lucide React
- **Data Tables**: TanStack Table
- **Forms**: React Hook Form + Zod
- **Charts**: Recharts
- **Date handling**: date-fns

## Color Schemes

### User App (Language Learning Optimized)
- **Primary Blue** (#4A90E2): Focus and concentration
- **Success Green** (#52C41A): Progress and achievements  
- **Warning Orange** (#FFA940): CTAs and engagement
- **Background**: #FAFAFA (off-white to reduce eye strain)
- **Text**: #2C3E50 (softer than pure black)

### Admin App (Professional Dashboard)
- **Primary Blue** (#2C5F8D): Professional tone
- **Success Green** (#4A7C59): Muted success
- **Warning Amber** (#E89923): Professional alerts
- **Background**: #F9FAFB (subtle off-white)
- **Text**: #263445 (professional dark)

## Development Commands

### Install Dependencies
```bash
cd privet-ui
npm install --legacy-peer-deps
```

### Run Development Servers
```bash
# Run both apps
cd privet-ui
npm run dev

# Run individually
cd privet-ui/apps/user-app && npm run dev
cd privet-ui/apps/admin-app && npm run dev
```

### Backend
```bash
# Run with auto-reload
python -m privet_api.main

# The backend excludes UI directories from file watching
```

## API Endpoints

### Users
- `GET /api/v1/users/` - List all users
- `POST /api/v1/users/` - Create user
- `GET /api/v1/users/{user_id}` - Get user
- `PUT /api/v1/users/{user_id}` - Update user
- `DELETE /api/v1/users/{user_id}` - Delete user
- `GET /api/v1/users/{user_id}/stats` - Get user stats

### Conversations
- `POST /api/v1/conversations/process` - Process message
- `GET /api/v1/conversations/{user_id}/history` - Get history
- `DELETE /api/v1/conversations/{user_id}/messages/{message_id}` - Delete message

### Memory/RAG
- `POST /api/v1/memory/facts` - Create fact
- `POST /api/v1/memory/facts/search` - Search facts
- `GET /api/v1/memory/facts/{user_id}` - Get user facts
- `DELETE /api/v1/memory/facts/{fact_id}` - Delete fact
- `GET /api/v1/memory/summaries/{user_id}` - Get summaries
- `GET /api/v1/memory/context/{user_id}` - Get memory context
- `GET /api/v1/memory/stats/{user_id}` - Get memory stats

### Voice
- `POST /api/v1/voice/transcribe` - Transcribe audio
- `POST /api/v1/voice/synthesize` - Text to speech
- `POST /api/v1/voice/process` - Complete pipeline

## Admin Panel Pages

Complete admin interface with comprehensive management capabilities:

### Users Management (`/users`)
- User list with search, filtering, and pagination
- User detail pages with stats, conversations, and memory facts
- CRUD operations with confirmation dialogs
- Animated stats cards and professional data tables

### Conversations Monitoring (`/conversations`)
- Real-time conversation monitoring with user filtering
- Message search and date filtering
- Role-based message display (user vs assistant)
- Export capabilities and refresh functionality

### Memory & RAG System (`/memory`)
- User facts database with category management
- Semantic search interface for testing
- Category breakdown and distribution charts
- Fact CRUD operations with bulk actions

### Voice Processing (`/voice`)
- Speech-to-text transcription interface
- Text-to-speech synthesis with voice selection
- Audio file upload and playback controls
- Processing history and statistics

## React Hooks (Admin App)

Located in `/privet-ui/apps/admin-app/src/hooks/useApi.ts`:

### User Management
- `useUsers(offset, limit)` - List users with pagination
- `useUser(userId)` - Get single user
- `useUserStats(userId)` - Get user statistics
- `useCreateUser()` - Create new user mutation
- `useUpdateUser()` - Update user mutation
- `useDeleteUser()` - Delete user mutation

### Conversation Management
- `useConversationHistory(userId, limit, offset)` - Get chat history
- `useProcessConversation()` - Send message mutation
- `useDeleteConversation()` - Delete message mutation

### Memory/RAG Management
- `useUserFacts(userId, limit, offset, category)` - Get facts
- `useCreateFact()` - Create fact mutation
- `useSearchFacts()` - Search facts mutation
- `useDeleteFact()` - Delete fact mutation
- `useProfileSummaries(userId)` - Get summaries
- `useMemoryContext(userId, query)` - Get context
- `useMemoryStats(userId)` - Get stats

### Voice Processing
- `useTranscribeAudio()` - Transcribe mutation
- `useSynthesizeSpeech()` - TTS mutation

## Component Structure

### Shared Components (`packages/shared/components/ui/`)
- `Button` - Base button component
- `Card` - Card container
- `ThemeToggle` - Dark/light mode toggle

### Admin Components (`apps/admin-app/src/components/`)
- `layout/Sidebar` - Navigation sidebar with animations
- `ui/DataTable` - Professional data table with TanStack Table
- `ui/StatsCard` - Animated metric display cards
- `ui/LoadingSpinner` - Reusable loading component
- `ui/EmptyState` - Empty state with actions

### User Components (`apps/user-app/src/components/`)
- `chat/ChatInterface` - Main chat container
- `chat/MessageList` - Message display
- `chat/MessageInput` - Text input
- `chat/VoiceRecorder` - Voice recording
- `gamification/ProgressBar` - XP progress
- `gamification/StreakCounter` - Daily streak

## Environment Variables

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

### Backend (.env)
```env
# Database
DATABASE_URL=postgresql://user:pass@localhost/privet_db

# API Keys
OPENAI_API_KEY=sk-...
OPENROUTER_API_KEY=sk-or-...
ELEVENLABS_API_KEY=...

# Settings
DEBUG=true
TTS_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-ada-002
```

## Design Principles

### User App
- **60-30-10 Rule**: 60% neutral, 30% primary blue, 10% accent colors
- **Progressive difficulty**: Color gradients for skill levels
- **Gamification**: Progress bars, streaks, achievements
- **Reduce fatigue**: Off-white backgrounds, soft colors

### Admin App
- **Professional**: Muted colors, squared corners
- **Data-focused**: Charts, tables, metrics
- **Efficiency**: Keyboard shortcuts, bulk actions
- **Real-time**: WebSocket updates, live monitoring

## Common Issues & Solutions

### Issue: npm workspace errors
```bash
# Use --legacy-peer-deps flag
npm install --legacy-peer-deps
```

### Issue: TypeScript errors in generated client
```bash
# Remove problematic files and rebuild
rm generated-client/react-example.tsx
cd generated-client && npm run build
```

### Issue: Backend file watching crashes
The backend now excludes UI directories from file watching:
```python
reload_excludes = ["*/privet-ui/*", "*/node_modules/*"]
```

## Development Workflow

1. **Backend changes**: API automatically reloads
2. **Generate client**: Run `python generate_api_client.py`
3. **Frontend changes**: Next.js hot reloads
4. **Test API**: Use http://localhost:8000/docs
5. **Check UI**: 
   - User: http://localhost:3000
   - Admin: http://localhost:3001

## Future Enhancements

- [ ] WebSocket for real-time updates
- [ ] Advanced analytics dashboard
- [ ] Bulk user operations
- [ ] Export/import functionality
- [ ] A/B testing interface
- [ ] Message broadcasting
- [ ] Scheduled tasks
- [ ] Audit logging
