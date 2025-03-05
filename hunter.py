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
    """Handles the state of auto-battling."""
    
    def __init__(self):
        self.state = False

    def start(self):
        """Starts the auto-battle mode."""
        self.state = True

    def stop(self, counter):
        """Stops the auto-battle mode and resets the counter."""
        self.state = False
        counter.reset()

class PokemonHuntingEngine:
    """Manages auto-battle functionality for the Userbot."""

    def __init__(self, client):
        self._client = client
        self._auto = Auto()
        self._counter = Counter()
        self._low_lvl = False

    async def send_hunt_periodically(self):
        """Sends /hunt command every 15 minutes until the client disconnects."""
        while self._client.is_connected():
            await asyncio.sleep(constants.PERIODICALLY_HUNT_SECONDS)
            if self._auto.state:
                await self._client.send_message(entity=constants.HEXA_BOT_ID, message='/hunt')

    async def auto_command(self, event):
        """Handles the auto-battle command."""
        if event.raw_text.endswith('on'):
            if self._auto.state:
                await event.edit('Auto Battle: already `on`.')
            else:
                self._auto.start()
                await event.edit('Auto Battle: changed state to `on`.')
        elif event.raw_text.endswith('off'):
            if self._auto.state:
                self._auto.stop(self._counter)
                await event.edit('Auto Battle: changed state to `off`.')
            else:
                await event.edit('Auto Battle: already `off`.')
        else:
            await event.edit('Unknown Error: cannot find auto battle state [on, off].')

    async def daily_limit(self, event):
        """Handles the daily hunt limit."""
        if not self._auto.state:
            return
        if 'Daily hunt limit reached' in event.raw_text:
            await event.client.send_message(entity=constants.CHAT_ID, message=constants.HUNT_DAILY_LIMIT_REACHED)
            self._auto.stop(self._counter)

    async def hunt_or_pass(self, event):
        """Decides whether to hunt or pass based on the event."""
        if not self._auto.state:
            return

        if 'shiny' in event.raw_text.lower() and event.raw_text.lower().endswith('found!'):
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
                    logger.exception('Failed to click the button for %s', pok_name)
            else:
                await asyncio.sleep(constants.COOLDOWN())
                await event.client.send_message(entity=constants.HEXA_BOT_ID, message='/hunt')

    async def battle_first(self, event):
        """Handles the first battle action."""
        if not self._auto.state:
            return

        if "Battle begins!" in event.raw_text:
            wild_pokemon_name_match = re.search(r"Wild (\w+) \[.*\]\nLv\. \d+  •  HP \d+/\d+", event.raw_text)
            if wild_pokemon_name_match:
                pok_name = wild_pokemon_name_match.group(1)
                wild_pokemon_hp_match = re.search(r"Wild .* \[.*\]\nLv\. \d+  •  HP (\d+)/(\d+)", event.raw_text)
                if wild_pokemon_hp_match:
                    wild_max_hp = int(wild_pokemon_hp_match.group(2))
                    self._low_lvl = wild_max_hp <= 50
                    logger.info('low lvl set to %s', self._low_lvl)
                    await self._handle_battle_action(event, pok_name, self._low_lvl)

    async def _handle_battle_action(self, event, pok_name: str, is_low_lvl: bool):
        """Handles the battle action based on the Pokémon's level."""
        if is_low_lvl:
            await asyncio.sleep(constants.COOLDOWN())
            try:
                await event.click(text="Poke Balls")
                logger.info('Clicked on Poke Balls')
            except MessageIdInvalidError:
                logger.error('Failed to click Poke Balls')
        else:
            await asyncio.sleep(2)
            try:
                await event.click(0, 0)
            except MessageIdInvalidError:
                logger.error('Failed to click the button for high-level Pokemon')

    async def switch_pokemon(self, event):
        """Switches to a Pokémon from the hunting team if available."""
        if "Choose your next pokemon." in event.raw_text and self._auto.state:
            for pokemon in constants.HUNTING_TEAM:
                try:
                    await event.click(text=pokemon)
                    logger.info(f'Switched to {pokemon}')
                    break
                except MessageIdInvalidError:
                    logger.error(f'Failed to switch to {pokemon}')

    @property
    def event_handlers(self) -> list:
        """Returns a list of event handlers for auto-battle."""
        return [
            {'callback': self.auto_command, 'event': events.NewMessage(pattern=r"//auto battle (on|--f on|off)", outgoing=True)},
            {'callback': self.daily_limit, 'event': events.NewMessage(chats=constants.HEXA_BOT_ID)},
            {'callback': self.hunt_or_pass, 'event': events.NewMessage(chats=constants.HEXA_BOT_ID)},
            {'callback': self.battle_first, 'event': events.NewMessage(chats=constants.HEXA_BOT_ID)},
            {'callback': self._handle_battle_action, 'event': events.MessageEdited(chats=constants.HEXA_BOT_ID)},
            {'callback': self.switch_pokemon, 'event': events.MessageEdited(chats=constants.HEXA_BOT_ID)},
        ]
