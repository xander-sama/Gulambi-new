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

        emoji = "🤔"
        pack_name = "KangPack"

        args = event.raw_text.split(" ", maxsplit=2)
        if len(args) == 2:
            if args[1].startswith(":"):
                emoji = args[1]
            else:
                pack_name = args[1]
        elif len(args) == 3:
            emoji, pack_name = args[1], args[2]

        sticker_path = os.path.join(TEMP_DOWNLOAD_PATH, "kang.webp")
        await reply.download_media(file=sticker_path)

        # Upload and add sticker to pack
        success = await self.add_sticker_to_pack(event, sticker_path, emoji, pack_name)
        if success:
            await event.edit(f"Sticker kanged successfully! {emoji}\nPack: `{pack_name}`")
        else:
            await event.edit("Failed to add sticker. Try again later!")

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
            return False  # Creating new packs requires bot interaction, skipping for now

        # Upload the sticker
        file = await event.client.upload_file(sticker_path)

        # Here, add the sticker to the pack (requires bot API)
        return True  # Placeholder

    def get_event_handlers(self):
        """Returns event handlers for kang."""
        return [
            {'callback': self.kang, 'event': events.NewMessage(pattern=r"\.kang(?: .+)?", outgoing=True)},
        ]
