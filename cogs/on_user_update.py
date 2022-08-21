from func.firebase_init import db

from disnake.ext import commands


class OnUserUpdate(commands.Cog):
    def __init__(self, client):
        """User updates their username or avatar, we update that in the database."""
        self.client = client

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        db.child("users").child(after.id).update({
            "username": str(after),
        })

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        db.child("users").child(after.id).update({
            "avatar_url": str(after.display_avatar.with_size(4096)),
        })


def setup(client):
    client.add_cog(OnUserUpdate(client))
