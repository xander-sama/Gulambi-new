import time
from datetime import datetime
from loguru import logger
from telethon import events

class AFKManager:
    """Manages the AFK status of the bot."""

    def __init__(self, client):
        self._client = client
        self._afk_status = False
        self._afk_message = "I'm AFK."
        self._afk_start_time = None

    async def afk_command(self, event):
        """Toggles AFK status and sets a reason if provided."""
        self._afk_status = not self._afk_status  # Toggle AFK status
        if self._afk_status:
            text = event.raw_text.split(' ', 1)
            self._afk_message = text[1] if len(text) > 1 else "I'm AFK."
            self._afk_start_time = datetime.now()
            await event.edit(f"🔹 **AFK Mode Activated**\nReason: {self._afk_message}")
        else:
            time_afk = datetime.now() - self._afk_start_time
            minutes = time_afk.seconds // 60
            await event.edit(f"✅ **You're back!** You were AFK for {minutes} minutes.")
            self._afk_start_time = None  # Reset time

    async def handle_mention(self, event):
        """Responds to mentions when AFK is active."""
        if self._afk_status and event.message.mentioned:
            time_diff = datetime.now() - self._afk_start_time
            minutes = time_diff.seconds // 60
            await event.reply(f"🚨 **I'm currently AFK!**\nReason: {self._afk_message}\nI've been away for {minutes} minutes.")

    @property
    def event_handlers(self):
        """Returns event handlers for AFK functionality."""
        return [
            {'callback': self.afk_command, 'event': events.NewMessage(pattern=r'(?i)^\.afk(?: (.+))?$', outgoing=True)},
            {'callback': self.handle_mention, 'event': events.NewMessage(incoming=True, func=lambda e: e.message.mentioned)}
        ]
