from telethon import events
from telethon.tl.functions.channels import GetParticipantRequest, EditBannedRequest, EditAdminRequest
from telethon.tl.types import ChatBannedRights, ChatAdminRights, ChannelParticipantCreator

# Store chat-specific data
chat_data = {
    # Format: {chat_id: {"muted_users": set(), "banned_users": set(), "admins": set()}}
}

class AdminManager:
    """Handles admin commands like ban, unban, mute, unmute, promote, and demote."""

    def __init__(self, client):
        self.client = client

    async def is_admin(self, chat, user_id):
        """Returns the participant object if the user is an admin, otherwise None."""
        try:
            participant = await self.client(GetParticipantRequest(chat, user_id))
            if hasattr(participant.participant, 'admin_rights'):
                return participant.participant
            return None
        except Exception:
            return None

    async def has_delete_rights(self, chat, user_id):
        """Checks if a user has the 'Delete Messages' admin right."""
        admin = await self.is_admin(chat, user_id)
        return admin and getattr(admin.admin_rights, 'delete_messages', False)

    async def _get_chat_data(self, chat_id):
        """Returns the data for a specific chat, initializing it if necessary."""
        if chat_id not in chat_data:
            chat_data[chat_id] = {"muted_users": set(), "banned_users": set(), "admins": set()}
        return chat_data[chat_id]

    async def mute_user(self, event):
        """Mutes a user in the specific chat where the command was used."""
        chat = await event.get_chat()
        sender = await event.get_sender()

        # Ensure sender is an admin
        if not await self.is_admin(chat, sender.id):
            return await event.edit("You need to be an admin to use this command.")

        # Ensure the sender has "Delete Messages" permission
        sender_admin = await self.is_admin(chat, sender.id)
        if not sender_admin or not getattr(sender_admin.admin_rights, 'delete_messages', False):
            return await event.edit("You need 'Delete Messages' permission to mute admins!")

        # Get the target user
        reply = await event.get_reply_message()
        if not reply or not reply.sender:
            return await event.edit("Reply to a user to mute them!")

        target = reply.sender
        target_admin = await self.is_admin(chat, target.id)

        # Prevent muting the group Owner
        if isinstance(target_admin, ChannelParticipantCreator):
            return await event.edit("You can't mute the group owner!")

        # Proceed with muting (since sender has 'Delete Messages' permission)
        await self.client(EditBannedRequest(
            chat.id, target.id,
            ChatBannedRights(until_date=None, send_messages=True)
        ))

        # Add the user to the muted list for this specific chat
        chat_info = await self._get_chat_data(chat.id)
        chat_info["muted_users"].add(target.id)

        await event.edit(f"Muted {target.first_name} in this chat!")

    async def unmute_user(self, event):
        """Unmutes a user in the specific chat where the command was used."""
        chat = await event.get_chat()

        if not await self.is_admin(chat, event.sender_id):
            return await event.edit("You need to be an admin to use this command.")

        if event.reply_to_msg_id:
            reply = await event.get_reply_message()
            user = reply.sender_id
        else:
            return await event.edit("Reply to a user to unmute them!")

        # Check if the user is muted in this specific chat
        chat_info = await self._get_chat_data(chat.id)
        if user not in chat_info["muted_users"]:
            return await event.edit("This user is not muted in this chat!")

        # Unmute the user
        await self.client(EditBannedRequest(
            chat.id, user,
            ChatBannedRights(until_date=None)  # Unmute the user
        ))

        # Remove the user from the muted list for this specific chat
        chat_info["muted_users"].discard(user)
        await event.edit(f"Unmuted {user} in this chat!")

    async def ban_user(self, event):
        """Bans a user in the specific chat where the command was used."""
        chat = await event.get_chat()

        if not await self.is_admin(chat, event.sender_id):
            return await event.edit("You need to be an admin to use this command.")

        if event.reply_to_msg_id:
            reply = await event.get_reply_message()
            user = reply.sender_id
        else:
            return await event.edit("Reply to a user to ban them!")

        # Ban the user
        await self.client(EditBannedRequest(
            chat.id, user,
            ChatBannedRights(until_date=None, view_messages=True)
        ))

        # Add the user to the banned list for this specific chat
        chat_info = await self._get_chat_data(chat.id)
        chat_info["banned_users"].add(user)

        await event.edit(f"Banned {user} in this chat!")

    async def unban_user(self, event):
        """Unbans a user in the specific chat where the command was used."""
        chat = await event.get_chat()

        if not await self.is_admin(chat, event.sender_id):
            return await event.edit("You need to be an admin to use this command.")

        if event.reply_to_msg_id:
            reply = await event.get_reply_message()
            user = reply.sender_id
        else:
            return await event.edit("Reply to a user to unban them!")

        # Check if the user is banned in this specific chat
        chat_info = await self._get_chat_data(chat.id)
        if user not in chat_info["banned_users"]:
            return await event.edit("This user is not banned in this chat!")

        # Unban the user
        await self.client(EditBannedRequest(
            chat.id, user,
            ChatBannedRights(until_date=None)
        ))

        # Remove the user from the banned list for this specific chat
        chat_info["banned_users"].discard(user)
        await event.edit(f"Unbanned {user} in this chat!")

    async def promote_user(self, event):
        """Promotes a user to admin in the specific chat where the command was used."""
        chat = await event.get_chat()

        if not await self.is_admin(chat, event.sender_id):
            return await event.edit("You need to be an admin to use this command.")

        if event.reply_to_msg_id:
            reply = await event.get_reply_message()
            user = reply.sender_id
        else:
            return await event.edit("Reply to a user to promote them!")

        # Check if the user is already an admin
        if await self.is_admin(chat, user):
            return await event.edit("This user is already an admin!")

        # Promote the user
        rights = ChatAdminRights(
            post_messages=True,
            delete_messages=True,
            ban_users=True,
            invite_users=True,
            change_info=True,
            pin_messages=True
        )
        await self.client(EditAdminRequest(chat.id, user, rights, rank="Admin"))

        # Add the user to the admins list for this specific chat
        chat_info = await self._get_chat_data(chat.id)
        chat_info["admins"].add(user)

        await event.edit(f"Promoted {user} to Admin in this chat!")

    async def demote_user(self, event):
        """Demotes an admin back to a normal user in the specific chat where the command was used."""
        chat = await event.get_chat()

        if not await self.is_admin(chat, event.sender_id):
            return await event.edit("You need to be an admin to use this command.")

        if event.reply_to_msg_id:
            reply = await event.get_reply_message()
            user = reply.sender_id
        else:
            return await event.edit("Reply to a user to demote them!")

        # Check if the user is an admin
        if not await self.is_admin(chat, user):
            return await event.edit("This user is not an admin!")

        # Demote the user
        rights = ChatAdminRights()
        await self.client(EditAdminRequest(chat.id, user, rights, rank=""))

        # Remove the user from the admins list for this specific chat
        chat_info = await self._get_chat_data(chat.id)
        chat_info["admins"].discard(user)

        await event.edit(f"Demoted {user} to a normal user in this chat!")

    async def delete_muted_messages(self, event):
        """Deletes messages sent by muted users in the specific chat."""
        chat = await event.get_chat()
        chat_info = await self._get_chat_data(chat.id)
        if event.sender_id in chat_info["muted_users"]:
            await event.delete()

    def get_event_handlers(self):
        """Returns event handlers for admin commands."""
        return [
            {"callback": self.mute_user, "event": events.NewMessage(pattern=r"\.mute$", outgoing=True)},
            {"callback": self.unmute_user, "event": events.NewMessage(pattern=r"\.unmute$", outgoing=True)},
            {"callback": self.ban_user, "event": events.NewMessage(pattern=r"\.ban$", outgoing=True)},
            {"callback": self.unban_user, "event": events.NewMessage(pattern=r"\.unban$", outgoing=True)},
            {"callback": self.promote_user, "event": events.NewMessage(pattern=r"\.promote$", outgoing=True)},
            {"callback": self.demote_user, "event": events.NewMessage(pattern=r"\.demote$", outgoing=True)},
            {"callback": self.delete_muted_messages, "event": events.NewMessage()},
            ]
