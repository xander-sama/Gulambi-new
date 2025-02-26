import time
from typing import Optional

from telethon import events

class AFKManager:
    """Manages the AFK feature for the userbot."""

    def __init__(self, client):
        self.client = client
        self.afk_status = False
        self.afk_message = "I am currently AFK. I will get back to you soon!"
        self.afk_start_time: Optional[float] = None

    async def afk_command(self, event) -> None:
        """Handle the .afk command."""
        if self.afk_status:
            await event.edit("I am already AFK!")
            return

        # Check if a custom message is provided
        custom_message = event.pattern_match.group(1)
        if custom_message:
            self.afk_message = custom_message

        # Enable AFK
        self.afk_status = True
        self.afk_start_time = time.time()
        await event.edit(f"I am now AFK: {self.afk_message}")

    async def unafk_command(self, event) -> None:
        """Handle the .unafk command."""
        if not self.afk_status:
            await event.edit("I am not AFK!")
            return

        # Disable AFK
        self.afk_status = False
        self.afk_start_time = None
        await event.edit("I am no longer AFK!")

    async def handle_afk_messages(self, event) -> None:
        """Handle incoming messages when AFK is enabled."""
        if not self.afk_status:
            return

        # Ignore messages from yourself
        if event.sender_id == (await self.client.get_me()).id:
            return

        # Calculate AFK duration
        afk_duration = int(time.time() - self.afk_start_time)
        hours, remainder = divmod(afk_duration, 3600)
        minutes, seconds = divmod(remainder, 60)
        duration_text = f"{hours}h {minutes}m {seconds}s"

        # Send AFK reply
        await event.reply(f"{self.afk_message}\n\n**AFK since:** {duration_text}")

    def get_event_handlers(self) -> list:
        """Returns a list of AFK-related event handlers."""
        return [
            {'callback': self.afk_command, 'event': events.NewMessage(pattern=r"^\.afk(?: |$)(.*)", outgoing=True)},
            {'callback': self.unafk_command, 'event': events.NewMessage(pattern=r"^\.unafk", outgoing=True)},
            {'callback': self.handle_afk_messages, 'event': events.NewMessage(incoming=True)}
        ]
