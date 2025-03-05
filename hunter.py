import asyncio
import logging
import re

from telethon import events
from telethon.errors import MessageIdInvalidError

import constants

logger = logging.getLogger(__name__)

class Counter:
    """Tracks the number of hunts or battles."""
    
    def __init__(self):
        self.count = 0

    def increment(self):
        """Increase the counter by 1."""
        self.count += 1

    def reset(self):
        """Reset the counter to 0."""
        self.count = 0

class Auto:
    """Handles the state of auto-hunting."""
    
    def __init__(self):
        self.state = False

    def start(self):
        """Starts the auto-hunt mode."""
        self.state = True

    def stop(self, counter):
        """Stops the auto-hunt mode and resets the counter."""
        self.state = False
        counter.reset()

class PokemonHuntingEngine:
    """Manages auto-hunt functionality for the Userbot."""

    def __init__(self, client):
        self._client = client
        self._auto = Auto()
        self._counter = Counter()

    def start(self):
        """Registers event handlers for hunting."""
        for handler in self.event_handlers:
            self._client.add_event_handler(handler['callback'], handler['event'])
            logger.debug(f"[{self.__class__.__name__}] Registered event handler: {handler['callback'].__name__}")

    async def handle_automation_control_request(self, event):
        """Handles the `.hunt on/off/stats` command."""
        command = event.raw_text.split()
        if len(command) < 2:
            await event.edit("Usage: `.hunt on/off/stats`")
            return

        option = command[1].lower()
        if option == "on":
            if self._auto.state:
                await event.edit("Hunting is already `on`.")
            else:
                self._auto.start()
                await event.edit("Hunting started.")
                asyncio.create_task(self.send_hunt_periodically())
        elif option == "off":
            if self._auto.state:
                self._auto.stop(self._counter)
                await event.edit("Hunting stopped.")
            else:
                await event.edit("Hunting is already `off`.")
        elif option == "stats":
            await event.edit(f"Total hunts: {self._counter.count}")
        else:
            await event.edit("Invalid option! Use `.hunt on/off/stats`.")

    async def send_hunt_periodically(self):
        """Sends /hunt command periodically until stopped."""
        while self._auto.state and self._client.is_connected():
            await asyncio.sleep(constants.PERIODICALLY_HUNT_SECONDS)
            await self._client.send_message(entity=constants.HEXA_BOT_ID, message="/hunt")

    async def daily_limit(self, event):
        """Handles the daily hunt limit message."""
        if "Daily hunt limit reached" in event.raw_text:
            await self._client.send_message(entity=constants.CHAT_ID, message=constants.HUNT_DAILY_LIMIT_REACHED)
            self._auto.stop(self._counter)

    async def hunt_or_pass(self, event):
        """Decides whether to hunt or pass based on the event message."""
        if not self._auto.state:
            return

        if "shiny" in event.raw_text.lower() and event.raw_text.lower().endswith("found!"):
            self._auto.stop(self._counter)
            await event.client.send_message(entity=constants.CHAT_ID, message=constants.SHINY_FOUND.format(event.client.me))
        elif "A wild" in event.raw_text:
            pok_name = event.raw_text.split("wild ")[1].split(" (")[0]
            logger.info(pok_name)
            if pok_name in constants.REGULAR_BALL or pok_name in constants.REPEAT_BALL:
                await asyncio.sleep(constants.COOLDOWN())
                try:
                    await event.click(0, 0)
                except MessageIdInvalidError:
                    logger.exception(f"Failed to click the button for {pok_name}")
            else:
                await asyncio.sleep(constants.COOLDOWN())
                await event.client.send_message(entity=constants.HEXA_BOT_ID, message="/hunt")

    @property
    def event_handlers(self):
        """Returns a list of event handlers for auto-hunting."""
        return [
            {"callback": self.handle_automation_control_request, "event": events.NewMessage(pattern=r"\.hunt (on|off|stats)", outgoing=True)},
            {"callback": self.daily_limit, "event": events.NewMessage(chats=constants.HEXA_BOT_ID)},
            {"callback": self.hunt_or_pass, "event": events.NewMessage(chats=constants.HEXA_BOT_ID)},
        ]
