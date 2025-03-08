import asyncio
from loguru import logger
from telethon import events

class SpamManager:
    def __init__(self, client):
        self.client = client

    async def spam(self, event):
        """Handles the `.spam` command with optional reply support."""
        args = event.raw_text.split(maxsplit=2)
        if len(args) < 3 or not args[2].isdigit():
            await event.edit("**Usage:** `.spam <message> <count>`")
            return

        message = args[1]
        count = int(args[2])
        reply_to = event.reply_to_msg_id  # Get the replied message ID (if any)

        await event.delete()

        if reply_to:
            try:
                await self.client.get_messages(event.chat_id, ids=reply_to)  # Check if the message exists
            except:
                await event.respond("❌ **The replied message was deleted. Cancelling spam.**")
                return  

        for _ in range(count):
            try:
                if reply_to:
                    await self.client.send_message(event.chat_id, message, reply_to=reply_to)
                else:
                    await self.client.send_message(event.chat_id, message)
                await asyncio.sleep(1)  
            except Exception as e:
                logger.error(f"Spam error: {e}")
                break  

    async def delay_spam(self, event):
        """Handles the `.delayspam` command with optional reply support."""
        args = event.raw_text.split(maxsplit=3)
        if len(args) < 4 or not args[2].isdigit() or not args[3].isdigit():
            await event.edit("**Usage:** `.delayspam <message> <count> <delay>`")
            return

        message = args[1]
        count = int(args[2])
        delay = int(args[3])
        reply_to = event.reply_to_msg_id  # Get the replied message ID (if any)

        await event.delete()

        if reply_to:
            try:
                await self.client.get_messages(event.chat_id, ids=reply_to)  # Check if the message exists
            except:
                await event.respond("❌ **The replied message was deleted. Cancelling delayed spam.**")
                return  

        for _ in range(count):
            try:
                if reply_to:
                    await self.client.send_message(event.chat_id, message, reply_to=reply_to)
                else:
                    await self.client.send_message(event.chat_id, message)
                await asyncio.sleep(delay)  
            except Exception as e:
                logger.error(f"Delayed spam error: {e}")
                break  
