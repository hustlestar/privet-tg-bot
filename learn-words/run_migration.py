#!/usr/bin/env python3
"""Migration runner and bot starter for the Learn Words bot."""

import asyncio
import asyncpg
import sys
import os
from dotenv import load_dotenv
import logging

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.bot import main as bot_main
from src.dao.database_migration_manager import DatabaseMigrationManager

# Load environment variables
load_dotenv()
logger = logging.getLogger(__name__)


async def main():
    """Run all migrations and then start the bot."""

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("Error: DATABASE_URL environment variable not set")
        sys.exit(1)

    try:
        print("Connecting to the database...")
        conn = await asyncpg.connect(database_url)

        # Run migrations
        print("Running database migrations...")
        migration_manager = DatabaseMigrationManager()
        await migration_manager._run_all_migrations(conn)
        print("✓ Database migrations completed successfully")

        await conn.close()

        # Start the bot
        print("Starting the bot...")
        await bot_main()

    except Exception as e:
        print(f"Error during startup: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
