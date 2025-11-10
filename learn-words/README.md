# Learn Words Telegram Bot 🎓

A sophisticated Telegram bot that helps users learn new languages through intelligent word translation, vocabulary management, and adaptive training exercises.

## Features ✨

### Core Functionality
- **Smart Translation**: Translate words with 3 detail levels (short, medium, long)
- **Intelligent Caching**: All translations are cached in PostgreSQL for fast retrieval
- **Sentence Parsing**: Input sentences and select individual words to learn
- **Adaptive Training**: Personalized exercises based on your learning progress

### Training System
- **3 Exercise Types**:
  - Direct Translation (learning language → native language)
  - Multiple Choice (4 options)
  - Reverse Translation (native language → learning language)
- **Smart Word Selection**: Prioritizes words with low success rates and few attempts
- **Progress Tracking**: Comprehensive statistics and performance analytics
- **Spaced Repetition**: Words appear based on your mastery level

### User Experience
- **Multi-language Support**: Learn any language pair
- **Customizable Responses**: Choose your preferred detail level
- **Mark as Known**: Skip words you already know (but still practice them)
- **Progress Statistics**: Track your learning journey
- **Intuitive Interface**: Simple commands and inline keyboards

## Setup Instructions 🚀

### Prerequisites
- Python 3.11+
- PostgreSQL database
- Telegram Bot Token (from @BotFather)
- OpenAI API Key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd learn-words
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your credentials:
   ```env
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   OPENAI_API_KEY=your_openai_api_key
   DATABASE_URL=postgresql://username:password@localhost:5432/learn_words
   ```

4. **Set up PostgreSQL database**
   ```bash
   createdb learn_words
   ```

5. **Run the bot**
   ```bash
   python main.py
   ```

## Usage Guide 📖

### Getting Started
1. Start a conversation with your bot: `/start`
2. Set your native language (e.g., "English")
3. Set the language you want to learn (e.g., "Spanish")
4. Choose your preferred response detail level

### Basic Commands
- `/start` - Initial setup or view current settings
- `/train` - Start a training session
- `/stats` - View your learning progress
- `/settings` - Change response mode preferences

### Learning Workflow

#### Adding Words
- **Single words**: Just send a word (e.g., "casa")
- **Sentences**: Send a sentence and select words to learn
- **Mark as known**: Use the button if you already know a word

#### Training
- Use `/train` to start practicing
- Answer questions using text input or multiple choice
- Get immediate feedback with explanations
- Continue with more words or check your stats

#### Response Modes
- **Short**: Just the translation
- **Medium**: Translation + meaning + example
- **Long**: Multiple translations + meanings + examples + context

## Architecture 🏗️

### Project Structure
```
learn-words/
├── src/
│   ├── bot.py          # Main bot logic and handlers
│   ├── database.py     # Database operations
│   ├── translator.py   # OpenAI integration & word normalization
│   ├── training.py     # Training system and exercises
│   ├── models.py       # Data models and enums
│   └── config.py       # Configuration management
├── migrations/
│   └── init.sql        # Database schema
├── main.py             # Entry point
├── .env.example        # Environment template
└── README.md
```

### Database Schema
- **users**: User preferences and language settings
- **words**: Cached translations with all detail levels
- **user_word_stats**: Individual word progress tracking
- **training_attempts**: Detailed training history

### Key Components
- **Smart Word Selection**: Priority algorithm based on success rate and attempt count
- **Word Normalization**: Converts words to base forms (singular, infinitive)
- **Adaptive Training**: Randomized exercises with intelligent word prioritization
- **Comprehensive Analytics**: Track learning progress and identify weak areas

## Configuration ⚙️

### Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token | Required |
| `OPENAI_API_KEY` | Your OpenAI API key | Required |
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `OPENAI_MODEL` | OpenAI model to use | `gpt-4o-mini` |
| `MAX_TRAINING_WORDS` | Max words per training session | `10` |
| `DEFAULT_RESPONSE_MODE` | Default detail level | `medium` |

### Database Configuration
The bot automatically creates all necessary tables on first run. Ensure your PostgreSQL user has CREATE privileges.

## Development 🛠️

### Adding New Features
1. **New Training Types**: Extend `TrainingType` enum and implement in `training.py`
2. **Additional Languages**: The system supports any language pair
3. **Enhanced Analytics**: Add new statistics in `database.py`
4. **UI Improvements**: Modify keyboards and messages in `bot.py`

### Testing
```bash
# Run with test database
DATABASE_URL=postgresql://username:password@localhost:5432/learn_words_test python main.py
```

## Troubleshooting 🔧

### Common Issues
1. **Database Connection**: Ensure PostgreSQL is running and credentials are correct
2. **OpenAI API**: Check your API key and billing status
3. **Telegram Token**: Verify token with @BotFather
4. **Import Errors**: Ensure all dependencies are installed with `uv sync`

### Logs
The bot logs all activities. Check console output for detailed error messages.

## Contributing 🤝

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License 📄

This project is licensed under the MIT License - see the LICENSE file for details.

## Support 💬

For questions, issues, or feature requests, please open an issue on GitHub.

---

**Happy Learning! 🎉**
