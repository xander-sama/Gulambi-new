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
from spam import SpamManager
from purge import PurgeManager
from clone import CloneManager
from admin import AdminManager
from kang import KangManager

HELP_MESSAGE = """**Help Menu**  

**General Commands:**  
• `.ping` - Pong!  
• `.alive` - Bot status  
• `.help` - Show this menu  

**Pokémon Commands:**  
• `.guess (on/off/stats)` - Pokémon guessing game  
• `.hunt (on/off/stats)` - Pokémon hunting  
• `.list <category>` - List Pokémon by category  
• `.release` - Pokémon release commands  

**Admin Commands:**  
• `.ban <user_id/reply>` - Ban a user  
• `.unban <user_id/reply>` - Unban a user  
• `.mute <user_id/reply>` - Mute a user (future messages only)  
• `.unmute <user_id/reply>` - Unmute a user  
• `.promote <user_id/reply>` - Make a user admin  
• `.demote <user_id/reply>` - Remove admin rights  
• `.kick <user_id/reply>` - Kick a user  

**Other Commands:**  
• `.afk (message)` - Set AFK status  
• `.unafk` - Remove AFK status  
• `.spam <msg> <count>` - Spam a message  
• `.delayspam <msg> <count> <delay>` - Spam with delay  
• `.stopspam` - Stop spam  
• `.purge <count>` - Delete the last `<count>` messages  
• `.clone` - Clone a user's profile (name, bio, username, and PFP)  
• `.revert` - Restore your original profile and remove cloned PFP  
• `.kang` - Steal stickers/images to your sticker pack  
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
        '_spam_manager',
        '_purge_manager',
        '_clone_manager',
        '_admin_manager',
        '_kang_manager'
    )

    def __init__(self, client) -> None:
        self._client = client
        self._guesser = PokemonIdentificationEngine(client)
        self._hunter = PokemonHuntingEngine(client)
        self._evaluator = ExpressionEvaluator(client)
        self._afk_manager = AFKManager(client)
        self._alive_handler = AliveHandler(client)
        self._release_manager = PokemonReleaseManager(client)
        self._spam_manager = SpamManager(client)
        self._purge_manager = PurgeManager(client)
        self._clone_manager = CloneManager(client)
        self._admin_manager = AdminManager(client)
        self._kang_manager = KangManager(client)

    def start(self) -> None:
        """Starts the Userbot's automations."""
        logger.info('Initializing Userbot')
        self._guesser.start()
        self._hunter.start()
        self._evaluator.start()
        self._alive_handler.register()

        # Add AFK event handlers
        for handler in self._afk_manager.get_event_handlers():
            self._client.add_event_handler(self._wrap_handler(handler['callback']), handler['event'])
            logger.debug(f'[{self.__class__.__name__}] Added AFK event handler: `{handler["callback"].__name__}`')

        # Register event handlers
        for handler in self.event_handlers:
            self._client.add_event_handler(self._wrap_handler(handler['callback']), handler['event'])
            logger.debug(f'[{self.__class__.__name__}] Added event handler: `{handler["callback"].__name__}`')

    def _wrap_handler(self, callback):
        """Wraps an event handler to catch and log exceptions."""
        async def wrapped_handler(event):
            try:
                await callback(event)
            except Exception as e:
                logger.error(f"Error in {callback.__name__}: {e}")
        return wrapped_handler

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
        """Returns a list of event handlers, including admin and kang commands."""
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
            {'callback': self._spam_manager.stop_spam, 'event': events.NewMessage(pattern=r"\.stopspam$", outgoing=True)},
            {'callback': self._purge_manager.purge_messages, 'event': events.NewMessage(pattern=r"\.purge (\d+)", outgoing=True)},
            {'callback': self._clone_manager.clone, 'event': events.NewMessage(pattern=r"\.clone$", outgoing=True)},
            {'callback': self._clone_manager.revert, 'event': events.NewMessage(pattern=r"\.revert$", outgoing=True)},
            {'callback': self._admin_manager.ban_user, 'event': events.NewMessage(pattern=r"\.ban(?: (\d+))?", outgoing=True)},
            {'callback': self._admin_manager.unban_user, 'event': events.NewMessage(pattern=r"\.unban(?: (\d+))?", outgoing=True)},
            {'callback': self._admin_manager.mute_user, 'event': events.NewMessage(pattern=r"\.mute(?: (\d+))?", outgoing=True)},
            {'callback': self._admin_manager.unmute_user, 'event': events.NewMessage(pattern=r"\.unmute(?: (\d+))?", outgoing=True)},
            {'callback': self._admin_manager.promote_user, 'event': events.NewMessage(pattern=r"\.promote(?: (\d+))?", outgoing=True)},
            {'callback': self._admin_manager.demote_user, 'event': events.NewMessage(pattern=r"\.demote(?: (\d+))?", outgoing=True)},
            {'callback': self._admin_manager.kick_user, 'event': events.NewMessage(pattern=r"\.kick(?: (\d+))?", outgoing=True)},
            {'callback': self._kang_manager.kang, 'event': events.NewMessage(pattern=r"\.kang(?: .+)?", outgoing=True)},
            {'callback': self._admin_manager.delete_muted_messages, 'event': events.NewMessage()},  # Auto-delete muted users' messages
        ]
