from datetime import datetime
from telethon import events

class AFKManager:
    def __init__(self, client):
        self._client = client
        self._afk_status = {
            "is_afk": False,
            "start_time": None,
            "reason": "I'm AFK right now. I'll get back to you later!"
        }

    def start(self):
        """Registers AFK event handlers."""
        self._client.add_event_handler(self.handle_afk_command, events.NewMessage(pattern=r"\.afk", outgoing=True))
        self._client.add_event_handler(self.handle_incoming_message, events.NewMessage(incoming=True))
        self._client.add_event_handler(self.disable_afk, events.NewMessage(outgoing=True))

    async def handle_afk_command(self, event):
        """Handles the `.afk` command."""
        reason = event.raw_text.split(".afk", 1)
        if len(reason) > 1 and reason[1].strip():
            self._afk_status["reason"] = reason[1].strip()

        self._afk_status["is_afk"] = True
        self._afk_status["start_time"] = datetime.now()
        await event.edit(f"I'm now AFK! Reason: {self._afk_status['reason']}")  # Use event.edit

    async def handle_incoming_message(self, event):
        """Handles incoming messages when AFK is enabled."""
        if self._afk_status["is_afk"] and event.is_private:
            now = datetime.now()
            afk_duration = now - self._afk_status["start_time"]
            hours, remainder = divmod(afk_duration.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            duration_str = f"{hours}h {minutes}m {seconds}s"

            reply_message = (
                f"{self._afk_status['reason']}\n"
                f"I've been AFK for: {duration_str}"
            )
            await event.reply(reply_message)  # Keep reply for incoming messages

    async def disable_afk(self, event):
        """Disables AFK when the user sends a message."""
        if self._afk_status["is_afk"]:
            self._afk_status["is_afk"] = False
            self._afk_status["start_time"] = None
            await event.edit("I'm no longer AFK!")  # Use event.edit
