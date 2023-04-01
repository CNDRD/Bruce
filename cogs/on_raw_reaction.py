from func.supabase import supabase

import disnake
from disnake.ext import commands

diskito_id = 402356550133350411
valid_rr_channels = [694161229475872808, 703289966842871868]


class RrRpEc(commands.Cog):
    def __init__(self, client):
        """Reaction Roles & Reaction Points & Emotes Count."""
        self.client = client

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: disnake.RawReactionActionEvent):
        # Doesn't work when a bot adds an emoji
        if payload.member.bot:
            return

        if payload.channel_id in valid_rr_channels:
            guild = self.client.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)
            role = disnake.utils.get(guild.roles, name=payload.emoji.name)  # Role name & Emoji name HAVE to be the same.

            if role is not None and member is not None:

                rr_ch = self.client.get_channel(payload.channel_id)
                rr_msg = await rr_ch.fetch_message(payload.message_id)

                # Add Role
                if role not in member.roles:
                    await member.add_roles(role)
                # Remove Role
                elif role in member.roles:
                    await member.remove_roles(role)

                await rr_msg.remove_reaction(payload.emoji, member)

            roles = [role.id for role in member.roles]
            supabase.from_('users').update({'roles': roles}).eq('id', member.id).execute()


def setup(client):
    client.add_cog(RrRpEc(client))
