from func.supabase import supabase

from disnake.ext import commands
from disnake import Member


class OnUserUpdate(commands.Cog):
    def __init__(self, client):
        """User updates their username or avatar, we update that in the database."""
        self.client = client

    @commands.Cog.listener()
    async def on_user_update(self, before: Member, after: Member):
        supabase.from_('users').update({'username': str(after)}).eq('id', after.id).execute()

    @commands.Cog.listener()
    async def on_member_update(self, before: Member, after: Member):
        roles = [str(role.id) for role in after.roles]
        avatar = str(after.display_avatar.with_size(4096))

        supabase.from_('users').update({'roles': roles, 'avatar': avatar}).eq('id', after.id).execute()


def setup(client):
    client.add_cog(OnUserUpdate(client))
