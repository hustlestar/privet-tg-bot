"""Health monitoring system that reports to maintainer."""

import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any

from telegram.ext import Application

from telegram_bot_template.config.settings import BotConfig
from telegram_bot_template.core.database_health import DatabaseHealthChecker
from telegram_bot_template.dao.user_dao import UserDAO

logger = logging.getLogger(__name__)


class HealthMonitor:
    """Monitors bot health and reports to maintainer."""

    def __init__(
        self,
        config: BotConfig,
        app: Application,
        database_url: str,
        user_dao: UserDAO,
    ):
        """Initialize health monitor.
        
        Args:
            config: Bot configuration
            app: Telegram application instance
            database_url: Database connection URL
            user_dao: User DAO for statistics
        """
        self.config = config
        self.app = app
        self.database_url = database_url
        self.user_dao = user_dao
        self.health_checker = DatabaseHealthChecker(database_url)
        self.monitoring_task: Optional[asyncio.Task] = None
        self.startup_time = datetime.now()
        self.message_count = 0
        self.error_count = 0

    async def start_monitoring(self, interval_hours: float = 24.0):
        """Start periodic health monitoring.
        
        Args:
            interval_hours: Hours between health reports
        """
        if self.monitoring_task:
            logger.warning("Health monitoring already running")
            return
        
        self.monitoring_task = asyncio.create_task(
            self._monitoring_loop(interval_hours)
        )
        logger.info(f"Health monitoring started (interval: {interval_hours} hours)")

    async def stop_monitoring(self):
        """Stop health monitoring."""
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
            self.monitoring_task = None
            logger.info("Health monitoring stopped")

    async def _monitoring_loop(self, interval_hours: float):
        """Main monitoring loop."""
        interval_seconds = interval_hours * 3600
        
        while True:
            try:
                await asyncio.sleep(interval_seconds)
                await self.send_health_report()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health monitoring: {e}")

    async def send_health_report(self):
        """Send comprehensive health report to maintainer."""
        if not self.config.MAINTAINER_CHAT_ID:
            return
        
        try:
            # Gather health data
            health_data = await self._gather_health_data()
            
            # Format report
            report = self._format_health_report(health_data)
            
            # Send to maintainer
            await self.app.bot.send_message(
                chat_id=self.config.MAINTAINER_CHAT_ID,
                text=report,
                parse_mode='Markdown'
            )
            
            logger.info("Health report sent to maintainer")
            
        except Exception as e:
            logger.error(f"Failed to send health report: {e}")

    async def _gather_health_data(self) -> Dict[str, Any]:
        """Gather all health-related data."""
        data = {
            "timestamp": datetime.now(),
            "uptime": datetime.now() - self.startup_time,
            "message_count": self.message_count,
            "error_count": self.error_count,
        }
        
        # Database health
        try:
            db_connected = await self.health_checker.check_connection()
            data["database_status"] = "connected" if db_connected else "disconnected"
            
            if db_connected:
                # Get user statistics
                stats = await self.user_dao.get_stats()
                data["total_users"] = stats.get("total_users", 0)
                data["active_users_24h"] = stats.get("active_users_24h", 0)
                
                # Check extensions
                extensions = await self.health_checker.check_extensions()
                data["pgvector_status"] = "installed" if extensions.get("vector", {}).get("installed") else "missing"
        except Exception as e:
            logger.error(f"Error gathering database health: {e}")
            data["database_status"] = "error"
        
        return data

    def _format_health_report(self, data: Dict[str, Any]) -> str:
        """Format health data into readable report."""
        report = f"📊 **Health Report - {self.config.bot_name}**\n\n"
        
        # Uptime
        uptime = data.get("uptime")
        if uptime:
            days = uptime.days
            hours = uptime.seconds // 3600
            minutes = (uptime.seconds % 3600) // 60
            report += f"⏱️ **Uptime:** {days}d {hours}h {minutes}m\n"
        
        # Database
        db_status = data.get("database_status", "unknown")
        db_emoji = "✅" if db_status == "connected" else "❌"
        report += f"{db_emoji} **Database:** {db_status}\n"
        
        # pgvector
        pgvector_status = data.get("pgvector_status", "unknown")
        pgv_emoji = "✅" if pgvector_status == "installed" else "⚠️"
        report += f"{pgv_emoji} **pgvector:** {pgvector_status}\n\n"
        
        # Statistics
        report += "📈 **Statistics:**\n"
        report += f"• Total Users: {data.get('total_users', 0)}\n"
        report += f"• Active (24h): {data.get('active_users_24h', 0)}\n"
        report += f"• Messages Processed: {data.get('message_count', 0)}\n"
        report += f"• Errors: {data.get('error_count', 0)}\n\n"
        
        # Status
        if data.get("error_count", 0) > 10:
            report += "⚠️ **Status:** High error rate detected\n"
        elif db_status != "connected":
            report += "❌ **Status:** Database issues detected\n"
        else:
            report += "✅ **Status:** All systems operational\n"
        
        report += f"\n_Report generated at {data.get('timestamp', datetime.now()).strftime('%Y-%m-%d %H:%M:%S')}_"
        
        return report

    def increment_message_count(self):
        """Increment processed message counter."""
        self.message_count += 1

    def increment_error_count(self):
        """Increment error counter."""
        self.error_count += 1

    async def send_critical_alert(self, message: str):
        """Send critical alert to maintainer immediately."""
        if not self.config.MAINTAINER_CHAT_ID:
            return
        
        try:
            alert = f"🚨 **CRITICAL ALERT**\n\n{message}\n\n_Bot: {self.config.bot_name}_"
            
            await self.app.bot.send_message(
                chat_id=self.config.MAINTAINER_CHAT_ID,
                text=alert,
                parse_mode='Markdown'
            )
            
            logger.info("Critical alert sent to maintainer")
            
        except Exception as e:
            logger.error(f"Failed to send critical alert: {e}")