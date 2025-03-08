import asyncio
from telethon import events

class SpamManager:
    """Handles spam commands for the Userbot."""

    def __init__(self, client):
        self._client = client
        self._running_spams = {}  # Dictionary to store running spam tasks

    async def spam(self, event):
        """Handles the `.spam <msg> <count>` command."""
        args = event.pattern_match.group(1).rsplit(" ", 1)
        if len(args) != 2 or not args[1].isdigit():
            await event.reply("**Usage:** `.spam <message> <count>`")
            return

        message, count = args[0], int(args[1])
        reply_to = event.reply_to_msg_id

        for _ in range(count):
            if event.chat_id not in self._running_spams:
                return  # Stop if spam is canceled
            await event.respond(message, reply_to=reply_to)

    async def delay_spam(self, event):
        """Handles the `.delayspam <msg> <count> <delay>` command."""
        args = event.pattern_match.group(1).rsplit(" ", 2)
        if len(args) != 3 or not args[1].isdigit() or not args[2].isdigit():
            await event.reply("**Usage:** `.delayspam <message> <count> <delay>`")
            return

        message, count, delay = args[0], int(args[1]), int(args[2])
        reply_to = event.reply_to_msg_id

        self._running_spams[event.chat_id] = True  # Mark spam as running

        for _ in range(count):
            if event.chat_id not in self._running_spams:
                return  # Stop if spam is canceled
            await event.respond(message, reply_to=reply_to)
            await asyncio.sleep(delay)

    async def stop_spam(self, event):
        """Stops ongoing spam in the chat."""
        if event.chat_id in self._running_spams:
            del self._running_spams[event.chat_id]
            await event.reply("**Spam Stopped!**")
        else:
            await event.reply("**No active spam found!**")
