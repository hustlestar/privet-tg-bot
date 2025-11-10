"""Database health check and extension management utilities."""

import asyncio
import logging
from typing import Dict, Any, List
import asyncpg
from .migration_manager import MigrationManager

logger = logging.getLogger(__name__)


class DatabaseHealthChecker:
    """Utility class for database health checks and extension management."""

    def __init__(self, database_url: str):
        """Initialize the health checker.
        
        Args:
            database_url: PostgreSQL database connection URL
        """
        self.database_url = database_url
        # Convert to asyncpg compatible URL
        if "postgresql+asyncpg://" in self.database_url:
            self.database_url = self.database_url.replace("postgresql+asyncpg://", "postgresql://")

    async def check_connection(self) -> bool:
        """Check if database connection is working.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            conn = await asyncpg.connect(self.database_url)
            await conn.execute("SELECT 1")
            await conn.close()
            logger.info("Database connection check passed")
            return True
        except Exception as e:
            logger.error(f"Database connection check failed: {e}")
            return False

    async def check_extensions(self) -> Dict[str, Any]:
        """Check status of required database extensions.
        
        Returns:
            Dictionary with extension status information
        """
        required_extensions = ["vector"]
        extension_status = {}
        
        try:
            conn = await asyncpg.connect(self.database_url)
            
            for ext_name in required_extensions:
                try:
                    result = await conn.fetch(
                        "SELECT * FROM pg_extension WHERE extname = $1", ext_name
                    )
                    if result:
                        extension_status[ext_name] = {
                            "installed": True,
                            "version": result[0]["extversion"],
                            "details": dict(result[0])
                        }
                    else:
                        extension_status[ext_name] = {
                            "installed": False,
                            "version": None,
                            "details": None
                        }
                except Exception as e:
                    extension_status[ext_name] = {
                        "installed": False,
                        "version": None,
                        "error": str(e)
                    }
            
            await conn.close()
            
        except Exception as e:
            logger.error(f"Failed to check extensions: {e}")
            return {"error": str(e)}
        
        return extension_status

    async def ensure_extensions(self) -> bool:
        """Ensure all required extensions are installed.
        
        Returns:
            True if all extensions are available, False otherwise
        """
        try:
            conn = await asyncpg.connect(self.database_url)
            
            # Enable pgvector extension
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            logger.info("pgvector extension ensured")
            
            await conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Failed to ensure extensions: {e}")
            return False

    async def get_database_info(self) -> Dict[str, Any]:
        """Get comprehensive database information.
        
        Returns:
            Dictionary with database information
        """
        try:
            conn = await asyncpg.connect(self.database_url)
            
            # Get PostgreSQL version
            version_result = await conn.fetchrow("SELECT version()")
            pg_version = version_result["version"] if version_result else "Unknown"
            
            # Get database size
            db_name = self.database_url.split("/")[-1].split("?")[0]
            size_result = await conn.fetchrow(
                "SELECT pg_size_pretty(pg_database_size($1)) as size", db_name
            )
            db_size = size_result["size"] if size_result else "Unknown"
            
            # Get table count
            table_count_result = await conn.fetchrow(
                "SELECT count(*) as count FROM information_schema.tables WHERE table_schema = 'public'"
            )
            table_count = table_count_result["count"] if table_count_result else 0
            
            await conn.close()
            
            return {
                "postgresql_version": pg_version,
                "database_size": db_size,
                "table_count": table_count,
                "connection_url": self.database_url.split("@")[1] if "@" in self.database_url else "Unknown"
            }
            
        except Exception as e:
            logger.error(f"Failed to get database info: {e}")
            return {"error": str(e)}

    async def comprehensive_health_check(self) -> Dict[str, Any]:
        """Perform a comprehensive health check.
        
        Returns:
            Dictionary with complete health check results
        """
        health_report = {
            "timestamp": asyncio.get_event_loop().time(),
            "overall_status": "unknown"
        }
        
        # Check connection
        connection_ok = await self.check_connection()
        health_report["connection"] = {"status": "ok" if connection_ok else "failed"}
        
        if not connection_ok:
            health_report["overall_status"] = "failed"
            return health_report
        
        # Check extensions
        extensions = await self.check_extensions()
        health_report["extensions"] = extensions
        
        # Check database info
        db_info = await self.get_database_info()
        health_report["database_info"] = db_info
        
        # Check migration status
        try:
            migration_manager = MigrationManager(self.database_url)
            current_rev = await migration_manager.get_current_revision()
            head_rev = migration_manager.get_head_revision()
            has_pending = await migration_manager.has_pending_migrations()
            
            health_report["migrations"] = {
                "current_revision": current_rev,
                "head_revision": head_rev,
                "has_pending": has_pending,
                "status": "up_to_date" if not has_pending else "pending"
            }
        except Exception as e:
            health_report["migrations"] = {"error": str(e)}
        
        # Determine overall status
        extension_issues = any(
            not ext.get("installed", False) for ext in extensions.values() 
            if isinstance(ext, dict) and "installed" in ext
        )
        migration_issues = health_report["migrations"].get("has_pending", False)
        
        if extension_issues or migration_issues:
            health_report["overall_status"] = "warning"
        else:
            health_report["overall_status"] = "healthy"
        
        return health_report