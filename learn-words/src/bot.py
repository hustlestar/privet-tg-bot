"""Main Telegram bot implementation."""

import asyncio
import logging
import platform  # Added for OS check
import signal
import sys

import httpx
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

from src.handlers import MAINTAINER
from .config import get_config
from .database import db
from .handlers.callback_handlers import handle_callback_query
from .handlers.command_handlers import (
    start_command,
    train_command,
    stats_command,
    settings_command,
    explanation_command,
    vocabulary_command,
    test_notification_command
)
from .handlers.message_handlers import handle_message
from .scheduler import start_scheduler


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colored output for different log levels."""

    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[37m",  # White
        "INFO": "\033[34m",  # Blue
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[91m",  # Bright Red
    }
    RESET = "\033[0m"  # Reset color

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Check if output is to a terminal (supports colors)
        self.use_colors = hasattr(sys.stderr, "isatty") and sys.stderr.isatty()

    def format(self, record):
        if self.use_colors and record.levelname in self.COLORS:
            # Add color to the level name
            colored_levelname = f"{self.COLORS[record.levelname]}[{record.levelname}]{self.RESET}"
            # Store original levelname
            original_levelname = record.levelname
            # Temporarily replace levelname with colored version
            record.levelname = colored_levelname
            # Format the message
            formatted = super().format(record)
            # Restore original levelname
            record.levelname = original_levelname
            return formatted
        else:
            # No colors - format normally with brackets around level
            original_levelname = record.levelname
            record.levelname = f"[{record.levelname}]"
            formatted = super().format(record)
            record.levelname = original_levelname
            return formatted


def setup_logging():
    """Set up enhanced logging configuration with colors and detailed format."""
    # Create formatter
    formatter = ColoredFormatter(
        fmt="%(asctime)s %(levelname)s %(filename)s:%(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Remove any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create console handler with proper Unicode handling
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    # Configure stream to handle Unicode characters properly
    console_handler.stream.reconfigure(errors="backslashreplace")

    # Add handler to root logger
    root_logger.addHandler(console_handler)

    # Suppress httpx INFO logs
    logging.getLogger("httpx").setLevel(logging.WARNING)


# Set up enhanced logging
setup_logging()
logger = logging.getLogger(__name__)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors caused by Updates and provide detailed context."""

    # The `update` object is where the event information is stored.
    # It can be a Message, CallbackQuery, etc.
    # The `context.error` holds the exception raised.

    error_details = {
        "error": str(context.error),
        "error_type": type(context.error).__name__,
    }

    if isinstance(update, Update) and update.effective_user:
        error_details["user_id"] = update.effective_user.id
        error_details["user_name"] = update.effective_user.username or "N/A"

    if isinstance(update, Update) and update.effective_chat:
        error_details["chat_id"] = update.effective_chat.id

    if isinstance(update, Update):
        if update.message:
            error_details["update_type"] = "message"
            error_details["message_text"] = update.message.text
        elif update.callback_query:
            error_details["update_type"] = "callback_query"
            error_details["callback_data"] = update.callback_query.data

    # Use exc_info=True to log the full traceback
    logger.error(f"Exception while handling an update: {error_details}", exc_info=True)


def create_application() -> Application:
    config = get_config()
    application = Application.builder().token(config.telegram_token).build()
    application.bot_data["is_shutting_down"] = False
    application.bot_data["main_loop_stop_event"] = asyncio.Event()
    return application


def register_handlers(application):
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("train", train_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("settings", settings_command))
    application.add_handler(CommandHandler("explanation", explanation_command))
    application.add_handler(CommandHandler("vocabulary", vocabulary_command))
    application.add_handler(CommandHandler("test_notification", test_notification_command))

    application.add_handler(CallbackQueryHandler(handle_callback_query))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Add error handler
    application.add_error_handler(error_handler)


async def main() -> None:
    """Main function to run the bot."""
    application = None
    try:
        # Initialize database
        await db.connect()

        # Create and configure the bot
        application = create_application()  # bot_data flags are set here

        # `async with application` handles initialize() on entry and shutdown() (after stop()) on exit
        async with application:
            logger.info("Starting Learn Words bot...")

            # `await application.initialize()` is redundant here, handled by `async with`.
            await application.start()  # Starts core background tasks

            # Signal handler setup
            loop = asyncio.get_running_loop()

            def signal_handler_closure():
                # This closure captures the `application` instance from `main`
                logger.info("Received termination signal, initiating graceful shutdown via signal")
                if application and not application.bot_data.get("is_shutting_down", False):
                    asyncio.create_task(shutdown_gracefully(application))
                elif not application:
                    logger.warning("Signal received but application instance is None.")
                else:
                    logger.info("Signal received but shutdown already in progress.")

            await register_signal_handlers(loop, signal_handler_closure)

            register_handlers(application)
            start_scheduler(application)
            await notify_maintainer(application, "🚀 Bot has started successfully!")

            logger.info("Starting polling...")
            await application.updater.start_polling(
                drop_pending_updates=False,
                allowed_updates=Update.ALL_TYPES,
                poll_interval=0.1,
            )
            logger.info("Bot is polling. Press Ctrl+C or send signal to stop.")

            # Wait for the main_loop_stop_event to be set (e.g., by shutdown_gracefully)
            await application.bot_data["main_loop_stop_event"].wait()
            logger.info("Main loop wait completed (stop event set).")

    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received in main.")
        if application:  # Check if application object exists
            logger.info("Initiating graceful shutdown due to KeyboardInterrupt.")
            await shutdown_gracefully(application)
        else:
            logger.info("Application not initialized; KeyboardInterrupt led to simple exit.")
            if "db" in globals() and hasattr(db, "close"):  # Check if db is available
                await db.close()  # Attempt to close db if it might have been connected

    except Exception as e:
        if isinstance(e, httpx.ConnectError):
            logger.error(
                "Connection Error: Could not connect to the Telegram API. "
                "Please check your network connection and ensure that the TELEGRAM_BOT_TOKEN is correct."
            )
        else:
            logger.error(f"Unhandled error in main: {e}", exc_info=True)
        if application:  # Check if application object exists
            logger.error("Initiating graceful shutdown due to unhandled error.")
            await shutdown_gracefully(application)
        else:
            logger.error(f"Error '{e}' occurred before application fully initialized or was None.")
            if "db" in globals() and hasattr(db, "close"):
                await db.close()  # Attempt to close db if it might have been connected
    finally:
        logger.info("Main function's finally block reached.")
        if application:
            await shutdown_gracefully(application)
        else:
            logger.info("Application was not created or failed early. Ensuring DB is closed if possible.")
            if "db" in globals() and hasattr(db, "close"):
                await db.close()
        logger.info("Exiting main function.")


async def register_signal_handlers(loop, signal_handler_closure):
    if platform.system() != "Windows":
        for sig in (signal.SIGTERM, signal.SIGINT):
            try:
                loop.add_signal_handler(sig, signal_handler_closure)
            except (
                NotImplementedError,
                RuntimeError,
            ) as e:  # RuntimeError can occur on some Windows builds/Python versions
                logger.warning(f"Could not set signal handler for {sig}: {e}. Ctrl+C (KeyboardInterrupt) should still work.")
    else:
        logger.info("Running on Windows, signal handlers for SIGTERM/SIGINT are not set. Use Ctrl+C to stop.")


async def shutdown_gracefully(application):
    """Gracefully shut down the application and database."""
    if not application:
        logger.info("Application object is None. Attempting to close DB if possible.")
        if "db" in globals() and hasattr(db, "close"):
            try:
                await db.close()
                logger.info("Database connection closed (application was None).")
            except Exception as e_db:
                logger.error(f"Error closing database (application was None): {e_db}")
        else:
            logger.info("Database object not available for closing (application was None).")
        logger.info("Shutdown for non-existent application complete.")
        return

    # Signal the main loop to stop waiting
    if application.bot_data.get("main_loop_stop_event"):
        application.bot_data["main_loop_stop_event"].set()

    if application.bot_data.get("is_shutting_down", False):
        logger.info("Shutdown already in progress.")
        return
    application.bot_data["is_shutting_down"] = True

    logger.info("Initiating graceful shutdown...")

    try:
        await notify_maintainer(application, "🛑 Bot is shutting down.")
    except Exception as e:
        logger.error(f"Failed to send shutdown notification: {e}")

    if hasattr(application, "updater") and application.updater:
        try:
            if application.updater.running:
                logger.info("Stopping updater...")
                await application.updater.stop()
                logger.info("Updater stopped.")
            else:
                logger.info("Updater was not running.")
        except RuntimeError as e:  # e.g., "Updater is not running"
            logger.warning(f"Error stopping updater (may be benign): {e}")
        except Exception as e:
            logger.error(f"Unexpected error stopping updater: {e}")

    try:
        if application.running:
            logger.info("Stopping application...")
            await application.stop()  # Stops background tasks like _update_fetcher
            logger.info("Application stopped.")
        else:
            logger.info("Application was not running.")
    except RuntimeError as e:  # e.g., "Application is not running"
        logger.warning(f"Error stopping application (may be benign): {e}")
    except Exception as e:
        logger.error(f"Unexpected error stopping application: {e}")

    try:
        if application.initialized:
            logger.info("Shutting down application (core)...")
            await application.shutdown()  # Cleans up resources
            logger.info("Application shut down (core).")
        else:
            logger.info("Application was not initialized for core shutdown.")
    except RuntimeError as e:  # e.g., "Application is still running" or "not initialized"
        logger.warning(f"Error during core application shutdown (may be benign): {e}")
    except Exception as e:
        logger.error(f"Unexpected error during core application shutdown: {e}")

    if "db" in globals() and hasattr(db, "close"):
        try:
            await db.close()
            logger.info("Database connection closed.")
        except Exception as e:
            logger.error(f"Error closing database connection: {e}")
    else:
        logger.warning("Database object 'db' not found or no 'close' method.")

    logger.info("Bot shutdown process complete.")


async def notify_maintainer(application, text):
    try:
        await application.bot.send_message(chat_id=MAINTAINER, text=text)
    except Exception as e:
        logger.error(f"Failed to send stop message to user: {e}")


if __name__ == "__main__":
    asyncio.run(main())
