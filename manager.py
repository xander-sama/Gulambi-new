import time
from typing import List, Dict, Callable, Optional

from loguru import logger
from telethon import events

import constants
from evaluate import ExpressionEvaluator
from guesser import PokemonIdentificationEngine
from hunter import PokemonHuntingEngine
from afk import AFKManager  # Import the AFKManager

HELP_MESSAGE = """**Help**

• `.ping` - Pong
• `.alive` - but dead inside.
• `.help` - help your self.
• `.guess` (on/off/stats) - any guesses?
• `.hunt` (on/off/stats) - hunting for poki
• `.list` - list of poki
• `.afk [reason]` - Sets your AFK status.
"""


class Manager:
    """managing automation."""

    __slots__ = (
        '_client',
        '_guesser',
        '_hunter',
        '_evaluator',
        '_afk_manager'  # Add the AFKManager
    )

    def __init__(self, client) -> None:
        self._client = client
        self._guesser = PokemonIdentificationEngine(client)
        self._hunter = PokemonHuntingEngine(client)
        self._evaluator = ExpressionEvaluator(client)
        self._afk_manager = AFKManager(client)  # Initialize AFKManager

    def start(self) -> None:
        """Starts the User's automations."""
        logger.info('Initializing User')
        self._guesser.start()
        self._hunter.start()
        self._evaluator.start()

        all_handlers = self.event_handlers + self._afk_manager.event_handlers  # Combine handlers

        for handler in all_handlers:
            callback = handler.get('callback')
            event = handler.get('event')
            self._client.add_event_handler(
                callback=callback, event=event
            )
            logger.debug(f'[{self.__class__.__name__}] Added event handler: `{callback.__name__}`')

    async def ping_command(self, event) -> None:
        start = time.time()
        await event.edit('...')
        ping_ms = (time.time() - start) * 1000
        await event.edit(f'Pong!!\n{ping_ms:.2f}ms')

    async def alive_command(self, event) -> None:
        start = time.time()
        await event.edit('...')
        ping_ms = (time.time() - start) * 1000
        await event.edit(f"Hy Hello!! It's me [Gulambi](t.me/GulambiRobot).\n\nPing {ping_ms}ms")

    async def help_command(self, event) -> None:
        await event.edit(HELP_MESSAGE)

    async def handle_guesser_automation_control_request(self, event) -> None:
        """Handles user-initiated requests to control the automation process (on/off)."""
        await self._guesser.handle_automation_control_request(event)

    async def handle_hunter_automation_control_request(self, event) -> None:
        """Handles user-initiated requests to control the automation process (on/off)."""
        await self._hunter.handle_automation_control_request(event)

    async def handle_hunter_poki_list(self, event) -> None:
        await self._hunter.poki_list(event)

    @property
    def event_handlers(self) -> List[Dict[str, Callable | events.NewMessage]]:
        """Returns a list of event handlers."""
        return [
            {'callback': self.ping_command, 'event': events.NewMessage(pattern=constants.PING_COMMAND_REGEX, outgoing=True)},
            {'callback': self.alive_command, 'event': events.NewMessage(pattern=constants.ALIVE_COMMAND_REGEX, outgoing=True)},
            {'callback': self.help_command, 'event': events.NewMessage(pattern=constants.HELP_COMMAND_REGEX, outgoing=True)},
            {'callback': self.handle_guesser_automation_control_request, 'event': events.NewMessage(pattern=constants.GUESSER_COMMAND_REGEX, outgoing=True)},
            {'callback': self.handle_hunter_automation_control_request, 'event': events.NewMessage(pattern=constants.HUNTER_COMMAND_REGEX, outgoing=True)},
            {'callback': self.handle_hunter_poki_list, 'event': events.NewMessage(pattern=constants.HUNTER_LIST_REGEX, outgoing=True)}, # Added hunter list regex.
        ]
