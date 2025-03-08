from telethon import events

class PurgeManager:
    """Handles message purging functionality."""

    def __init__(self, client):
        self._client = client

    async def purge_messages(self, event):
        """Handles the `.purge <count>` command to delete messages."""
        args = event.raw_text.split()
        if len(args) != 2 or not args[1].isdigit():
            return await event.reply("Usage: `.purge <count>`")

        count = int(args[1])
        if count <= 0:
            return await event.reply("Count must be greater than 0.")

        chat = event.chat_id
        to_delete = []
        async for message in self._client.iter_messages(chat, limit=count):
            to_delete.append(message.id)

        if to_delete:
            await self._client.delete_messages(chat, to_delete)
            confirmation = await event.reply(f"Deleted {len(to_delete)} messages!")
            await confirmation.delete(delay=3)
