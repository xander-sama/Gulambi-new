import time
from typing import List, Dict, Callable

from loguru import logger
from telethon import events, Button

import constants
from afk import AFKManager  # Import AFKManager
from hunter import PokemonHuntingEngine  # Import PokemonHuntingEngine
from guesser import PokemonIdentificationEngine  # Import PokemonIdentificationEngine
from evaluate import ExpressionEvaluator  # Import ExpressionEvaluator

HELP_MESSAGE = """**Help**

**Pokemon Commands:**
- `.guess` (on/off/stats) - Any guesses?
- `.hunt` (on/off/stats) - Hunting for poki
- `.list` - List of poki

**General Commands:**
- `.ping` - Pong
- `.alive` - But dead inside.
- `.help` - Help yourself.
- `.afk` (message) - Set AFK status
- `.unafk` - Disable AFK status"""


class Manager:
    """Managing automation."""

    __slots__ = (
        '_client',
        '_guesser',
        '_hunter',
        '_evaluator',
        '_afk_manager'  # Add AFK manager
    )

    def __init__(self, client) -> None:
        self._client = client
        self._guesser = PokemonIdentificationEngine(client)  # Initialize guesser
        self._hunter = PokemonHuntingEngine(client)  # Initialize hunter
        self._evaluator = ExpressionEvaluator(client)  # Initialize evaluator
        self._afk_manager = AFKManager(client)  # Initialize AFK manager

    def start(self) -> None:
        """Starts the User's automations."""
        logger.info('Initializing User')
        self._guesser.start()
        self._hunter.start()
        self._evaluator.start()

        # Add AFK event handlers
        for handler in self._afk_manager.get_event_handlers():
            self._client.add_event_handler(
                callback=handler['callback'], event=handler['event']
            )
            logger.debug(f'[{self.__class__.__name__}] Added AFK event handler: `{handler["callback"].__name__}`')

        # Add other event handlers
        for handler in self.event_handlers:
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
        buttons = [
            [Button.inline("Pokemon Commands", data="pokemon_commands")],
            [Button.inline("General Commands", data="general_commands")]
        ]
        logger.debug(f"Buttons created: {buttons}")  # Debug log
        await event.reply("Please select a section:", buttons=buttons)
        logger.debug("Help message sent with buttons")  # Debug log

    async def handle_button_click(self, event) -> None:
        data = event.data.decode('utf-8')
        if data == "pokemon_commands":
            buttons = [
                [Button.inline("Guess (on/off/stats)", data="guess_command")],
                [Button.inline("Hunt (on/off/stats)", data="hunt_command")],
                [Button.inline("List Poki", data="list_command")]
            ]
            await event.edit("**Pokemon Commands:**", buttons=buttons)
        elif data == "general_commands":
            buttons = [
                [Button.inline("Ping", data="ping_command")],
                [Button.inline("Alive", data="alive_command")],
                [Button.inline("Help", data="help_command")],
                [Button.inline("AFK", data="afk_command")],
                [Button.inline("UnAFK", data="unafk_command")]
            ]
            await event.edit("**General Commands:**", buttons=buttons)
        elif data == "guess_command":
            await self.handle_guesser_automation_control_request(event)
        elif data == "hunt_command":
            await self.handle_hunter_automation_control_request(event)
        elif data == "list_command":
            await self.handle_hunter_poki_list(event)
        elif data == "ping_command":
            await self.ping_command(event)
        elif data == "alive_command":
            await self.alive_command(event)
        elif data == "help_command":
            await self.help_command(event)
        elif data == "afk_command":
            await self._afk_manager.set_afk(event)
        elif data == "unafk_command":
            await self._afk_manager.unafk(event)

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
            {'callback': self.handle_button_click, 'event': events.CallbackQuery()}
        ]
