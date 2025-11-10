"""Handler modules for the Learn Words bot."""

MAINTAINER = 66395090


async def on_new_user_notify(bot):
    await bot.send_message(chat_id=MAINTAINER, text="New user registered")
