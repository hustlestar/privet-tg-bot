"""Legacy callback handlers - redirects to new callback package."""

from src.handlers.callbacks import handle_callback_query

# Re-export the main handler for backward compatibility
__all__ = ["handle_callback_query"]
