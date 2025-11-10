[![Deploy Telegram Bot](https://github.com/hustlestar/tg-bot-template/actions/workflows/deploy.yml/badge.svg)](https://github.com/hustlestar/tg-bot-template/actions/workflows/deploy.yml)
# Simplified Telegram Bot Template

A clean, maintainable Telegram bot template with essential features and modern architecture.

## 🚀 Features

- **🌐 Locale Management** - Multi-language support with easy translation management
- **⌨️ Keyboard Management** - Dynamic inline keyboards with language-aware buttons
- **🤖 OpenRouter AI Integration** - Modern AI provider with multiple model support
- **🆘 Optional Support Bot** - Built-in support system for user assistance
- **💾 Database with Migrations** - PostgreSQL with Alembic migration management
- **🔄 Auto-Migration** - Automatic schema updates on bot startup
- **🎛️ Click CLI** - Command-line interface with migration commands
- **📝 Clean Architecture** - Well-organized, extensible codebase

## 📁 Project Structure

```
telegram_bot_template/
├── __init__.py                    # Package initialization
├── main.py                        # Entry point with click options
├── cli.py                         # CLI commands for migrations
├── config/
│   ├── __init__.py
│   └── settings.py               # Configuration management
├── core/
│   ├── __init__.py
│   ├── bot.py                    # Main bot class
│   ├── database.py               # Database operations with migrations
│   ├── migration_manager.py      # Alembic migration management
│   ├── locale_manager.py         # Localization support
│   ├── keyboard_manager.py       # Keyboard management
│   └── ai_provider.py            # OpenRouter integration
├── models/
│   ├── __init__.py               # SQLAlchemy metadata
│   ├── base.py                   # Base table definitions
│   └── users.py                  # Users table schema
├── handlers/
│   ├── __init__.py
│   ├── basic.py                  # Basic commands (/start, /help, /about)
│   └── message.py                # Message handling with AI
├── support/
│   ├── __init__.py
│   └── bot.py                    # Optional support bot
└── utils/
    ├── __init__.py
    └── helpers.py                # Utility functions

alembic/                           # Database migration files
├── env.py                        # Alembic environment configuration
├── script.py.mako               # Migration template
└── versions/                     # Migration version files
    └── 001_initial_users_table.py

alembic.ini                       # Alembic configuration
```

## 🛠️ Installation

1. **Install uv** (if not already installed)
   ```bash
   # On macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # On Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

   # Or with pip
   pip install uv
   ```

2. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd telegram-bot-template
   ```

3. **Setup virtual environment and install dependencies**
   ```bash
   # Create virtual environment and sync dependencies
   uv sync

   # Or install directly into current environment
   uv pip install -e .
   ```

4. **Setup environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Setup database**
   ```bash
   # Create PostgreSQL database
   createdb botdb
   ```

## ⚙️ Configuration

### Required Environment Variables

```env
# Required
TELEGRAM_BOT_TOKEN=your_bot_token_here
DATABASE_URL=postgresql://user:password@localhost:5432/botdb
```

### Optional Environment Variables

```env
# OpenRouter AI (optional)
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=openai/gpt-3.5-turbo

# Support Bot (optional)
SUPPORT_BOT_TOKEN=your_support_bot_token_here
SUPPORT_CHAT_ID=your_support_chat_id_here

# Bot Metadata (optional)
BOT_NAME=My Telegram Bot
BOT_DESCRIPTION=A simple Telegram bot
BOT_VERSION=1.0.0

# Localization (optional)
DEFAULT_LANGUAGE=en
SUPPORTED_LANGUAGES=en,ru,es

# Logging (optional)
LOG_LEVEL=INFO
```

## 🚀 Usage

### Basic Usage

```bash
# Activate virtual environment (if using uv sync)
source .venv/bin/activate  # On Linux/macOS
# or
.venv\Scripts\activate     # On Windows

# Start the bot
python -m telegram_bot_template.main

# Start with specific language
python -m telegram_bot_template.main --locale ru

# Start in debug mode
python -m telegram_bot_template.main --debug

# Validate configuration without starting
python -m telegram_bot_template.main --dry-run
```

### CLI Commands

```bash
# Using uv run (recommended)
uv run telegram-bot-template db status
uv run telegram-bot-template migrate
uv run telegram-bot-template db revision -m "Add new table"
uv run telegram-bot-template db upgrade
uv run telegram-bot-template db downgrade

# Or after activating virtual environment
telegram-bot-template db status
telegram-bot-template migrate
telegram-bot-template db revision -m "Add new table"
telegram-bot-template db upgrade
telegram-bot-template db downgrade
telegram-bot-template db history
telegram-bot-template db current
```

## 💾 Database Migrations

The template uses Alembic for professional database schema management with automatic migration support.

### Automatic Migrations

By default, the bot automatically applies pending migrations on startup:

```bash
# Bot will check and apply migrations automatically
python -m telegram_bot_template.main
```

### Manual Migration Commands

```bash
# Check migration status
telegram-bot-template db status

# Apply all pending migrations
telegram-bot-template migrate

# Create a new migration
telegram-bot-template db revision -m "Add new table"

# Apply migrations manually
telegram-bot-template db upgrade

# Rollback to previous migration
telegram-bot-template db downgrade

# Show migration history
telegram-bot-template db history

# Show current revision
telegram-bot-template db current
```

### Migration Configuration

Control migration behavior with environment variables:

```env
# Enable/disable automatic migrations (default: true)
AUTO_MIGRATE=true

# Migration timeout in seconds (default: 300)
MIGRATION_TIMEOUT=300
```

### Creating New Migrations

1. **Modify your models** in `telegram_bot_template/models/`
2. **Generate migration**:
   ```bash
   telegram-bot-template db revision --autogenerate -m "Description of changes"
   ```
3. **Review the generated migration** in `alembic/versions/`
4. **Apply the migration**:
   ```bash
   telegram-bot-template db upgrade
   ```

### Migration Best Practices

- **Always review** auto-generated migrations before applying
- **Test migrations** in a staging environment first
- **Backup your database** before applying migrations in production
- **Use descriptive messages** when creating migrations
- **Keep migrations small** and focused on single changes

### Programmatic Usage

```python
from telegram_bot_template import TelegramBot, BotConfig

# Load configuration from environment
config = BotConfig.from_env()

# Create and run bot
bot = TelegramBot(config)
await bot.run()
```

## 🤖 AI Integration

The template uses OpenRouter for AI functionality, which provides access to multiple AI models through a unified API.

### Supported Models

- OpenAI GPT models (gpt-3.5-turbo, gpt-4, etc.)
- Anthropic Claude models
- Google PaLM models
- And many more through OpenRouter

### Getting OpenRouter API Key

1. Visit [OpenRouter.ai](https://openrouter.ai)
2. Sign up for an account
3. Generate an API key
4. Add it to your `.env` file

## 🆘 Support Bot

The optional support bot allows users to send messages directly to administrators.

### Setup Support Bot

1. Create a second bot with @BotFather
2. Get the bot token
3. Get your Telegram user ID (chat with @userinfobot)
4. Add both to your `.env` file:
   ```env
   SUPPORT_BOT_TOKEN=your_support_bot_token
   SUPPORT_CHAT_ID=your_telegram_user_id
   ```

### How It Works

- Users send messages to the support bot
- Messages are forwarded to the admin
- Admin replies to forwarded messages
- Replies are sent back to users

## 🌐 Localization

### Adding New Languages

1. Create a new JSON file in `locales/` directory:
   ```bash
   cp locales/en.json locales/de.json
   ```

2. Translate the strings in the new file

3. Add the language to supported languages:
   ```env
   SUPPORTED_LANGUAGES=en,ru,es,de
   ```

### Translation Keys

The template includes these translation keys:

- `welcome_message` - Bot welcome message
- `help_message` - Help text
- `about_message` - About text
- `language_changed` - Language change confirmation
- `processing` - Processing message
- `error_occurred` - Generic error message
- And more...

## 📊 Database Schema

The template uses a simple database schema with just a users table:

```sql
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    username VARCHAR(255),
    language VARCHAR(10) DEFAULT 'en',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔧 Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=telegram_bot_template
```

### Code Formatting

```bash
# Format code
black telegram_bot_template/
isort telegram_bot_template/

# Type checking
mypy telegram_bot_template/
```

### Adding New Features

1. **New Handlers**: Add to `handlers/` directory
2. **New Commands**: Register in `core/bot.py`
3. **New Keyboards**: Add to `keyboard_manager.py`
4. **New Translations**: Add to locale files

## 🐳 Docker Deployment

```bash
# Build image
docker build -t telegram-bot .

# Run with docker-compose
docker-compose up -d
```

## 📝 Examples

### Simple Echo Bot

```python
from telegram_bot_template import TelegramBot, BotConfig

config = BotConfig.from_env()
config.openrouter_api_key = None  # Disable AI

bot = TelegramBot(config)
await bot.run()
```

### AI-Powered Bot

```python
from telegram_bot_template import TelegramBot, BotConfig

config = BotConfig.from_env()
# AI will be enabled if OPENROUTER_API_KEY is set

bot = TelegramBot(config)
await bot.run()
```

### Custom Configuration

```python
from telegram_bot_template import TelegramBot, BotConfig

config = BotConfig(
    bot_token="your_token",
    database_url="postgresql://...",
    bot_name="Custom Bot",
    default_language="ru"
)

bot = TelegramBot(config)
await bot.run()
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- Create an issue for bug reports
- Join our Telegram group for discussions
- Check the documentation for detailed guides

## 🔄 Migration from Complex Template

If you're migrating from the complex template:

1. **Database**: Only the users table is needed
2. **Configuration**: Update environment variables
3. **AI Provider**: Replace OpenAI with OpenRouter
4. **Features**: Remove payment/subscription code
5. **Handlers**: Simplify message handling

## 🎯 Roadmap

- [ ] Plugin system for extensions
- [ ] Webhook support
- [ ] Admin dashboard
- [ ] Message scheduling
- [ ] User analytics
- [ ] Rate limiting
- [ ] Message templates

## 🔄 Migration from pip to uv

This project has been migrated to use `uv` for modern Python package management. If you're migrating from an older version that used `requirements.txt`, please see [MIGRATION_FROM_PIP_TO_UV.md](MIGRATION_FROM_PIP_TO_UV.md) for detailed instructions.

### Quick Start with uv

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Setup project
uv sync
source .venv/bin/activate

# Run the bot
python -m telegram_bot_template.main
```

## 🎨 Frontend UI & API Client

This project includes a FastAPI backend with automatic OpenAPI spec generation and TypeScript client generation for React applications.

### API Client Generation

Generate a TypeScript client for your React applications:

```bash
# Method 1: Automated script (starts backend, extracts spec, generates client)
python generate_api_client.py

# Method 2: Using shell script
./generate_client.sh

# Method 3: Manual steps (if backend is already running)
python extract_openapi_spec.py
npx @openapitools/openapi-generator-cli generate \
  -i openapi.json \
  -g typescript-axios \
  -o generated-client \
  --additional-properties=supportsES6=true,npmName=privet-api-client,npmVersion=1.0.0
```

The generated client will be in the `generated-client/` directory with:
- Full TypeScript types for all API endpoints
- Axios-based HTTP client
- Ready-to-use React integration examples

### Using the Generated Client in React

```typescript
import { Configuration, UsersApi, ConversationsApi } from './generated-client';

// Configure API client
const config = new Configuration({
  basePath: process.env.REACT_APP_API_URL || 'http://localhost:8000'
});

// Create API instances
const usersApi = new UsersApi(config);
const conversationsApi = new ConversationsApi(config);

// Use in your components
const user = await usersApi.getUserOrCreate({ /* ... */ });
const response = await conversationsApi.processMessage({ /* ... */ });
```

See `generated-client/react-example.tsx` for complete integration examples.

---

**Made with ❤️ for the Telegram bot community**