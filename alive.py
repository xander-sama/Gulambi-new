import time
from telethon import events
from platform import python_version
from telethon import version

import constants

class AliveHandler:
    def __init__(self, client):
        self._client = client

    async def alive_command(self, event):
        """Responds with bot status when `.alive` is used."""
        start_time = time.time()
        await event.edit("Checking...")
        ping_ms = (time.time() - start_time) * 1000

        alive_message = (
            "**✅ Bot is Alive!**\n\n"
            f"**👤 Owner:** `{constants.OWNER_NAME}`\n"
            f"**⚡ Uptime:** `{ping_ms:.2f}ms`\n"
            f"**🐍 Python:** `{python_version()}`\n"
            f"**📡 Telethon:** `{version.__version__}`\n"
            f"**📌 Bot Version:** `{constants.BOT_VERSION}`\n\n"
            "➜ [made by](https://t.me/exryuh) "
        )

        await event.edit(alive_message, link_preview=False)

    def register(self):
        """Registers the `.alive` command with the client."""
        self._client.add_event_handler(
            self.alive_command,
            events.NewMessage(pattern=constants.ALIVE_COMMAND_REGEX, outgoing=True)
        )
