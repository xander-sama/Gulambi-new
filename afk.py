# afk.py
import time
from datetime import datetime

from loguru import logger
from telethon import events

class AFKManager:
    """Manages the AFK status of the bot."""

    def __init__(self, client):
        self._client = client
        self._afk_status = False
        self._afk_message = None
        self._afk_start_time = None

    async def afk_command(self, event):
        """Sets the AFK status."""
        self._afk_status = not self._afk_status  # Toggle AFK status
        if self._afk_status:
            text = event.message.message.split(' ', 1)
            self._afk_message = text[1] if len(text) > 1 else "Away from keyboard."
            self._afk_start_time = datetime.now()
            await event.edit(f"AFK mode enabled. Reason: {self._afk_message}")
        else:
            await event.edit("AFK mode disabled.")

    async def handle_mention(self, event):
        """Handles mentions when AFK is enabled."""
        if self._afk_status and event.is_private:
            time_diff = datetime.now() - self._afk_start_time
            minutes = time_diff.seconds // 60
            await event.reply(f"I'm AFK. Reason: {self._afk_message}. I've been away for {minutes} minutes.")

    @property
    def event_handlers(self):
        """Returns a list of event handlers for AFK functionality."""
        return [
            {'callback': self.afk_command, 'event': events.NewMessage(pattern=r'\.afk', outgoing=True)},
            {'callback': self.handle_mention, 'event': events.NewMessage(incoming=True, func=lambda e: e.mentioned)}
        ]
  
