from telethon import events
from telethon.tl.functions.channels import GetParticipantRequest, EditBannedRequest, EditAdminRequest
from telethon.tl.types import ChatBannedRights, ChatAdminRights, ChannelParticipantCreator

muted_users = set()  # Store muted users in memory

class AdminManager:
    """Handles admin commands like ban, unban, mute, unmute, promote, and demote."""

    def __init__(self, client):
        self.client = client

    async def is_admin(self, chat, user_id):
        """Returns the participant's admin rights if they are an admin."""
        try:
            participant = await self.client(GetParticipantRequest(chat, user_id))
            return participant.participant  # Returns admin info (or None if not an admin)
        except Exception:
            return None  

    async def has_delete_rights(self, chat, user_id):
        """Checks if a user has the 'Delete Messages' admin right."""
        admin = await self.is_admin(chat, user_id)
        return bool(admin and getattr(admin.admin_rights, 'delete_messages', False))

    async def mute_user(self, event):
        """Mutes a user, including admins if the sender has 'Delete Messages' permission."""
        chat = await event.get_chat()
        sender = await event.get_sender()

        # Ensure sender is an admin
        if not await self.is_admin(chat, sender.id):
            return await event.edit("You need to be an admin to use this command.")

        # Ensure the sender has "Delete Messages" permission
        if not await self.has_delete_rights(chat, sender.id):
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
        muted_users.add(target.id)  # Store muted users
        await event.edit(f"Muted {target.first_name}!")

    async def unmute_user(self, event):
        """Unmutes a user."""
        args = event.pattern_match.group(1)
        chat = await event.get_chat()

        if not await self.is_admin(chat, event.sender_id):
            return await event.edit("You need to be an admin to use this command.")

        if event.reply_to_msg_id:
            reply = await event.get_reply_message()
            user = reply.sender_id
        elif args:
            try:
                user = int(args) if args.isdigit() else await self.client.get_entity(args)
            except Exception as e:
                return await event.edit(f"Invalid user ID/username: {e}")
        else:
            return await event.edit("Reply to a user or provide a user ID/username.")

        await self.client(EditBannedRequest(chat.id, user, ChatBannedRights()))
        muted_users.discard(user)  # Remove user from muted list
        await event.edit(f"Unmuted {user}!")

    async def delete_muted_messages(self, event):
        """Deletes messages sent by muted users."""
        if event.sender_id in muted_users:
            await event.delete()

    async def ban_user(self, event):
        """Bans a user from the chat."""
        args = event.pattern_match.group(1)
        chat = await event.get_chat()

        if not await self.is_admin(chat, event.sender_id):
            return await event.edit("You need to be an admin to use this command.")

        if event.reply_to_msg_id:
            reply = await event.get_reply_message()
            user = reply.sender_id
        elif args:
            try:
                user = int(args) if args.isdigit() else await self.client.get_entity(args)
            except Exception as e:
                return await event.edit(f"Invalid user ID/username: {e}")
        else:
            return await event.edit("Reply to a user or provide a user ID/username.")

        await self.client(EditBannedRequest(chat.id, user, ChatBannedRights(until_date=None, view_messages=True)))
        await event.edit(f"Banned {user}!")

    async def unban_user(self, event):
        """Unbans a user from the chat."""
        args = event.pattern_match.group(1)
        chat = await event.get_chat()

        if not await self.is_admin(chat, event.sender_id):
            return await event.edit("You need to be an admin to use this command.")

        if event.reply_to_msg_id:
            reply = await event.get_reply_message()
            user = reply.sender_id
        elif args:
            try:
                user = int(args) if args.isdigit() else await self.client.get_entity(args)
            except Exception as e:
                return await event.edit(f"Invalid user ID/username: {e}")
        else:
            return await event.edit("Reply to a user or provide a user ID/username.")

        await self.client(EditBannedRequest(chat.id, user, ChatBannedRights()))
        await event.edit(f"Unbanned {user}!")

    async def promote_user(self, event):
        """Promotes a user to admin."""
        args = event.pattern_match.group(1)
        chat = await event.get_chat()

        if not await self.is_admin(chat, event.sender_id):
            return await event.edit("You need to be an admin to use this command.")

        if event.reply_to_msg_id:
            reply = await event.get_reply_message()
            user = reply.sender_id
        elif args:
            try:
                user = int(args) if args.isdigit() else await self.client.get_entity(args)
            except Exception as e:
                return await event.edit(f"Invalid user ID/username: {e}")
        else:
            return await event.edit("Reply to a user or provide a user ID/username.")

        rights = ChatAdminRights(post_messages=True, delete_messages=True, ban_users=True, invite_users=True, change_info=True, pin_messages=True)
        await self.client(EditAdminRequest(chat.id, user, rights, rank="Admin"))
        await event.edit(f"Promoted {user} to Admin!")

    async def demote_user(self, event):
        """Demotes an admin back to a normal user."""
        args = event.pattern_match.group(1)
        chat = await event.get_chat()

        if not await self.is_admin(chat, event.sender_id):
            return await event.edit("You need to be an admin to use this command.")

        if event.reply_to_msg_id:
            reply = await event.get_reply_message()
            user = reply.sender_id
        elif args:
            try:
                user = int(args) if args.isdigit() else await self.client.get_entity(args)
            except Exception as e:
                return await event.edit(f"Invalid user ID/username: {e}")
        else:
            return await event.edit("Reply to a user or provide a user ID/username.")

        rights = ChatAdminRights()
        await self.client(EditAdminRequest(chat.id, user, rights, rank=""))
        await event.edit(f"Demoted {user} to a normal user!")
