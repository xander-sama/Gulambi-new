import asyncio
from telethon import events
from loguru import logger
import constants

class PokemonReleaseManager:
    def __init__(self, client):
        self.client = client
        self.release_task = None  
        self.running = False  
        self.current_chat_id = None  # Stores the chat where .release on was sent

    async def release_pokemon(self):
        """Releases Pokémon in the chat where .release on was used"""
        while self.running:
            try:
                if not self.current_chat_id:
                    logger.warning("No active chat ID for release. Stopping...")
                    self.running = False
                    return  

                for pokemon in constants.RELEASE:
                    logger.info(f"Releasing {pokemon} in chat {self.current_chat_id}...")
                    await self.client.send_message(self.current_chat_id, f"/release {pokemon}")

                    await asyncio.sleep(2)
                    async for message in self.client.iter_messages(self.current_chat_id, limit=1):
                        if message.buttons:
                            await message.click(0, 1)  
                            await asyncio.sleep(4)
                            async for updated_message in self.client.iter_messages(self.current_chat_id, limit=1):
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
        """Starts the auto-release process in the chat where the command was sent"""
        if not self.running:
            self.running = True
            self.current_chat_id = event.chat_id  # Store chat ID
            self.release_task = asyncio.create_task(self.release_pokemon())
            await event.edit(" Pokémon auto-release started in this chat!")  # Edit instead of sending a new message
        else:
            await event.edit(" Release is already running!")  # Edit instead of sending a new message

    async def stop_releasing(self, event):
        """Stops the release process"""
        if self.running:
            self.running = False
            if self.release_task:
                self.release_task.cancel()
                self.release_task = None
            self.current_chat_id = None  # Reset the chat ID
            await event.edit(" Pokémon auto-release stopped!")  # Edit instead of sending a new message
        else:
            await event.edit(" No active release process.")  # Edit instead of sending a new message
