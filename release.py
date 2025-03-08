import asyncio
from telethon import events
from loguru import logger
import constants

class PokemonReleaseManager:
    def __init__(self, client):
        self.client = client
        self.release_task = None  
        self.running = False  

    async def release_pokemon(self):
        """Releases Pokémon listed in constants.RELEASE"""
        while self.running:
            try:
                for pokemon in constants.RELEASE:
                    logger.info(f"Releasing {pokemon}...")
                    await self.client.send_message(constants.TARGET_BOT, f"/release {pokemon}")

                    await asyncio.sleep(2)
                    async for message in self.client.iter_messages(constants.TARGET_BOT, limit=1):
                        if message.buttons:
                            await message.click(0, 1)  
                            await asyncio.sleep(4)
                            async for updated_message in self.client.iter_messages(constants.TARGET_BOT, limit=1):
                                if updated_message.buttons:
                                    for i, row in enumerate(updated_message.buttons):
                                        for j, button in enumerate(row):
                                            if 'Release' in button.text:
                                                await updated_message.click(i, j)
                                                logger.info(f"{pokemon} released!")

                await asyncio.sleep(10)  

            except Exception as e:
                logger.error(f"Error: {e}")
                await asyncio.sleep(5)  

    async def start_releasing(self, event):
        if not self.running:
            self.running = True
            self.release_task = asyncio.create_task(self.release_pokemon())
            await event.reply(" Pokémon auto-release started!")
        else:
            await event.reply(" Release is already running!")

    async def stop_releasing(self, event):
        if self.running:
            self.running = False
            if self.release_task:
                self.release_task.cancel()
                self.release_task = None
            await event.reply(" Pokémon auto-release stopped!")
        else:
            await event.reply(" No active release process.")
