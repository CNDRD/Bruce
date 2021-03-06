from func.console_logging import cl
from func.stuff import add_spaces
from func.levels import *

import pyrebase, discord, time, yaml, json
from discord.ext import commands
from numpy.random import randint
from numpy.random import seed
from discord.utils import get
from numerize import numerize

## Config Load ##
config = yaml.safe_load(open('config.yml'))
valid_post_channels = config.get('valid_post_channels')

## Firebase Database ##
db = pyrebase.initialize_app( json.loads(config.get('firebase')) ).database()


class OnMessage(commands.Cog):
    def __init__(self, client):
        """
        Leveling system.
        Auto-deleting `User xyz pinned a message` messages.
        """
        self.client = client


    @commands.Cog.listener()
    async def on_message(self, message):
        # cl('', 'OnMessage', 'on_message')
        # We don't want the bot giving XP to itself now do we
        if message.author.bot:
            return

        # Auto-delete "xyz has pinned a message in this channel" messages
        if message.type == discord.MessageType.pins_add:
            await message.delete()
            return

        # Don't work in DM's
        try:
            if message.channel.id == message.author.dm_channel.id:
                return
        except:
            ...
            # Not the most elegant solution but it just throws error
            # every time a message is not sent in DM's
            # and i cannot be bothered to read the docs to fix this..

        # Basic-ass variables
        now = int(time.time())
        uid = message.author.id
        level_up = False

        # Server Totals Data
        st = db.child('serverTotals').get().val()
        st_levels = st.get('levels')
        st_messages = st.get('messages')
        st_xp = st.get('xp')

        # User Data
        ud = db.child('users').child(uid).get().val()
        current_lvl = ud.get('level')
        current_xp = ud.get('xp')
        last_xp_get = ud.get('last_xp_get')
        messages_count = ud.get('messages_count')

        # Get fucked in the mouth if you try to speak and your level is less than 5
        if current_lvl <= 5 and message.attachments == [] and message.channel.id in valid_post_channels:
            await message.delete()
            embed = discord.Embed(colour=discord.Colour(0xb53737),title="You need to be at least level 5 to post shit like that in here..")
            embed.set_author(name=message.author.name, url='https://chuckwalla-69.web.app/leader.html')
            await message.channel.send(embed=embed, delete_after=10)
            return

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
                # Level-Up
                level_up = True
                data = {'level':current_lvl+1, 'last_xp_get':now, 'xp':new_xp, 'messages_count':messages_count+1}
                server_totals = {'xp':st_xp + xp_to_add, 'messages':st_messages+1, 'levels':st_levels+1}

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
                data = {'xp':new_xp,
                        'last_xp_get':now,
                        'messages_count':messages_count+1}

                server_totals = {'xp':st_xp + xp_to_add, 'messages':st_messages+1}

        else:
            # Too Fast (less than 60s since last message)
            data = {'messages_count':messages_count+1}
            server_totals = {'messages':st_messages+1}

        # Update users individual stats & server total stats
        db.child('users').child(uid).update(data)
        db.child('serverTotals').update(server_totals)

        # Send a level up message if there was a level up
        # could be done above, but this way it's prettier i think
        if level_up:
            dm_ch = await message.author.create_dm()
            approx_messages = add_spaces(int(((xp_from_level(data['level']+1)-xp_from_level(data['level']-1))/20)))

            embed = discord.Embed(colour=discord.Colour.random())
            embed.set_author(name=message.author.name, url='https://diskito.eu/leader.html')
            embed.set_thumbnail(url=message.author.avatar_url)
            embed.set_footer(text=f"That's about {approx_messages} more messages")

            # Split like this because fuck long lines
            line_1 = f'Your new level is **{data["level"]}**!'
            line_2 = f'You now have **{numerize.numerize(int(data["xp"]))}** xp'

            embed.add_field(name='You have just levelled up! Congrats!',
                            value=f'{line_1}\n{line_2}',
                            inline=False)
            await dm_ch.send(embed=embed)


def setup(client):
    client.add_cog(OnMessage(client))
