"""Grammar rules table definition for language learning."""

from sqlalchemy import (
    Table,
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Boolean,
    Index,
)
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.sql import func

from .base import metadata

grammar_rules_table = Table(
    "grammar_rules",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("rule_code", String(100), nullable=False, unique=True, comment="Unique identifier for the rule"),
    Column("language", String(10), nullable=False, comment="Language code (es, en, ru)"),
    Column("category", String(100), nullable=False, comment="Grammar category (verbs, tenses, pronouns, etc.)"),
    Column("difficulty_level", String(10), nullable=False, comment="CEFR level (A1, A2, B1, B2, C1, C2)"),

    # Multi-language content
    Column("title_en", String(255), nullable=False, comment="Rule title in English"),
    Column("title_es", String(255), nullable=True, comment="Rule title in Spanish"),
    Column("title_ru", String(255), nullable=True, comment="Rule title in Russian"),

    Column("description_en", Text, nullable=False, comment="Rule description in English"),
    Column("description_es", Text, nullable=True, comment="Rule description in Spanish"),
    Column("description_ru", Text, nullable=True, comment="Rule description in Russian"),

    # Examples with translations
    Column("examples", JSONB, nullable=True, comment="Array of example objects with translations"),

    # Additional metadata
    Column("tags", ARRAY(String), nullable=True, comment="Searchable tags"),
    Column("related_rules", ARRAY(String), nullable=True, comment="Array of related rule codes"),
    Column("order_index", Integer, nullable=False, default=0, comment="Order for curriculum"),
    Column("is_active", Boolean, nullable=False, default=True, server_default="true"),

    Column(
        "created_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
    ),
    Column(
        "updated_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    ),
)

# Indexes for efficient queries
grammar_language_idx = Index("idx_grammar_language", grammar_rules_table.c.language)
grammar_category_idx = Index("idx_grammar_category", grammar_rules_table.c.category)
grammar_difficulty_idx = Index("idx_grammar_difficulty", grammar_rules_table.c.difficulty_level)
grammar_code_idx = Index("idx_grammar_code", grammar_rules_table.c.rule_code, unique=True)
