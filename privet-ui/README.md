# Privet UI - Monorepo for React Applications

This monorepo contains two separate React applications built with Next.js 14, TypeScript, and Tailwind CSS.

## 🏗️ Architecture

### Two Separate Applications

1. **User App** (`apps/user-app`) - Chat interface for end users
   - Port: 3000
   - Features: Real-time chat, voice messages, animations
   - Tech: Framer Motion for animations, WebSocket for real-time

2. **Admin App** (`apps/admin-app`) - CRM dashboard for administrators
   - Port: 3001
   - Features: User management, analytics, memory/RAG management
   - Tech: Data visualization, tables, forms

### Shared Package

The `packages/shared` directory contains:
- Generated API client (installed via npm from generated-client)
- Reusable UI components (Button, Card, etc.)
- Custom hooks (useApi, useApiHealth)
- Utility functions (cn for className merging)

## 🚀 Getting Started

### Prerequisites

- Node.js 18+
- npm 9+
- Running FastAPI backend on port 8000

### Installation

1. Generate the API client first (from root directory):
```bash
cd ..
python generate_api_client.py
```

2. Install dependencies:
```bash
npm install
```

3. Start development servers:
```bash
# Start both apps
npm run dev

# Or start individually
npm run dev --workspace=@privet-ui/user-app
npm run dev --workspace=@privet-ui/admin-app
```

### Access the applications:
- User App: http://localhost:3000
- Admin App: http://localhost:3001

## 🎨 Tech Stack

### Core Technologies
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Animations**: Framer Motion
- **State Management**: Zustand + TanStack Query
- **UI Components**: Radix UI (unstyled, accessible primitives)
- **Icons**: Lucide React

### Why This Stack?

1. **Framer Motion** - Best-in-class animation library for React
   - Declarative animations
   - Gesture support
   - Layout animations
   - Optimized performance

2. **Tailwind CSS** - Rapid development with utility classes
   - Consistent design system
   - Small bundle size
   - Perfect integration with Framer Motion

3. **Radix UI** - Accessible, unstyled components
   - Full customization control
   - Built-in accessibility
   - Animation-ready

## 📁 Project Structure

```
privet-ui/
├── apps/
│   ├── user-app/          # User-facing chat application
│   │   ├── src/
│   │   │   ├── app/       # Next.js app router
│   │   │   ├── components/# React components
│   │   │   └── hooks/     # Custom hooks
│   │   └── package.json
│   │
│   └── admin-app/         # Admin CRM dashboard
│       ├── src/
│       │   ├── app/       # Next.js app router
│       │   ├── components/# React components
│       │   └── hooks/     # Custom hooks
│       └── package.json
│
├── packages/
│   └── shared/            # Shared code between apps
│       ├── components/    # Reusable UI components
│       ├── hooks/         # Shared React hooks
│       ├── utils/         # Utility functions
│       └── package.json
│
├── turbo.json            # Turborepo configuration
└── package.json          # Root package.json
```

## 🛠️ Development

### Available Scripts

```bash
# Development
npm run dev              # Start all apps in development mode
npm run build           # Build all apps for production
npm run lint            # Lint all apps
npm run type-check      # Type check all apps
npm run clean           # Clean build artifacts

# Generate API Client
npm run generate:client  # Regenerate TypeScript client from OpenAPI spec
```

### Environment Variables

Create `.env.local` files in each app:

```env
# apps/user-app/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000

# apps/admin-app/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

## 🎯 Features

### User App Features
- ✅ Real-time chat interface
- ✅ Voice message recording
- ✅ Typing indicators
- ✅ Emotion indicators
- ✅ Smooth animations
- ✅ Responsive design
- 🔄 WebSocket support (planned)
- 🔄 File attachments (planned)

### Admin App Features
- ✅ Dashboard with analytics
- ✅ User management
- ✅ Conversation monitoring
- 🔄 Memory/RAG content management
- 🔄 Real-time metrics
- 🔄 Settings configuration
- 🔄 Export functionality

## 🚢 Deployment

### Build for Production

```bash
npm run build
```

### Deploy with Docker

```dockerfile
# Dockerfile example
FROM node:18-alpine AS builder
WORKDIR /app
COPY . .
RUN npm ci
RUN npm run build

FROM node:18-alpine AS runner
WORKDIR /app
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

EXPOSE 3000 3001
CMD ["npm", "start"]
```

## 📝 Contributing

1. Create a feature branch
2. Make your changes
3. Ensure tests pass
4. Submit a pull request

## 📄 License

MIT