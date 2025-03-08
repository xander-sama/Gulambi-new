import time
from typing import List, Dict, Callable

from loguru import logger
from telethon import events

import constants
from evaluate import ExpressionEvaluator
from guesser import PokemonIdentificationEngine
from hunter import PokemonHuntingEngine
from afk import AFKManager
from alive import AliveHandler
from release import PokemonReleaseManager
from spam import SpamManager  # Import SpamManager

HELP_MESSAGE = """**Help**

• `.ping` - Pong
• `.alive` - Bot status
• `.help` - Help menu
• `.guess` (on/off/stats) - any guesses?
• `.hunt` (on/off/stats) - hunting for poki
• `.list <category>` - List Pokémon by category
• `.afk` (message) - Set AFK status
• `.unafk` - Disable AFK status
• `.release` - Release Pokémon commands
• `.spam <msg> <count>` - Spam message multiple times
• `.delayspam <msg> <count> <delay>` - Spam with delay
"""

class Manager:
    """Manages automation for the Userbot."""

    __slots__ = (
        '_client',
        '_guesser',
        '_hunter',
        '_evaluator',
        '_afk_manager',
        '_alive_handler',
        '_release_manager',
        '_spam_manager'  # Added spam manager
    )

    def __init__(self, client) -> None:
        self._client = client
        self._guesser = PokemonIdentificationEngine(client)
        self._hunter = PokemonHuntingEngine(client)
        self._evaluator = ExpressionEvaluator(client)
        self._afk_manager = AFKManager(client)
        self._alive_handler = AliveHandler(client)
        self._release_manager = PokemonReleaseManager(client)
        self._spam_manager = SpamManager(client)  # Initialize spam manager

    def start(self) -> None:
        """Starts the Userbot's automations."""
        logger.info('Initializing Userbot')
        self._guesser.start()
        self._hunter.start()
        self._evaluator.start()
        self._alive_handler.register()

        # Add AFK event handlers
        for handler in self._afk_manager.get_event_handlers():
            self._client.add_event_handler(handler['callback'], handler['event'])
            logger.debug(f'[{self.__class__.__name__}] Added AFK event handler: `{handler["callback"].__name__}`')

        # Register event handlers
        for handler in self.event_handlers:
            self._client.add_event_handler(handler['callback'], handler['event'])
            logger.debug(f'[{self.__class__.__name__}] Added event handler: `{handler["callback"].__name__}`')

    async def ping_command(self, event) -> None:
        """Handles the `.ping` command."""
        start = time.time()
        await event.edit('...')
        ping_ms = (time.time() - start) * 1000
        await event.edit(f'Pong!!\n{ping_ms:.2f}ms')

    async def help_command(self, event) -> None:
        """Handles the `.help` command."""
        await event.edit(HELP_MESSAGE)

    @property
    def event_handlers(self) -> List[Dict[str, Callable | events.NewMessage]]:
        """Returns a list of event handlers, including release and spam commands."""
        return [
            {'callback': self.ping_command, 'event': events.NewMessage(pattern=constants.PING_COMMAND_REGEX, outgoing=True)},
            {'callback': self.help_command, 'event': events.NewMessage(pattern=constants.HELP_COMMAND_REGEX, outgoing=True)},
            {'callback': self._release_manager.show_release_help, 'event': events.NewMessage(pattern=r"\.release$", outgoing=True)},
            {'callback': self._release_manager.start_releasing, 'event': events.NewMessage(pattern=r"\.release on", outgoing=True)},
            {'callback': self._release_manager.stop_releasing, 'event': events.NewMessage(pattern=r"\.release off", outgoing=True)},
            {'callback': self._release_manager.add_pokemon, 'event': events.NewMessage(pattern=r"\.release add (.+)", outgoing=True)},
            {'callback': self._release_manager.remove_pokemon, 'event': events.NewMessage(pattern=r"\.release remove (.+)", outgoing=True)},
            {'callback': self._release_manager.list_pokemon, 'event': events.NewMessage(pattern=r"\.release list", outgoing=True)},
            {'callback': self._spam_manager.spam, 'event': events.NewMessage(pattern=r"\.spam (.+) (\d+)", outgoing=True)},
            {'callback': self._spam_manager.delay_spam, 'event': events.NewMessage(pattern=r"\.delayspam (.+) (\d+) (\d+)", outgoing=True)},
        ]
