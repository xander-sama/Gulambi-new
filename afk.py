import time
from typing import Optional, Dict

from loguru import logger
from telethon import events

import constants

class AFKManager:
    """Manages the AFK feature for the userbot."""

    def __init__(self, client):
        self.client = client
        self.afk_status = False
        self.afk_message = "I'm AFK."
        self.afk_start_time: Optional[float] = None
        self.afk_reason: Optional[str] = None
        self.last_replied: Dict[int, float] = {}  # Track last reply time to each user

    async def afk_command(self, event) -> None:
        """Handle the .afk command."""
        if self.afk_status:
            await event.edit("I am already AFK!")
            return

        # Get custom reason if provided
        custom_message = event.pattern_match.group(1)
        self.afk_reason = custom_message if custom_message else "No reason provided"

        # Prevent editing if message content is the same
        new_afk_message = f"I'm now AFK! Reason: {self.afk_reason}"
        if event.text == new_afk_message:
            return

        # Enable AFK
        self.afk_status = True
        self.afk_start_time = time.time()
        await event.edit(new_afk_message)
        logger.info(f"AFK enabled. Reason: {self.afk_reason}")

    async def handle_afk_messages(self, event) -> None:
        """Handle incoming messages when AFK is enabled."""
        if not self.afk_status:
            return

        # Ignore messages from yourself
        if event.sender_id == (await self.client.get_me()).id:
            return

        # Check if the message is in a group and the bot is not mentioned
        if event.is_group and not event.mentioned:
            return

        # Prevent multiple AFK replies to the same user in a short period
        current_time = time.time()
        last_reply_time = self.last_replied.get(event.sender_id, 0)
        if current_time - last_reply_time < 60:  # 60 seconds cooldown
            return

        # Calculate AFK duration
        afk_duration = int(current_time - self.afk_start_time)
        hours, remainder = divmod(afk_duration, 3600)
        minutes, seconds = divmod(remainder, 60)
        duration_text = f"{hours}h {minutes}m {seconds}s"

        # Prepare AFK reply
        reply_message = f"I'm AFK.\nReason: {self.afk_reason}\nTotal time since AFK: {duration_text}"

        # Send AFK reply
        await event.reply(reply_message)
        self.last_replied[event.sender_id] = current_time  # Update last reply time
        logger.info(f"Sent AFK reply to {event.sender_id}")

    async def disable_afk_on_message(self, event) -> None:
        """Automatically disable AFK when the user sends any message."""
        if self.afk_status:
            self.afk_status = False
            self.afk_start_time = None
            self.afk_reason = None
            logger.info("AFK disabled.")
            await event.respond("I am no longer AFK!")

    def get_event_handlers(self) -> list:
        """Returns a list of AFK-related event handlers."""
        return [
            {'callback': self.afk_command, 'event': events.NewMessage(pattern=constants.AFK_COMMAND_REGEX, outgoing=True)},
            {'callback': self.handle_afk_messages, 'event': events.NewMessage(incoming=True)},
            {'callback': self.disable_afk_on_message, 'event': events.NewMessage(outgoing=True)}  # Disable AFK on message
        ]
