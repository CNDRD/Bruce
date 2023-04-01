from func.supabase import supabase
from func.levels import rank_name
from func.stuff import ordinal

import disnake
from disnake.utils import get
from disnake.ext import commands

from humanfriendly import format_timespan
from datetime import datetime


testing = True


class InNOut(commands.Cog):
    def __init__(self, client):
        """Not so simple 'in & out' events."""
        self.client = client
        self.test_account_id = 552570700171313187 if not testing else 0
        self.ino_channel = self.client.get_channel(731024736456409159 if not testing else 694165272155783248)
        self.green_arrow = self.client.get_emoji(784822110723112974)
        self.yellow_arrow = self.client.get_emoji(784822110622974014)
        self.red_arrow = self.client.get_emoji(784822110836097094)

    @commands.Cog.listener()
    async def on_member_join(self, member: disnake.Member):
        # Do not harass the in-n-out channel with test account
        if member.id == self.test_account_id:
            return

        # No welcome messages for bots
        # But autorole for them, so they all have the same color
        if member.bot:
            return await member.add_roles(get(member.guild.roles, name="Hosts"))

        member_data = supabase.from_('users').select('level, leaves, roles').eq('id', member.id).execute()

        if member_data.data:
            # The user has joined the server before at least once
            msg = f"{self.yellow_arrow} **{member.mention}** has just ***joined*** for the {ordinal(member_data.data[0]['leaves']+1)} time!"

            if member_data.data[0]['roles']:
                for role_id in member_data.data[0]['roles']:
                    if role_id in [402356550133350411]:
                        continue
                    role = get(member.guild.roles, id=role_id)
                    await member.add_roles(role)
            else:
                await member.add_roles(get(member.guild.roles, name=member_data.data[0]['level']))
                await member.add_roles(get(member.guild.roles, name="Jeetard"))

            supabase.from_('users').update({'in_server': True}).eq('id', member.id).execute()

        else:
            # First join ever
            msg = f"{self.green_arrow} **{member.mention}** has just ***joined!***"

            # Give the user the 0-level role
            await member.add_roles(get(member.guild.roles, name=rank_name(0)))

            data = {
                "id": member.id,
                "username": str(member),
                "avatar": str(member.display_avatar.with_size(4096)),
                "cicina": {
                    "average": 0,
                    "count": 0,
                    "last": "2020-1-1",
                    "longest": 0,
                },
                "roles": [role.id for role in member.roles],
            }
            supabase.from_('users').insert(data).execute()

        await self.ino_channel.send(msg)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        # Do not harass the in-n-out channel with test account or bots
        if member.id == self.test_account_id or member.bot:
            return

        member_data = supabase.from_('users').select('username, level, leaves').eq('id', member.id).execute()
        username = member_data.data[0]['username']
        leaves = member_data.data[0]['leaves'] + 1

        # Update users individual stats
        supabase.from_('users').update({"leaves": leaves, "in_server": False}).eq('id', member.id).execute()

        # Basic-ass variables
        joined = member.joined_at.replace(tzinfo=None)
        left = datetime.utcnow()

        diff = (left - joined)
        stayed = format_timespan(int(diff.total_seconds()))

        msg = None

        async for ban in member.guild.bans():
            if ban.user.id == member.id:
                msg = f"{self.red_arrow} **{username}** has just been banned! (Reason: {ban.reason or 'No Reason Given'})"

        if not msg:
            if leaves == 1:
                msg = f"{self.red_arrow} **{username}** has just ***left*** us! Was here for *{stayed}*."
            else:
                msg = f"{self.red_arrow} **{username}** has just ***left*** us for the {ordinal(leaves)} time! Was here for *{stayed}*."

        view = disnake.ui.View()
        view.add_item(disnake.ui.Button(label=str(username), url=f"discord://-/users/{member.id}"))

        clown = await self.ino_channel.send(msg, view=view)

        # Automatically adds 🤡 emoji to every leave message
        # if they left within 15 minutes of joining it also adds another clown emoji
        await clown.add_reaction("🤡")
        if int(diff.total_seconds()) < 900:
            e = get(self.client.emojis, name="HonkHonk")
            await clown.add_reaction(e)


def setup(client):
    client.add_cog(InNOut(client))
