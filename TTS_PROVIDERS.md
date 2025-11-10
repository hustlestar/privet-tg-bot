# Text-to-Speech (TTS) Providers

The bot now supports multiple TTS providers that can be switched via environment variables without code changes.

## 🎯 Quick Configuration

In your `.env` file:
```env
# Choose your provider
TTS_PROVIDER=openai  # Options: elevenlabs, openai, google, amazon

# Provider-specific settings
TTS_VOICE=nova       # Voice selection
TTS_LANGUAGE=en-US   # Language code
TTS_MODEL=tts-1-hd   # Model (if applicable)
```

## 📊 Provider Comparison

| Provider | Quality | Cost | Emotion Support | Languages | Speed |
|----------|---------|------|-----------------|-----------|--------|
| **ElevenLabs** | ⭐⭐⭐⭐⭐ | $$$ | Excellent | 29+ | Fast |
| **OpenAI** | ⭐⭐⭐⭐ | $ | Limited | 50+ | Very Fast |
| **Google** | ⭐⭐⭐⭐ | $ | Limited | 40+ | Fast |
| **Amazon** | ⭐⭐⭐ | $ | Basic | 30+ | Fast |

## 🔧 Provider Details

### 1. ElevenLabs (`elevenlabs`)

**Best for:** High-quality, emotional voice synthesis

```env
TTS_PROVIDER=elevenlabs
ELEVENLABS_API_KEY=your_api_key_here
TTS_VOICE=Rachel  # Options: Rachel, Domi, Bella, Josh, etc.
```

**Features:**
- Superior voice quality
- Excellent emotion control
- Voice cloning available
- Real-time streaming

**Pricing:** ~$0.30 per 1,000 characters

---

### 2. OpenAI (`openai`)

**Best for:** Fast, affordable, good quality

```env
TTS_PROVIDER=openai
OPENAI_API_KEY=your_api_key_here
TTS_VOICE=nova  # Options: alloy, echo, fable, onyx, nova, shimmer
TTS_MODEL=tts-1  # or tts-1-hd for higher quality
```

**Voices:**
- `alloy` - Neutral and balanced
- `echo` - Male, warm
- `fable` - British, storyteller
- `onyx` - Deep, authoritative  
- `nova` - Female, friendly
- `shimmer` - Female, warm

**Pricing:** 
- tts-1: $0.015 per 1,000 characters
- tts-1-hd: $0.030 per 1,000 characters

---

### 3. Google Cloud (`google`)

**Best for:** Multi-language support, neural voices

```env
TTS_PROVIDER=google
GOOGLE_TTS_API_KEY=/path/to/service-account.json
TTS_VOICE=en-US-Neural2-C  # Many options available
TTS_LANGUAGE=en-US
```

**Setup:**
1. Create a Google Cloud project
2. Enable Text-to-Speech API
3. Create service account and download JSON key
4. Set path to JSON in `GOOGLE_TTS_API_KEY`

**Features:**
- Neural2 and WaveNet voices
- 40+ languages
- SSML support
- Custom voice models

**Pricing:**
- Standard: $4 per million characters
- Neural2/WaveNet: $16 per million characters

---

### 4. Amazon Polly (`amazon`)

**Best for:** AWS integration, cost-effective

```env
TTS_PROVIDER=amazon
AMAZON_POLLY_API_KEY=access_key,secret_key,region
TTS_VOICE=Joanna  # Many options
```

**Setup:**
```env
# Format: access_key,secret_key,region
AMAZON_POLLY_API_KEY=AKIA...,wJalr...,us-east-1
```

**Features:**
- Neural and standard voices
- SSML support
- Lexicon customization
- Long-form synthesis

**Pricing:**
- Standard: $4 per million characters
- Neural: $16 per million characters

## 🎭 Emotion Support

### ElevenLabs
Full emotion control through voice settings:
- Stability (0-1): Voice consistency
- Style (0-1): Emotional expressiveness
- Pre-configured emotions: cheerful, calm, excited, sad, angry

### OpenAI
Limited emotion through voice selection:
- Choose different voices for different moods
- Adjust speed (0.25-4.0) for emphasis

### Google & Amazon
Basic emotion through SSML prosody:
- Adjust rate, pitch, volume
- Limited emotional range

## 🌍 Language Support

### Most Supported Languages
- English (all providers)
- Spanish, French, German, Italian
- Portuguese, Russian, Japanese, Korean
- Chinese (Mandarin), Arabic, Hindi

### Provider-Specific
- **OpenAI**: 50+ languages with same voices
- **Google**: 40+ languages with locale-specific voices
- **ElevenLabs**: 29 languages with multilingual model
- **Amazon**: 30+ languages with dedicated voices

## 💰 Cost Optimization

### By Use Case

**High Volume, Low Cost:**
- Use OpenAI tts-1 or Google standard voices
- ~$0.015-$0.004 per 1,000 chars

**High Quality, Emotional:**
- Use ElevenLabs for important messages
- OpenAI tts-1-hd for good balance

**Multi-language:**
- Google for best language coverage
- OpenAI for consistent voice across languages

### Hybrid Approach
```python
# In your code, you could switch providers based on context:
if is_premium_user:
    os.environ['TTS_PROVIDER'] = 'elevenlabs'
elif needs_emotion:
    os.environ['TTS_PROVIDER'] = 'elevenlabs'
else:
    os.environ['TTS_PROVIDER'] = 'openai'
```

## 🚀 Quick Start Examples

### Example 1: High-Quality Emotional Bot
```env
TTS_PROVIDER=elevenlabs
ELEVENLABS_API_KEY=your_key
TTS_VOICE=Rachel
```

### Example 2: Cost-Effective Multi-language
```env
TTS_PROVIDER=openai
OPENAI_API_KEY=your_key
TTS_VOICE=nova
TTS_MODEL=tts-1
```

### Example 3: Enterprise with Google Cloud
```env
TTS_PROVIDER=google
GOOGLE_TTS_API_KEY=/secrets/gcp-key.json
TTS_VOICE=en-US-Neural2-F
TTS_LANGUAGE=en-US
```

## 🔍 Testing Voices

Run this to test your configuration:
```python
python -c "
from telegram_bot_template.config.settings import BotConfig
from telegram_bot_template.services.audio_service import AudioService
import asyncio

async def test():
    config = BotConfig.from_env()
    audio = AudioService(config)
    
    # Test TTS
    audio_bytes = await audio.text_to_speech(
        'Hello! This is a test of the TTS system.',
        emotion='cheerful'
    )
    
    if audio_bytes:
        with open('test_output.mp3', 'wb') as f:
            f.write(audio_bytes)
        print(f'✅ TTS working with {config.tts_provider}')
        print(f'Audio saved to test_output.mp3')
    else:
        print('❌ TTS failed')
    
    # Show provider info
    info = audio.get_tts_provider_info()
    print(f'Provider info: {info}')

asyncio.run(test())
"
```

## 🎯 Recommendations

1. **For Production:** Start with OpenAI (good balance of quality/cost)
2. **For Premium Features:** Use ElevenLabs for emotional responses
3. **For Enterprise:** Google Cloud with service account
4. **For AWS Users:** Amazon Polly with IAM roles

## 🔄 Switching Providers

Simply change `TTS_PROVIDER` in your `.env` and restart:
```bash
# No code changes needed!
TTS_PROVIDER=openai  # Switch from elevenlabs to openai
```

The bot automatically uses the new provider with appropriate settings.

---

**Note:** Always test voices with your target audience before production deployment!