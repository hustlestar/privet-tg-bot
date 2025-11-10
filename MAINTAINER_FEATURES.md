# Maintainer Monitoring Features

## Configuration

Set the maintainer chat ID in your `.env` file:
```env
MAINTAINER_CHAT_ID=66395090
```

## Automatic Notifications

### 🚀 Startup Notification
When the bot starts, you'll receive:
- Bot name and version
- Service status (Database, AI, Voice services)
- Configuration summary

### 🛑 Shutdown Notification
When the bot stops, you'll receive:
- Shutdown reason (signal or manual)
- Session duration

### ⚠️ Error Notifications
Critical errors are automatically reported with:
- Error type and message
- User ID (if applicable)
- Timestamp

### 📊 Health Reports (Optional)
If enabled, periodic health reports include:
- Uptime statistics
- Database connection status
- pgvector extension status
- User statistics (total, active)
- Message processing count
- Error count

## Status Messages Format

### Start Message Example:
```
🚀 **My Bot** v1.0.0

✅ Bot started successfully!

**Services Status:**
• Database: ✅ Connected
• AI Provider: ✅ openai/gpt-3.5-turbo
• Voice STT: ✅ Ready
• Voice TTS: ✅ Ready
• Support Bot: ❌ Disabled

🎙️ AI Companion features active!
```

### Shutdown Message Example:
```
🛑 **My Bot** v1.0.0

⚠️ Bot is shutting down...

**Shutdown Reason:** Signal received (SIGTERM/SIGINT)

📊 Session Statistics will be available on next start.
```

### Error Alert Example:
```
⚠️ **Error in My Bot**

**Error Type:** ValueError
**Error:** Invalid user input...
**User:** 123456789
```

## Enabling Health Monitoring

To enable periodic health reports, add the health monitor to your bot initialization. The monitor can:
- Send daily/hourly health reports
- Track message and error counts
- Monitor database connectivity
- Alert on critical issues

## Benefits

1. **Real-time Awareness**: Know immediately when the bot starts, stops, or encounters errors
2. **Proactive Monitoring**: Catch issues before users report them
3. **Performance Tracking**: Monitor usage patterns and system health
4. **Quick Response**: Get notified of critical issues instantly

## Privacy Note

The maintainer receives:
- System status and errors
- Aggregate statistics
- NO user messages or personal data
- Only user IDs when errors occur

---

All notifications are sent to Telegram chat ID: **66395090**