from telethon import events
from telethon.tl.functions.photos import DeletePhotosRequest, UploadProfilePhotoRequest
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.errors import StickersetInvalidError

import os
from constants import TEMP_DOWNLOAD_PATH

class CloneManager:
    """Handles cloning and reverting user profiles."""

    def __init__(self, client):
        self._client = client
        self.original_profile = {}

    async def clone(self, event):
        """Clones a target user's profile (name, bio, username, and profile picture)."""
        reply = await event.get_reply_message()
        if not reply or not reply.sender:
            await event.edit("Reply to a user's message to clone their profile.")
            return

        user = reply.sender

        try:
            # Save original profile details
            my_profile = await self._client(GetFullUserRequest("me"))

            self.original_profile = {
                "first_name": my_profile.user.first_name or "",
                "last_name": my_profile.user.last_name or "",
                "bio": my_profile.about or "",
                "username": my_profile.user.username or "",
                "photos": await self._client.get_profile_photos("me")
            }

            # Get target user's profile details
            target_profile = await self._client(GetFullUserRequest(user.id))
            target_user = target_profile.user  # Extract `user` object

            # Update name, bio, and username
            await self._client(UpdateProfileRequest(
                first_name=target_user.first_name or "",
                last_name=target_user.last_name or "",
                about=target_profile.about or "",
                username=target_user.username or ""
            ))

            # Upload latest profile picture if available
            target_photos = await self._client.get_profile_photos(user)
            if target_photos:
                photo_path = await self._client.download_media(target_photos[0])
                await self._client(UploadProfilePhotoRequest(file=await self._client.upload_file(photo_path)))
                os.remove(photo_path)  # Clean up temp file

            await event.edit(f"Cloned **{target_user.first_name}**'s profile!")

        except Exception as e:
            await event.edit(f"An error occurred: {str(e)}")

    async def revert(self, event):
        """Reverts to the original profile and removes the cloned profile picture."""
        if not self.original_profile:
            await event.edit("No original profile saved. Clone first!")
            return

        try:
            # Restore name, bio, and username
            await self._client(UpdateProfileRequest(
                first_name=self.original_profile["first_name"],
                last_name=self.original_profile["last_name"],
                about=self.original_profile["bio"],
                username=self.original_profile["username"]
            ))

            # Remove cloned profile picture
            current_photos = await self._client.get_profile_photos("me")
            if current_photos:
                await self._client(DeletePhotosRequest([current_photos[0]]))

            # Clear stored profile
            self.original_profile = {}

            await event.edit("Profile reverted to original!")

        except Exception as e:
            await event.edit(f"An error occurred: {str(e)}")

    def get_event_handlers(self):
        """Returns event handlers for clone and revert commands."""
        return [
            {"callback": self.clone, "event": events.NewMessage(pattern=r"\.clone$", outgoing=True)},
            {"callback": self.revert, "event": events.NewMessage(pattern=r"\.revert$", outgoing=True)},
        ]
