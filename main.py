import asyncio

import uvloop
from loguru import logger
from telethon import TelegramClient
from telethon.errors import ApiIdInvalidError, AuthKeyDuplicatedError, FloodError
from telethon.sessions import StringSession

import constants
import health_checker
from manager import Manager

async def main():
    try:
        client = TelegramClient(
            session=StringSession(constants.SESSION),
            api_id=constants.API_ID,
            api_hash=constants.API_HASH,
            app_version=constants.__version__,
            auto_reconnect=True
        )

        await client.start()
        me = await client.get_me()
        client.me = me
        client.parse_mode = 'html'

        manager = Manager(client)
        manager.start()

        logger.info(f'Userbot Login successfull: {me.first_name} - @{me.username} ({me.id})')
        await client.run_until_disconnected()

    except (
        AuthKeyDuplicatedError, ApiIdInvalidError,
        EOFError, FloodError
    ) as e:
        logger.exception(f'error occurred when login userbot. {e}')

health_checker.check()
try:
    with asyncio.Runner(loop_factory=uvloop.new_event_loop) as runner:
        runner.run(main())
except KeyboardInterrupt as e:
    logger.exception(f'Forced stop... Bye! {e}')
