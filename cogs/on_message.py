from func.supabase import supabase
from func.levels import xp_from_level, rank_name

from disnake.ext import commands
import disnake

from pytz import timezone
from numpy.random import randint
from numpy.random import seed
from datetime import datetime
from disnake.utils import get


class OnMessage(commands.Cog):
    def __init__(self, client):
        """Leveling system & Auto-deletion of `User xyz pinned a message` messages."""
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):
        # We don't want the bot giving XP to itself now do we
        if message.author.bot:
            return

        # Don't work in DMs
        if isinstance(message.channel, disnake.channel.DMChannel):
            return

        # Auto-delete "pinned" & "thread has been created" messages
        if message.type == disnake.MessageType.pins_add or message.type == disnake.MessageType.thread_created:
            return await message.delete()

        # Basic-ass variables
        now = datetime.now(timezone('UTC'))

        # User Data
        user_data = supabase.from_('users').select('level, xp, last_xp, messages').eq('id', message.author.id).execute()
        current_lvl = user_data.data[0]['level']
        current_xp = user_data.data[0]['xp']
        last_xp_get = datetime.strptime(user_data.data[0]['last_xp'], '%Y-%m-%dT%H:%M:%S.%f%z')
        messages_count = user_data.data[0]['messages']

        # Get the time since the user last posted a message
        # since_last_mess = now - last_xp_get
        since_last_mess = (now - last_xp_get).total_seconds()

        if since_last_mess > 60:

            # Calculate new XP
            seed(int(since_last_mess))
            xp_to_add = randint(15, 25)
            new_xp = xp_to_add + current_xp

            # +100 extra XP for a message in a new day
            if since_last_mess > 86400:
                new_xp += 100

            if new_xp >= xp_from_level(current_lvl+1):
                # Level based roles
                # Removes the old role and gives a new one, is applicable
                add_r = rank_name(current_lvl+1)
                del_r = rank_name(current_lvl)
                if add_r != del_r:
                    new_r = get(message.author.guild.roles, name=add_r)
                    await message.author.add_roles(new_r)
                    old_r = get(message.author.guild.roles, name=del_r)
                    await message.author.remove_roles(old_r)

                roles = [str(role.id) for role in message.author.roles]
                data = {"level": current_lvl + 1, "last_xp": str(now), "xp": new_xp, "messages": messages_count + 1, "roles": roles}

            else:
                # No level change
                data = {"xp": new_xp, "last_xp": str(now), "messages": messages_count + 1}

        else:
            # Too Fast (less than 60s since last message)
            data = {"messages": messages_count + 1}

        # Update users individual stats & server total stats
        supabase.from_('users').update(data).eq('id', message.author.id).execute()


def setup(client):
    client.add_cog(OnMessage(client))
