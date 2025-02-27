import time
from typing import List, Dict, Callable

from loguru import logger
from telethon import events, Button

import constants
from evaluate import ExpressionEvaluator
from guesser import PokemonIdentificationEngine
from hunter import PokemonHuntingEngine
from afk import AFKManager  # Import AFKManager


class Manager:
    """Managing automation."""

    __slots__ = (
        "_client",
        "_guesser",
        "_hunter",
        "_evaluator",
        "_afk_manager",
        "_commands"
    )

    def __init__(self, client) -> None:
        self._client = client
        self._guesser = PokemonIdentificationEngine(client)
        self._hunter = PokemonHuntingEngine(client)
        self._evaluator = ExpressionEvaluator(client)
        self._afk_manager = AFKManager(client)

        # Commands categorized into General and Pokémon
        self._commands = {
            "General": [
                ("ping", "`.ping` - Check bot response time"),
                ("alive", "`.alive` - Check if the bot is running"),
                ("help", "`.help` - Display this help message"),
                ("afk", "`.afk` (message) - Set AFK status with a message"),
                ("unafk", "`.unafk` - Disable AFK status"),
            ],
            "Pokémon": [
                ("guess", "`.guess` (on/off/stats) - Play Pokémon guessing game"),
                ("hunt", "`.hunt` (on/off/stats) - Start Pokémon hunting"),
                ("list", "`.list` - Show Pokémon list"),
            ],
        }

    def start(self) -> None:
        """Starts the User's automations."""
        logger.info("Initializing User")
        self._guesser.start()
        self._hunter.start()
        self._evaluator.start()

        # Add AFK event handlers
        for handler in self._afk_manager.get_event_handlers():
            self._client.add_event_handler(
                callback=handler["callback"], event=handler["event"]
            )
            logger.debug(f"[{self.__class__.__name__}] Added AFK event handler: `{handler['callback'].__name__}`")

        # Add other event handlers
        for handler in self.event_handlers:
            self._client.add_event_handler(
                callback=handler["callback"], event=handler["event"]
            )
            logger.debug(f"[{self.__class__.__name__}] Added event handler: `{handler['callback'].__name__}`")

    async def help_command(self, event) -> None:
        """Displays the help menu with category buttons."""
        buttons = [
            [Button.inline("📌 General Commands", b"help_general")],
            [Button.inline("🎮 Pokémon Commands", b"help_pokemon")],
        ]
        await event.edit("**📜 Help Menu**\n\nSelect a category:", buttons=buttons)

    async def show_help_category(self, event) -> None:
        """Handles button clicks and displays commands for the selected category."""
        data = event.data.decode("utf-8")  # Convert bytes to string

        if data in ["help_general", "help_pokemon"]:
            category = "General" if data == "help_general" else "Pokémon"
            buttons = [[Button.inline(desc.split(" ")[0], f"cmd_{cmd}".encode())] for cmd, desc in self._commands[category]]
            buttons.append([Button.inline("⬅ Back", b"help_main")])

            await event.edit(f"**📌 {category} Commands**\n\nSelect a command to see details:", buttons=buttons)

        elif data.startswith("cmd_"):
            cmd_key = data.split("_")[1]  # Extract command key
            for category in self._commands:
                for cmd, desc in self._commands[category]:
                    if cmd == cmd_key:
                        await event.edit(f"**ℹ️ Command Details**\n\n{desc}", buttons=[[Button.inline("⬅ Back", f"help_{category.lower()}".encode())]])
                        return

        elif data == "help_main":
            await self.help_command(event)  # Return to main menu

    async def ping_command(self, event) -> None:
        start = time.time()
        await event.edit("...")
        ping_ms = (time.time() - start) * 1000
        await event.edit(f"Pong!!\n{ping_ms:.2f}ms")

    async def alive_command(self, event) -> None:
        start = time.time()
        await event.edit("...")
        ping_ms = (time.time() - start) * 1000
        await event.edit(f"Hy Hello!! It's me [Gulambi](t.me/GulambiRobot).\n\nPing {ping_ms}ms")

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
            {"callback": self.ping_command, "event": events.NewMessage(pattern=constants.PING_COMMAND_REGEX, outgoing=True)},
            {"callback": self.alive_command, "event": events.NewMessage(pattern=constants.ALIVE_COMMAND_REGEX, outgoing=True)},
            {"callback": self.help_command, "event": events.NewMessage(pattern=constants.HELP_COMMAND_REGEX, outgoing=True)},
            {"callback": self.show_help_category, "event": events.CallbackQuery(pattern=b"help_.*|cmd_.*")},
            {"callback": self.handle_guesser_automation_control_request, "event": events.NewMessage(pattern=constants.GUESSER_COMMAND_REGEX, outgoing=True)},
            {"callback": self.handle_hunter_automation_control_request, "event": events.NewMessage(pattern=constants.HUNTER_COMMAND_REGEX, outgoing=True)}
        ]
