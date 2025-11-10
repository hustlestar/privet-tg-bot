# Simple Parallel Translator Usage Guide

## Overview

The `simple_parallel_translator.py` script provides a streamlined version of the database population functionality, focusing only on core parallel translation without checkpoints, statistics, reports, or CLI interface.

## Key Features

- ✅ **Simple Function Interface**: Single async function call
- ✅ **Parallel Processing**: Configurable batch size and concurrency
- ✅ **Rate Limiting**: Built-in API rate limiting and circuit breaker
- ✅ **Error Handling**: Retry logic with exponential backoff
- ✅ **File Input**: Load words from JSON files
- ❌ **No Checkpoints**: No resume functionality
- ❌ **No Statistics**: Minimal result tracking
- ❌ **No Reports**: No detailed reporting
- ❌ **No CLI**: Function-based interface only

## Function Signature

```python
async def simple_parallel_translation(
    input_file: str,
    from_lang: str,
    to_lang: str,
    native_lang: str,
    learning_lang: str,
    batch_size: int = 50,
    max_concurrent: int = 25,
    requests_per_second: float = 50.0
) -> Dict[str, Any]
```

### Parameters

- **`input_file`**: Path to JSON file containing word list
- **`from_lang`**: Source language for translation (e.g., "russian")
- **`to_lang`**: Target language for translation (e.g., "english")
- **`native_lang`**: User's native language (for context)
- **`learning_lang`**: User's learning language (for context)
- **`batch_size`**: Number of words to process per batch (default: 50)
- **`max_concurrent`**: Maximum concurrent translation tasks (default: 25)
- **`requests_per_second`**: Rate limit for API calls (default: 50.0)

### Return Value

```python
{
    "total_words": int,      # Total words in input file
    "processed": int,        # Successfully translated words
    "skipped": int,          # Words already in database
    "errors": int,           # Failed translations
    "duration": float,       # Processing time in seconds
    "throughput": float,     # Words per second
    "error": str             # Error message (if any)
}
```

## Input File Format

The script accepts JSON files in multiple formats:

### Format 1: With "words" wrapper (dictionary objects)
```json
{
  "words": [
    {"word": "привет", "frequency": 1000},
    {"word": "мир", "frequency": 800},
    {"word": "дом", "frequency": 600}
  ]
}
```

### Format 2: Direct array (dictionary objects)
```json
[
  {"word": "привет", "frequency": 1000},
  {"word": "мир", "frequency": 800},
  {"word": "дом", "frequency": 600}
]
```

### Format 3: With "words" wrapper (string array)
```json
{
  "words": [
    "привет",
    "мир",
    "дом"
  ]
}
```

### Format 4: Direct string array
```json
[
  "привет",
  "мир",
  "дом"
]
```

## Usage Examples

### Basic Usage

```python
import asyncio
from scripts.simple_parallel_translator import simple_parallel_translation

async def translate_russian_words():
    result = await simple_parallel_translation(
        input_file="scripts/generated_lists/russian_1000.json",
        from_lang="russian",
        to_lang="english",
        native_lang="russian",
        learning_lang="english"
    )
    
    print(f"Processed: {result['processed']}")
    print(f"Skipped: {result['skipped']}")
    print(f"Errors: {result['errors']}")
    print(f"Duration: {result['duration']:.1f}s")

# Run the translation
asyncio.run(translate_russian_words())
```

### Custom Configuration

```python
async def translate_with_custom_settings():
    result = await simple_parallel_translation(
        input_file="my_words.json",
        from_lang="polish",
        to_lang="english",
        native_lang="polish",
        learning_lang="english",
        batch_size=25,           # Smaller batches
        max_concurrent=10,       # Lower concurrency
        requests_per_second=20.0 # Conservative rate limit
    )
    
    return result
```

### Error Handling

```python
async def safe_translation():
    try:
        result = await simple_parallel_translation(
            input_file="words.json",
            from_lang="spanish",
            to_lang="english",
            native_lang="spanish",
            learning_lang="english"
        )
        
        if "error" in result:
            print(f"Translation failed: {result['error']}")
            return False
            
        success_rate = result['processed'] / result['total_words'] * 100
        print(f"Success rate: {success_rate:.1f}%")
        return True
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
```

## Performance Tuning

### Conservative Settings (Stable)
```python
result = await simple_parallel_translation(
    input_file="words.json",
    from_lang="russian",
    to_lang="english", 
    native_lang="russian",
    learning_lang="english",
    batch_size=20,
    max_concurrent=5,
    requests_per_second=10.0
)
```

### High Performance Settings (Fast)
```python
result = await simple_parallel_translation(
    input_file="words.json",
    from_lang="russian",
    to_lang="english",
    native_lang="russian", 
    learning_lang="english",
    batch_size=100,
    max_concurrent=50,
    requests_per_second=100.0
)
```

## Testing

Run the test script to verify functionality:

```bash
uv run python scripts/test_simple_translator.py
```

This will:
1. Create a small test word list
2. Run the simple parallel translator
3. Display results
4. Test with existing word list files (if available)

## Comparison with Full populate_database.py

| Feature | Simple Translator | Full populate_database.py |
|---------|------------------|---------------------------|
| **Interface** | Function call | CLI with many options |
| **Checkpoints** | ❌ None | ✅ Full checkpoint system |
| **Statistics** | ❌ Basic only | ✅ Comprehensive stats |
| **Reports** | ❌ None | ✅ Detailed reports |
| **Resume** | ❌ No | ✅ Resume from checkpoint |
| **Bidirectional** | ❌ Single direction | ✅ Bidirectional processing |
| **Word Sources** | ❌ Files only | ✅ Files, DB, mixed |
| **Performance** | ✅ Fast setup | ✅ Advanced monitoring |
| **Use Case** | Quick translations | Production processing |

## When to Use

### Use Simple Translator When:
- ✅ You need quick, one-off translations
- ✅ You have a specific word list file
- ✅ You want minimal setup and configuration
- ✅ You don't need resume functionality
- ✅ You're doing development/testing

### Use Full populate_database.py When:
- ✅ You need production-grade processing
- ✅ You want comprehensive statistics and reports
- ✅ You need checkpoint/resume functionality
- ✅ You're processing large datasets
- ✅ You need bidirectional translation
- ✅ You want advanced monitoring and error tracking

## Dependencies

The script requires the same dependencies as the main application:
- `asyncio` (built-in)
- `json` (built-in)
- `logging` (built-in)
- `src.database.Database`
- `src.translation.translator.TranslationService`
- `scripts.util.TokenBucketRateLimiter`
- `scripts.util.CircuitBreaker`
- `scripts.util.ErrorClassifier`

Make sure your environment is properly configured with database access and API keys.