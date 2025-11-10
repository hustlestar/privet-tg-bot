# Word List Generation and Database Population Scripts

This directory contains scripts for generating word lists and populating the database with translations for the Learn Words application.

## Scripts Overview

### 1. `generate_word_lists.py`
Generates lists of the most common words for supported languages from multiple sources.

### 2. `populate_database.py`
Populates the database with translations for all language pairs using the existing translation system.

## Quick Start

### Step 1: Generate Word Lists

```bash
# Generate word lists for all supported languages (5000 words each)
python scripts/generate_word_lists.py --languages english,polish,russian,spanish --count 5000

# Generate for a single language
python scripts/generate_word_lists.py --language english --count 3000

# Generate with verbose output
python scripts/generate_word_lists.py --languages english,polish --count 1000 --verbose
```

### Step 2: Populate Database

```bash
# Populate database with all language pairs
python scripts/populate_database.py --all-pairs

# Populate specific language pairs only
python scripts/populate_database.py --pairs english-polish,polish-english

# Resume from a previous interrupted run
python scripts/populate_database.py --resume

# Custom batch processing settings
python scripts/populate_database.py --all-pairs --batch-size 25 --delay 2.0
```

## Detailed Usage

### Word List Generator

The word list generator aggregates words from multiple sources:
- **NLTK corpora** (for English): Brown, Reuters, Gutenberg
- **Online frequency lists**: Hermit Dave's frequency word lists
- **Manual curated lists**: Local word files in `word_sources/`

#### Options:
- `--languages`: Comma-separated list of languages
- `--language`: Single language to process
- `--count`: Number of words to generate (default: 5000)
- `--output-dir`: Custom output directory
- `--verbose`: Enable detailed logging

#### Output:
- JSON files in `generated_lists/` directory
- Each file contains word list with metadata and statistics
- Comprehensive generation report in `reports/`

### Database Populator

The database populator processes word lists and creates translations for all language pairs:

#### Supported Language Pairs:
- English ↔ Polish
- English ↔ Russian  
- English ↔ Spanish
- Polish ↔ Russian
- Polish ↔ Spanish
- Russian ↔ Spanish

**Total: 12 translation directions**

#### Options:
- `--all-pairs`: Process all possible language pairs
- `--pairs`: Specific pairs (e.g., `english-polish,polish-english`)
- `--resume`: Resume from last checkpoint
- `--batch-size`: Words per batch (default: 50)
- `--delay`: Seconds between API calls (default: 1.0)
- `--max-retries`: Retry attempts for failed translations (default: 3)
- `--checkpoint-interval`: Save checkpoint every N words (default: 100)
- `--verbose`: Enable detailed logging

#### Features:
- **Checkpoint system**: Automatically saves progress and can resume
- **Rate limiting**: Respects API limits with configurable delays
- **Cache awareness**: Skips words that already exist in database
- **Error handling**: Robust retry logic and error reporting
- **Progress tracking**: Real-time progress with ETA calculations

## File Structure

```
scripts/
├── generate_word_lists.py      # Word list generator
├── populate_database.py        # Database populator
├── README.md                   # This file
├── word_sources/               # Source word lists
│   ├── english/
│   │   └── basic_english_850.txt
│   ├── polish/
│   │   └── polish_common_5000.txt
│   ├── russian/
│   │   └── russian_common_5000.txt
│   └── spanish/
│       └── spanish_common_5000.txt
├── generated_lists/            # Generated word lists (JSON)
├── checkpoints/                # Resume checkpoints
└── reports/                    # Execution reports and logs
```

## Performance Estimates

### Word List Generation
- **Time**: ~5-10 minutes per language
- **Output**: JSON files with 1000-5000 words each
- **Dependencies**: Internet connection for online sources

### Database Population
- **Time**: ~8-12 hours for all pairs (60,000 translations)
- **API Costs**: ~$30-50 (based on OpenAI pricing)
- **Storage**: ~500MB for complete database
- **Dependencies**: Database connection, OpenAI API access

## Error Handling

Both scripts include comprehensive error handling:

- **Logging**: Detailed logs saved to `reports/` directory
- **Checkpoints**: Automatic progress saving for resumption
- **Graceful shutdown**: Handle Ctrl+C and system signals
- **Validation**: Data quality checks and error reporting
- **Retry logic**: Automatic retries for transient failures

## Examples

### Generate Small Test Dataset
```bash
# Generate 100 words for testing
python scripts/generate_word_lists.py --language english --count 100

# Populate just English-Polish pair
python scripts/populate_database.py --pairs english-polish
```

### Full Production Run
```bash
# Step 1: Generate all word lists
python scripts/generate_word_lists.py --languages english,polish,russian,spanish --count 5000

# Step 2: Populate all language pairs
python scripts/populate_database.py --all-pairs --batch-size 50 --delay 1.0
```

### Resume Interrupted Run
```bash
# If population was interrupted, resume from checkpoint
python scripts/populate_database.py --resume
```

## Monitoring Progress

### Real-time Monitoring
- Both scripts provide real-time progress updates
- ETA calculations and performance metrics
- Success/error rates and statistics

### Log Files
- `reports/word_list_generation.log` - Word list generation logs
- `reports/database_population.log` - Database population logs
- `reports/*_report_*.txt` - Detailed execution reports

### Checkpoints
- `checkpoints/populate_*.json` - Resume data for database population
- Automatically saved every 100 words (configurable)

## Troubleshooting

### Common Issues

1. **No word lists found**
   - Run `generate_word_lists.py` first
   - Check `generated_lists/` directory for JSON files

2. **Database connection errors**
   - Verify database is running and accessible
   - Check `.env` file for correct database URL

3. **API rate limiting**
   - Increase `--delay` parameter
   - Reduce `--batch-size` parameter

4. **Out of memory**
   - Reduce batch size
   - Process fewer language pairs at once

5. **Network timeouts**
   - Check internet connection
   - Retry with `--resume` option

### Getting Help

Run scripts with `--help` for detailed usage information:
```bash
python scripts/generate_word_lists.py --help
python scripts/populate_database.py --help
```

## Integration with Application

The generated translations integrate seamlessly with the existing Learn Words application:

- **Database Schema**: Uses existing `words` table structure
- **Translation Format**: Compatible with `TranslationData` model
- **Cache System**: Leverages existing caching mechanisms
- **API Integration**: Uses existing OpenAI translation system

After running these scripts, the application will have a comprehensive database of common words with rich translation data for all supported language pairs.