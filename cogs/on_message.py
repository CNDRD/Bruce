from func.firebase_init import db
from func.levels import xp_from_level, rank_name

from disnake.ext import commands
import disnake

import time
from numpy.random import randint
from numpy.random import seed
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
        now = int(time.time())
        uid = message.author.id

        # Server Totals Data
        st = db.child('serverTotals').get().val()
        st_levels = st.get('levels', 0)
        st_messages = st.get('messages', 0)
        st_xp = st.get('xp', 0)

        # User Data
        ud = db.child('users').child(uid).get().val()
        current_lvl = ud.get('level', 0)
        current_xp = ud.get('xp', 0)
        last_xp_get = ud.get('last_xp_get', 0)
        messages_count = ud.get('messages_count', 0)
        money = ud.get('money', 0)

        # Get the time since the user last posted a message
        since_last_mess = now - last_xp_get

        if since_last_mess > 60:

            # Calculate new XP
            seed(now)
            xp_to_add = randint(15, 25)
            new_xp = xp_to_add + current_xp

            # +100 extra XP for a message in a new day
            if since_last_mess > 86400:
                new_xp += 100

            if new_xp >= xp_from_level(current_lvl+1):
                data = {
                    'level': current_lvl + 1,
                    'last_xp_get': now,
                    'xp': new_xp,
                    'messages_count': messages_count + 1,
                    'money': money + xp_to_add
                }
                server_totals = {
                    'xp': st_xp + xp_to_add,
                    'messages': st_messages + 1,
                    'levels': st_levels + 1
                }

                # Level based roles
                # Removes the old role and gives a new one, is applicable
                add_r = rank_name(current_lvl+1)
                del_r = rank_name(current_lvl)
                if add_r != del_r:
                    new_r = get(message.author.guild.roles, name=add_r)
                    await message.author.add_roles(new_r)
                    old_r = get(message.author.guild.roles, name=del_r)
                    await message.author.remove_roles(old_r)
            else:
                # No level change
                data = {
                    'xp': new_xp,
                    'last_xp_get': now,
                    'messages_count': messages_count + 1,
                    'money': money + xp_to_add
                }

                server_totals = {
                    'xp': st_xp + xp_to_add,
                    'messages': st_messages + 1
                }

        else:
            # Too Fast (less than 60s since last message)
            data = {'messages_count': messages_count + 1}
            server_totals = {'messages': st_messages + 1}

        # Update users individual stats & server total stats
        db.child('users').child(uid).update(data)
        db.child('serverTotals').update(server_totals)


def setup(client):
    client.add_cog(OnMessage(client))
