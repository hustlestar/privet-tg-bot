"""Command-line interface for the Telegram bot template.

This module provides CLI commands for database migration management
and other administrative tasks.
"""

import asyncio
import logging
import sys
from pathlib import Path

import click
from dotenv import load_dotenv

from .config.settings import BotConfig
from .core.migration_manager import MigrationManager
from .core.database_health import DatabaseHealthChecker

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def cli(verbose: bool):
    """Telegram Bot Template CLI."""
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)


@cli.group()
def db():
    """Database management commands."""
    pass


@db.command()
@click.option("--message", "-m", required=True, help="Migration description")
@click.option("--autogenerate/--no-autogenerate", default=True, help="Auto-generate migration from model changes")
def revision(message: str, autogenerate: bool):
    """Create a new migration revision."""
    async def _revision():
        try:
            config = BotConfig.from_env()
            migration_manager = MigrationManager(config.database_url)

            revision_id = await migration_manager.create_migration(message, autogenerate)
            click.echo(f"Created migration revision: {revision_id}")

        except Exception as e:
            click.echo(f"Error creating migration: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_revision())


@db.command()
@click.option("--target", "-t", default="head", help="Target revision (default: head)")
def upgrade(target: str):
    """Apply migrations to upgrade the database."""
    async def _upgrade():
        try:
            config = BotConfig.from_env()
            migration_manager = MigrationManager(config.database_url)

            current = await migration_manager.get_current_revision()
            click.echo(f"Current revision: {current}")

            if await migration_manager.apply_migrations(target):
                new_revision = await migration_manager.get_current_revision()
                click.echo(f"Successfully upgraded to revision: {new_revision}")
            else:
                click.echo("Migration failed", err=True)
                sys.exit(1)

        except Exception as e:
            click.echo(f"Error applying migrations: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_upgrade())


@db.command()
@click.option("--target", "-t", default="-1", help="Target revision (default: -1 for previous)")
def downgrade(target: str):
    """Rollback migrations to downgrade the database."""
    async def _downgrade():
        try:
            config = BotConfig.from_env()
            migration_manager = MigrationManager(config.database_url)

            current = await migration_manager.get_current_revision()
            click.echo(f"Current revision: {current}")

            if await migration_manager.rollback_migration(target):
                new_revision = await migration_manager.get_current_revision()
                click.echo(f"Successfully downgraded to revision: {new_revision}")
            else:
                click.echo("Rollback failed", err=True)
                sys.exit(1)

        except Exception as e:
            click.echo(f"Error rolling back migrations: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_downgrade())


@db.command()
def current():
    """Show current migration revision."""
    async def _current():
        try:
            config = BotConfig.from_env()
            migration_manager = MigrationManager(config.database_url)

            current = await migration_manager.get_current_revision()
            head = migration_manager.get_head_revision()

            click.echo(f"Current revision: {current}")
            click.echo(f"Head revision: {head}")

            if await migration_manager.has_pending_migrations():
                click.echo("⚠️  Pending migrations detected!")
            else:
                click.echo("✅ Database is up to date")

        except Exception as e:
            click.echo(f"Error checking migration status: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_current())


@db.command()
def history():
    """Show migration history."""
    async def _history():
        try:
            config = BotConfig.from_env()
            migration_manager = MigrationManager(config.database_url)

            history = await migration_manager.get_migration_history()

            if not history:
                click.echo("No migrations found")
                return

            click.echo("Migration History:")
            click.echo("-" * 50)

            for migration in history:
                status = "✅ CURRENT" if migration["is_current"] else ""
                click.echo(f"{migration['revision']}: {migration['description']} {status}")

        except Exception as e:
            click.echo(f"Error getting migration history: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_history())


@db.command()
@click.option("--revision", "-r", default="head", help="Revision to stamp (default: head)")
def stamp(revision: str):
    """Stamp the database with a specific revision without running migrations."""
    async def _stamp():
        try:
            config = BotConfig.from_env()
            migration_manager = MigrationManager(config.database_url)

            if await migration_manager.stamp_database(revision):
                click.echo(f"Successfully stamped database with revision: {revision}")
            else:
                click.echo("Stamp operation failed", err=True)
                sys.exit(1)

        except Exception as e:
            click.echo(f"Error stamping database: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_stamp())


@db.command()
def status():
    """Show detailed database and migration status."""
    async def _status():
        try:
            config = BotConfig.from_env()
            migration_manager = MigrationManager(config.database_url)

            current = await migration_manager.get_current_revision()
            head = migration_manager.get_head_revision()
            has_pending = await migration_manager.has_pending_migrations()

            click.echo("Database Status:")
            click.echo("-" * 30)
            click.echo(f"Database URL: {config.database_url}")
            click.echo(f"Current revision: {current or 'None'}")
            click.echo(f"Head revision: {head or 'None'}")
            click.echo(f"Pending migrations: {'Yes' if has_pending else 'No'}")

            if has_pending:
                click.echo("\n⚠️  Run 'telegram-bot-template db upgrade' to apply pending migrations")
            else:
                click.echo("\n✅ Database is up to date")

        except Exception as e:
            click.echo(f"Error checking database status: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_status())


@db.command()
def health():
    """Perform comprehensive database health check."""
    async def _health():
        try:
            config = BotConfig.from_env()
            health_checker = DatabaseHealthChecker(config.database_url)

            click.echo("🔍 Performing comprehensive database health check...")
            health_report = await health_checker.comprehensive_health_check()

            # Display results
            status_emoji = {
                "healthy": "✅",
                "warning": "⚠️",
                "failed": "❌",
                "unknown": "❓"
            }

            overall_status = health_report.get("overall_status", "unknown")
            click.echo(f"\n{status_emoji.get(overall_status, '❓')} Overall Status: {overall_status.upper()}")
            click.echo("=" * 50)

            # Connection status
            conn_status = health_report.get("connection", {}).get("status", "unknown")
            click.echo(f"🔗 Connection: {status_emoji.get(conn_status, '❓')} {conn_status}")

            # Database info
            db_info = health_report.get("database_info", {})
            if "error" not in db_info:
                click.echo(f"🗄️  Database Info:")
                click.echo(f"   • PostgreSQL Version: {db_info.get('postgresql_version', 'Unknown')}")
                click.echo(f"   • Database Size: {db_info.get('database_size', 'Unknown')}")
                click.echo(f"   • Table Count: {db_info.get('table_count', 'Unknown')}")

            # Extensions
            extensions = health_report.get("extensions", {})
            if "error" not in extensions:
                click.echo(f"🔌 Extensions:")
                for ext_name, ext_info in extensions.items():
                    if isinstance(ext_info, dict):
                        installed = ext_info.get("installed", False)
                        version = ext_info.get("version", "Unknown")
                        status_icon = "✅" if installed else "❌"
                        click.echo(f"   • {ext_name}: {status_icon} {'Installed' if installed else 'Not installed'}")
                        if installed and version:
                            click.echo(f"     Version: {version}")

            # Migrations
            migrations = health_report.get("migrations", {})
            if "error" not in migrations:
                click.echo(f"🔄 Migrations:")
                current = migrations.get("current_revision", "None")
                head = migrations.get("head_revision", "None")
                has_pending = migrations.get("has_pending", False)
                click.echo(f"   • Current Revision: {current}")
                click.echo(f"   • Head Revision: {head}")
                click.echo(f"   • Status: {'⚠️  Pending migrations' if has_pending else '✅ Up to date'}")

            # Recommendations
            if overall_status == "warning":
                click.echo(f"\n💡 Recommendations:")
                if any(not ext.get("installed", False) for ext in extensions.values() if isinstance(ext, dict)):
                    click.echo("   • Install missing database extensions")
                if migrations.get("has_pending", False):
                    click.echo("   • Run 'telegram-bot-template db upgrade' to apply pending migrations")

        except Exception as e:
            click.echo(f"❌ Health check failed: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_health())


@cli.command()
def migrate():
    """Shortcut command to apply all pending migrations."""
    async def _migrate():
        try:
            config = BotConfig.from_env()
            migration_manager = MigrationManager(config.database_url)

            if not await migration_manager.has_pending_migrations():
                click.echo("✅ No pending migrations")
                return

            current = await migration_manager.get_current_revision()
            head = migration_manager.get_head_revision()

            click.echo(f"Applying migrations from {current} to {head}...")

            if await migration_manager.apply_migrations():
                click.echo("✅ All migrations applied successfully")
            else:
                click.echo("❌ Migration failed", err=True)
                sys.exit(1)

        except Exception as e:
            click.echo(f"Error applying migrations: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_migrate())


def main():
    """Main CLI entry point."""
    cli()


if __name__ == "__main__":
    main()
