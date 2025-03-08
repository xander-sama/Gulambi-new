import asyncio
from telethon import events
from loguru import logger
import constants

class PokemonReleaseManager:
    def __init__(self, client):
        self.client = client
        self.release_task = None  
        self.running = False  
        self.current_chat_id = None  
        self.pokemon_to_release = []  

    async def release_pokemon(self):
        """Releases Pokémon in the chat where .release on was used"""
        while self.running:
            try:
                if not self.current_chat_id:
                    logger.warning("No active chat ID for release. Stopping...")
                    self.running = False
                    return  

                for pokemon in self.pokemon_to_release:  
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
        """Starts auto-releasing Pokémon. Users can specify Pokémon to release."""
        args = event.raw_text.split()[1:]  

        if not args:
            await event.respond(" Please provide Pokémon names to release.\n\n**Example:** `.release on Pikachu Bulbasaur Charmander`")
            return

        self.pokemon_to_release = args  

        if not self.running:
            self.running = True
            self.current_chat_id = event.chat_id  
            self.release_task = asyncio.create_task(self.release_pokemon())
            await event.respond(f" Auto-releasing: {', '.join(self.pokemon_to_release)} in this chat!")  
        else:
            await event.respond(" Release is already running!")

    async def stop_releasing(self, event):
        """Stops the release process"""
        if self.running:
            self.running = False
            if self.release_task:
                self.release_task.cancel()
                self.release_task = None
            self.current_chat_id = None  
            self.pokemon_to_release = []  
            await event.respond("Pokémon auto-release stopped!")  
        else:
            await event.respond("No active release process.")
