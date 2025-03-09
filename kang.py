import os
import asyncio
from telethon import events
from telethon.tl.functions.messages import GetStickerSetRequest
from telethon.tl.types import InputStickerSetShortName
from telethon.errors import StickersetInvalidError
from constants import TEMP_DOWNLOAD_PATH

class KangManager:
    def __init__(self, client):
        self._client = client

    async def kang(self, event):
        """Handles the `.kang` command to steal stickers or images."""
        reply = await event.get_reply_message()
        if not reply:
            return await event.edit("Reply to a sticker or image to kang!")

        await event.edit("Kanging sticker...")

        # Default emoji and pack name
        emoji = "🤔"
        pack_name = "KangPack"

        # Parse arguments
        args = event.raw_text.split(" ", maxsplit=2)
        if len(args) == 2:
            if args[1].startswith(":"):
                emoji = args[1]
            else:
                pack_name = args[1]
        elif len(args) == 3:
            emoji, pack_name = args[1], args[2]

        # Validate emoji
        if not self.is_valid_emoji(emoji):
            return await event.edit("Invalid emoji. Please provide a single valid emoji.")

        # Download the sticker/image
        sticker_path = os.path.join(TEMP_DOWNLOAD_PATH, "kang.webp")
        await reply.download_media(file=sticker_path)

        # Upload and add sticker to pack
        success = await self.add_sticker_to_pack(event, sticker_path, emoji, pack_name)
        if success:
            await event.edit(f"Sticker kanged successfully! {emoji}\nPack: `{pack_name}`")
        else:
            await event.edit("Failed to add sticker. Try again later!")

        # Clean up the temporary file
        if os.path.exists(sticker_path):
            os.remove(sticker_path)

    async def add_sticker_to_pack(self, event, sticker_path, emoji, pack_name):
        """Adds the sticker to the user's sticker pack."""
        user = await event.client.get_me()
        pack_short_name = f"{user.id}_{pack_name}_kang"

        try:
            # Check if pack exists
            sticker_set = await event.client(GetStickerSetRequest(InputStickerSetShortName(pack_short_name)))
        except StickersetInvalidError:
            sticker_set = None

        if not sticker_set:
            # Create a new sticker pack
            return await self.create_new_sticker_pack(event, sticker_path, emoji, pack_short_name)

        # Add sticker to existing pack
        return await self.add_sticker_to_existing_pack(event, sticker_path, emoji, pack_short_name)

    async def create_new_sticker_pack(self, event, sticker_path, emoji, pack_short_name):
        """Creates a new sticker pack and adds the sticker."""
        client = event.client

        async def send_and_wait(text):
            await client.send_message("Stickers", text)
            await asyncio.sleep(2)  # Give some time for the bot to process

        await send_and_wait("/newpack")
        await send_and_wait(pack_short_name)
        await client.send_file("Stickers", sticker_path, force_document=False)
        await send_and_wait(emoji)
        await send_and_wait("/publish")
        await send_and_wait(pack_short_name)
        
        return True

    async def add_sticker_to_existing_pack(self, event, sticker_path, emoji, pack_short_name):
        """Adds a sticker to an existing sticker pack."""
        client = event.client

        async def send_and_wait(text):
            await client.send_message("Stickers", text)
            await asyncio.sleep(2)

        await send_and_wait("/addsticker")
        await send_and_wait(pack_short_name)
        await client.send_file("Stickers", sticker_path, force_document=False)
        await send_and_wait(emoji)
        await send_and_wait("/done")

        return True

    def is_valid_emoji(self, emoji):
        """Checks if the provided emoji is valid."""
        return len(emoji) == 1 and emoji in "😀😃😄😁😆😅😂🤣😊😇🙂🙃😉😌😍🥰😘😗😙😚😋😛😝😜🤪🤨🧐🤓😎🤩🥳😏😒😞😔😟😕🙁☹️😣😖😫😩🥺😢😭😤😠😡🤬🤯😳🥵🥶😱😨😰😥😓🤗🤔🤭🤫🤥😶😐😑😬🙄😯😦😧😮😲🥱😴🤤😪😵🤐🥴🤢🤮🤧😷🤒🤕🤑🤠😈👿👹👺🤡💩👻💀☠️👽👾🤖🎃😺😸😹😻😼😽🙀😿😾"

    def get_event_handlers(self):
        """Returns event handlers for kang."""
        return [
            {'callback': self.kang, 'event': events.NewMessage(pattern=r"\.kang(?: .+)?", outgoing=True)},
        ]
