# AI-Powered Grammar Generation Workflow

## Overview

This system uses AI to automatically generate comprehensive grammar rules for language learning, with proper CEFR level classification and personalized recommendations.

## Architecture

### Components

1. **GrammarRuleGenerator** - AI-powered content generation service
2. **GrammarRepository** - Database access layer
3. **API Endpoints** - RESTful interface for generation and access
4. **CLI Tool** - Command-line seeding script

### CEFR Level Classification

The system uses the Common European Framework of Reference (CEFR) levels:

| Level | Name | Description | Grammar Complexity |
|-------|------|-------------|-------------------|
| **A1** | Beginner | Basic expressions and simple sentences | Present tense, basic articles, simple pronouns |
| **A2** | Elementary | Simple everyday situations | Past tense, basic comparatives, simple conjunctions |
| **B1** | Intermediate | Main points on familiar topics | Future tense, conditionals, subjunctive basics |
| **B2** | Upper Intermediate | Complex texts and abstract topics | Advanced tenses, complex conditionals, passive voice |
| **C1** | Advanced | Sophisticated language use | Nuanced grammar, idiomatic expressions, advanced subjunctive |
| **C2** | Mastery | Native-like proficiency | All grammatical structures, subtle distinctions |

### Grammar Categories

Categories are prioritized for learning progression:

1. **Verbs** (Priority 1) - 8 subcategories
   - present_tense, past_tense, future_tense, conditional
   - subjunctive, imperative, progressive, perfect_tenses

2. **Nouns** (Priority 2) - 5 subcategories
   - gender, number, articles, diminutives, augmentatives

3. **Pronouns** (Priority 3) - 6 subcategories
   - personal, possessive, demonstrative, relative, reflexive, object_pronouns

4. **Adjectives** (Priority 4) - 4 subcategories
   - agreement, position, comparatives, superlatives

5. **Prepositions** (Priority 5) - 4 subcategories
   - location, time, direction, compound_prepositions

6. **Adverbs** (Priority 6) - 4 subcategories
   - manner, time, frequency, degree

7. **Sentence Structure** (Priority 7) - 5 subcategories
   - word_order, questions, negation, complex_sentences, clauses

**Total Possible Rules**: ~200 per language (36 subcategories × 6 levels = 216)

## Workflow Options

### 1. API-Based Generation (Programmatic)

#### Generate Single Rule

```bash
curl -X POST "http://localhost:8000/api/v1/grammar/generate/rule" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-key" \
  -d '{
    "language": "es",
    "category": "verbs",
    "subcategory": "present_tense",
    "difficulty_level": "A1",
    "native_language": "en"
  }'
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "rule_code": "es_verbs_present_tense_a1",
    "title_en": "Present Tense: Regular -AR Verbs",
    "description_en": "Comprehensive explanation...",
    "examples": [
      {
        "es": "Yo hablo español",
        "en": "I speak Spanish",
        "explanation_en": "Regular -AR verb conjugation..."
      }
    ]
  },
  "message": "Grammar rule generated successfully"
}
```

#### Generate Entire Category

```bash
curl -X POST "http://localhost:8000/api/v1/grammar/generate/category" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-key" \
  -d '{
    "language": "es",
    "category": "verbs",
    "difficulty_levels": ["A1", "A2"],
    "native_language": "en"
  }'
```

**Time**: ~5-10 minutes for one category at 2 levels
**Cost**: ~$2-5 in AI API credits

**Response**:
```json
{
  "success": true,
  "data": {
    "category": "verbs",
    "language": "es",
    "total_attempted": 16,
    "total_created": 14,
    "total_skipped": 2,
    "total_failed": 0
  }
}
```

#### Generate Complete Library

```bash
curl -X POST "http://localhost:8000/api/v1/grammar/generate/library" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-key" \
  -d '{
    "language": "es",
    "native_language": "en",
    "categories": ["verbs", "nouns"],
    "difficulty_levels": ["A1", "A2"]
  }'
```

**Time**: 30-60 minutes for full library
**Cost**: $20-50 in AI API credits

⚠️ **WARNING**: This is resource-intensive. Use targeted generation instead.

### 2. CLI-Based Generation (Recommended)

The CLI tool provides a user-friendly interface with pre-defined packs:

#### Starter Pack (Recommended for New Languages)

```bash
python scripts/seed_grammar.py --language es --starter
```

**Includes**:
- Categories: verbs, nouns, pronouns, adjectives
- Levels: A1, A2
- Total rules: ~48 rules
- Time: ~10 minutes
- Cost: ~$5

**Use case**: Essential grammar for beginners

#### Intermediate Pack

```bash
python scripts/seed_grammar.py --language es --intermediate
```

**Includes**:
- Categories: verbs, nouns, pronouns, adjectives, prepositions
- Levels: B1, B2
- Total rules: ~60 rules
- Time: ~15 minutes
- Cost: ~$8

#### Advanced Pack

```bash
python scripts/seed_grammar.py --language es --advanced
```

**Includes**:
- Categories: ALL
- Levels: C1, C2
- Total rules: ~72 rules
- Time: ~20 minutes
- Cost: ~$10

#### Custom Generation

```bash
# Generate specific categories and levels
python scripts/seed_grammar.py \
  --language es \
  --categories verbs nouns \
  --levels A1 A2 B1
```

#### List Existing Rules

```bash
python scripts/seed_grammar.py --language es --list
```

**Output**:
```
📚 Existing Grammar Rules for ES
============================================================

VERBS:
  A1: 8 rules
  A2: 8 rules
  B1: 5 rules

NOUNS:
  A1: 5 rules
  A2: 5 rules

Total: 31 rules
============================================================
```

### 3. Gradual Generation (Best Practice)

For cost-effectiveness and quality control:

```bash
# Week 1: Start with essentials
python scripts/seed_grammar.py --language es --starter

# Week 2: Add intermediate content as users progress
python scripts/seed_grammar.py --language es \
  --categories verbs \
  --levels B1 B2

# Week 3: Expand to other categories
python scripts/seed_grammar.py --language es \
  --categories prepositions adverbs \
  --levels A1 A2 B1

# Week 4: Add advanced content
python scripts/seed_grammar.py --language es --advanced
```

## AI Generation Process

### 1. Prompt Construction

For each rule, the system builds a comprehensive prompt:

```
Generate a comprehensive grammar rule for Spanish language learning.

**Target Audience**: A1 (Beginner) level learners
**Category**: verbs
**Topic**: present_tense

Please provide the grammar rule in JSON format with:
- Multi-language titles (en, es, ru)
- Comprehensive descriptions (3-5 paragraphs)
- 5-8 practical examples with translations
- Searchable tags
- Related rule suggestions
```

### 2. AI Processing

- Model: OpenRouter (default: Claude Sonnet)
- Temperature: 0.7 for creativity while maintaining accuracy
- Max tokens: 4000 for comprehensive responses

### 3. Response Parsing

The system:
1. Extracts JSON from AI response
2. Validates required fields
3. Normalizes example structures
4. Generates unique rule code

### 4. Database Storage

Stores in `grammar_rules` table with:
- Indexed by language, category, difficulty
- JSONB examples for flexible structure
- ARRAY tags for searchability
- Multi-language support

### 5. Quality Checks

- **Validation**: Ensures all required fields present
- **Uniqueness**: Prevents duplicate rules
- **Difficulty**: Validates appropriate for CEFR level
- **Examples**: Verifies translations present

## Personalized Recommendations

### GET /grammar/recommend/{user_id}

Returns grammar rules tailored to user's level:

```bash
curl "http://localhost:8000/api/v1/grammar/recommend/1?language=es&limit=10" \
  -H "X-API-Key: your-key"
```

**Algorithm**:

1. **Determine User Level**
   - Checks `user_language_settings` for proficiency level
   - Falls back to `user_progress` total XP
   - Default: A1

2. **Select Rules**
   - Current level: 60% of recommendations
   - Next level: 40% of recommendations
   - Prioritized by category importance

3. **Filter**
   - Exclude already mastered rules
   - Prioritize unreviewed rules
   - Consider recent learning patterns

**Example Response**:
```json
{
  "success": true,
  "data": {
    "recommendations": [
      {
        "rule_code": "es_verbs_present_tense_a1",
        "title_en": "Present Tense: Regular -AR Verbs",
        "difficulty_level": "A1",
        "category": "verbs",
        "reason": "Essential for your current level"
      },
      ...
    ]
  }
}
```

## Integration with Learning Flow

### 1. Onboarding

When user starts learning a language:

```python
# 1. Check if grammar library exists
rules = await grammar_repo.get_rules_by_language(
    language="es",
    difficulty_level="A1",
    limit=1
)

# 2. If not, trigger generation
if not rules:
    # Generate starter pack asynchronously
    await generator.generate_category_rules(
        language="es",
        category="verbs",
        difficulty_levels=["A1"]
    )
```

### 2. Lesson Planning

```python
# Get recommended rules for user
recommendations = await generator.get_recommended_rules(
    user_id=user_id,
    language="es",
    limit=5
)

# Present in chat or lesson UI
for rule in recommendations:
    display_grammar_lesson(rule)
```

### 3. Contextual Help

During conversation, reference relevant grammar:

```python
# User makes grammar mistake
if detected_error.type == "verb_conjugation":
    # Find relevant rule
    rule = await grammar_repo.get_rule_by_code(
        "es_verbs_present_tense_a1"
    )

    # Show inline explanation
    show_grammar_hint(rule)
```

### 4. Progress Tracking

```python
# After user completes grammar practice
await progress_repo.add_xp(
    user_id=user_id,
    xp_amount=10,
    activity_type="grammar"
)

# Award achievement
if user_completed_category:
    await progress_repo.award_achievement(
        user_id=user_id,
        achievement_code="grammar_master_verbs_a1"
    )
```

## Cost Optimization

### Token Usage per Rule

- Prompt: ~500 tokens
- Response: ~2000 tokens
- Total: ~2500 tokens per rule

### Cost Estimates

Using Claude Sonnet (via OpenRouter):
- Input: $3 per 1M tokens
- Output: $15 per 1M tokens

**Per Rule**:
- Input: 500 tokens × $3/1M = $0.0015
- Output: 2000 tokens × $15/1M = $0.03
- **Total**: ~$0.032 per rule

**Packs**:
- Starter (48 rules): ~$1.50
- Intermediate (60 rules): ~$2.00
- Advanced (72 rules): ~$2.30
- **Full library (216 rules)**: ~$7.00

### Optimization Strategies

1. **Cache Generated Rules**
   - Store in database permanently
   - No regeneration needed
   - One-time cost per rule

2. **Batch Generation**
   - Generate during off-peak hours
   - Use cheaper models for drafts
   - Human review for quality

3. **Incremental Expansion**
   - Start with A1-A2 only
   - Add levels as users progress
   - Generate on-demand for less common categories

4. **Quality Over Quantity**
   - 50 excellent rules > 200 mediocre rules
   - Focus on high-priority categories
   - User feedback for improvements

## Quality Assurance

### Automated Checks

1. **Structure Validation**
   - Required fields present
   - JSON format valid
   - Examples have translations

2. **Content Validation**
   - Title length appropriate
   - Description comprehensive (>200 chars)
   - Minimum 5 examples

3. **Difficulty Validation**
   - Examples appropriate for level
   - Complexity matches CEFR

### Manual Review Process

```bash
# 1. Generate rules
python scripts/seed_grammar.py --language es --starter

# 2. Export for review
python scripts/export_grammar.py --language es --output grammar_review.json

# 3. Review and edit in spreadsheet/editor

# 4. Re-import edited rules
python scripts/import_grammar.py --input grammar_review_edited.json
```

### Continuous Improvement

- Track user engagement with rules
- Identify confusing explanations
- Update examples based on feedback
- A/B test different explanations

## Monitoring

### Key Metrics

```python
# Get generation stats
stats = await grammar_repo.get_stats()

# {
#   "total_rules": 150,
#   "by_language": {
#     "es": 100,
#     "ru": 30,
#     "en": 20
#   },
#   "by_level": {
#     "A1": 30,
#     "A2": 25,
#     ...
#   },
#   "by_category": {
#     "verbs": 40,
#     "nouns": 25,
#     ...
#   }
# }
```

### API Endpoint for Metadata

```bash
curl "http://localhost:8000/api/v1/grammar/metadata" \
  -H "X-API-Key: your-key"
```

Returns:
- CEFR level definitions
- Category structures
- Subcategory lists
- Estimated rule counts

## Best Practices

### 1. Start Small

```bash
# Don't do this on day 1:
python scripts/seed_grammar.py --language es --full

# Do this instead:
python scripts/seed_grammar.py --language es --starter
```

### 2. Monitor Costs

```python
# Track API usage
from privet_api.repositories.api_usage_repository import APIUsageRepository

usage_repo = APIUsageRepository(pool)
total_cost = await usage_repo.get_total_cost()

if total_cost > budget_limit:
    pause_generation()
```

### 3. Quality Over Completeness

- Generate A1-A2 completely before moving to B1-B2
- Verify rules work well in practice
- Get user feedback
- Iterate on quality

### 4. Cache Everything

- Rules are generated once, used forever
- No need to regenerate
- Focus on creating high-quality initial content

### 5. Localize Thoughtfully

- Generate descriptions in user's native language
- Provide examples with accurate translations
- Consider cultural context

## Troubleshooting

### Issue: AI returns invalid JSON

**Solution**: The parser handles markdown code blocks. If still failing:
1. Check AI provider temperature (lower = more consistent)
2. Verify prompt format
3. Add retry logic with exponential backoff

### Issue: Rules already exist

**Solution**: This is normal behavior
- System skips existing rules
- Check with `--list` flag first
- No duplicate charges

### Issue: Generation too slow

**Solution**:
- Use parallel generation (careful with rate limits)
- Lower retry attempts
- Use faster AI model for drafts

### Issue: High API costs

**Solution**:
- Start with starter pack only
- Generate during off-peak hours
- Use cheaper models (GPT-3.5) for initial generation
- Human review before expensive model polish

## Future Enhancements

- [ ] Grammar rule versioning
- [ ] User-contributed examples
- [ ] Automated difficulty assessment
- [ ] Rule prerequisite chains
- [ ] Interactive grammar exercises
- [ ] Voice examples for pronunciation
- [ ] Video explanations
- [ ] Cultural context notes
- [ ] Common mistake patterns
- [ ] Rule effectiveness analytics

## Support

For issues or questions:
- Check API docs: http://localhost:8000/docs
- Review logs: `privet_api/logs/`
- Test endpoints: Use `/grammar/metadata` for structure info
