from func.firebase_init import db

from disnake.ext import commands



class OnUserUpdate(commands.Cog):
    def __init__(self, client):
        """User updates their username or avatar, we update that in the database"""
        self.client = client


    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        data = {
            "username": str(after),
            "avatar_url":str(after.avatar_url_as(size=4096))
        }
        db.child('users').child(after.id).update(data)


def setup(client):
    client.add_cog(OnUserUpdate(client))
