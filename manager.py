import time
from typing import List, Dict, Callable

from loguru import logger
from telethon import events

import constants
from evaluate import ExpressionEvaluator
from guesser import PokemonIdentificationEngine
from hunter import PokemonHuntingEngine
from afk import AFKManager  
from alive import AliveHandler  # Import AliveHandler

HELP_MESSAGE = """**Help**

• `.ping` - Pong
• `.alive` - Bot status
• `.help` - Help menu
• `.guess` (on/off/stats) - any guesses?
• `.hunt` (on/off/stats) - hunting for poki
• `.list <category>` - List Pokémon by category
• `.afk` (message) - Set AFK status
• `.unafk` - Disable AFK status

**Available Categories for `.list`**
- `regular`
- `repeat`
- `ultra`
- `great`
- `nest`
- `safari`
"""

class Manager:
    """Manages automation for the Userbot."""

    __slots__ = (
        '_client',
        '_guesser',
        '_hunter',
        '_evaluator',
        '_afk_manager',
        '_alive_handler'
    )

    def __init__(self, client) -> None:
        self._client = client
        self._guesser = PokemonIdentificationEngine(client)
        self._hunter = PokemonHuntingEngine(client)
        self._evaluator = ExpressionEvaluator(client)
        self._afk_manager = AFKManager(client)  
        self._alive_handler = AliveHandler(client)  

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

    async def handle_guesser_automation_control_request(self, event) -> None:
        """Handles user requests to enable/disable guesser automation."""
        await self._guesser.handle_automation_control_request(event)

    async def handle_hunter_automation_control_request(self, event) -> None:
        """Handles user requests to enable/disable hunter automation."""
        await self._hunter.handle_automation_control_request(event)

    async def list_pokemon(self, event) -> None:
        """Handles the `.list` command by showing Pokémon based on the specified category."""
        args = event.pattern_match.group(1)

        categories = {
            "regular": constants.REGULAR_BALL,
            "repeat": constants.REPEAT_BALL,
            "ultra": constants.ULTRA_BALL,
            "great": constants.GREAT_BALL,
            "nest": constants.NEST_BALL,
            "safari": constants.SAFARI
        }

        if not args:  
            await event.edit(
                "**Usage:** `.list <category>`\n\n"
                "**Available categories:**\n"
                "- `regular`\n"
                "- `repeat`\n"
                "- `ultra`\n"
                "- `great`\n"
                "- `nest`\n"
                "- `safari`"
            )
            return

        category = args.lower()
        if category not in categories:
            await event.edit(f"**Invalid category!**\nUse one of: {', '.join(categories.keys())}")
            return

        pokemon_list = categories[category]
        if not pokemon_list:
            await event.edit(f"No Pokémon found in `{category}` category.")
            return

        formatted_list = ", ".join(sorted(pokemon_list))  
        await event.edit(f"**{category.capitalize()} Ball Pokémon:**\n{formatted_list}")

    @property
    def event_handlers(self) -> List[Dict[str, Callable | events.NewMessage]]:
        """Returns a list of event handlers."""
        return [
            {'callback': self.ping_command, 'event': events.NewMessage(pattern=constants.PING_COMMAND_REGEX, outgoing=True)},
            {'callback': self.help_command, 'event': events.NewMessage(pattern=constants.HELP_COMMAND_REGEX, outgoing=True)},
            {'callback': self.handle_guesser_automation_control_request, 'event': events.NewMessage(pattern=constants.GUESSER_COMMAND_REGEX, outgoing=True)},
            {'callback': self.handle_hunter_automation_control_request, 'event': events.NewMessage(pattern=constants.HUNTER_COMMAND_REGEX, outgoing=True)},
            {'callback': self.list_pokemon, 'event': events.NewMessage(pattern=constants.LIST_COMMAND_REGEX, outgoing=True)}
        ]  
