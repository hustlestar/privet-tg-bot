"""Script to check database health and pgvector extension status."""

import asyncio
import json
from telegram_bot_template.config.settings import BotConfig
from telegram_bot_template.core.database_health import DatabaseHealthChecker


async def main():
    """Check database health and pgvector status."""
    print("🏥 Database Health Check")
    print("=" * 60)
    
    # Load configuration
    config = BotConfig.from_env()
    
    # Initialize health checker
    health_checker = DatabaseHealthChecker(config.database_url)
    
    # Run comprehensive health check
    print("\n📊 Running comprehensive health check...")
    health_report = await health_checker.comprehensive_health_check()
    
    # Display results
    print("\n📋 Health Report:")
    print("-" * 40)
    
    # Connection status
    connection_status = health_report.get("connection", {}).get("status", "unknown")
    if connection_status == "ok":
        print("✅ Database Connection: OK")
    else:
        print("❌ Database Connection: FAILED")
        print("   Cannot proceed with further checks")
        return
    
    # Database info
    db_info = health_report.get("database_info", {})
    if "error" not in db_info:
        print(f"\n📦 Database Information:")
        print(f"   PostgreSQL Version: {db_info.get('postgresql_version', 'Unknown')[:50]}...")
        print(f"   Database Size: {db_info.get('database_size', 'Unknown')}")
        print(f"   Table Count: {db_info.get('table_count', 0)}")
    
    # Extension status
    print(f"\n🔌 Extension Status:")
    extensions = health_report.get("extensions", {})
    
    if "vector" in extensions:
        vector_ext = extensions["vector"]
        if vector_ext.get("installed"):
            print(f"   ✅ pgvector: Installed (version {vector_ext.get('version', 'unknown')})")
        else:
            print(f"   ❌ pgvector: Not Installed")
            print(f"      Attempting to install pgvector extension...")
            
            # Try to install the extension
            success = await health_checker.ensure_extensions()
            if success:
                print(f"      ✅ pgvector extension installed successfully!")
            else:
                print(f"      ❌ Failed to install pgvector extension")
                print(f"      You may need to install it manually:")
                print(f"      1. Install pgvector in PostgreSQL")
                print(f"      2. Run: CREATE EXTENSION vector;")
    
    # Migration status
    print(f"\n🔄 Migration Status:")
    migrations = health_report.get("migrations", {})
    if "error" not in migrations:
        current = migrations.get("current_revision", "unknown")
        head = migrations.get("head_revision", "unknown")
        has_pending = migrations.get("has_pending", False)
        
        if has_pending:
            print(f"   ⚠️  Pending migrations detected!")
            print(f"   Current: {current}")
            print(f"   Head: {head}")
            print(f"   Run migrations to update the database")
        else:
            print(f"   ✅ Database is up to date")
            print(f"   Current revision: {current}")
    else:
        print(f"   ❌ Error checking migrations: {migrations.get('error')}")
    
    # Overall status
    print(f"\n🎯 Overall Status: ", end="")
    overall = health_report.get("overall_status", "unknown")
    if overall == "healthy":
        print("✅ HEALTHY")
    elif overall == "warning":
        print("⚠️  WARNING - Some issues need attention")
    else:
        print("❌ UNHEALTHY")
    
    # Save detailed report
    report_file = "database_health_report.json"
    with open(report_file, "w") as f:
        json.dump(health_report, f, indent=2, default=str)
    print(f"\n📄 Detailed report saved to: {report_file}")
    
    print("\n" + "=" * 60)
    print("✨ Health check complete!")


if __name__ == "__main__":
    asyncio.run(main())