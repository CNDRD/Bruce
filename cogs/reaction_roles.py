import pyrebase, discord, yaml, json
from discord.ext import commands

# Config Load #
config = yaml.safe_load(open("config.yml"))
cl = config.get('console_logging')
error_channel_id = config.get('error_channel_id')
diskito_id = config.get('diskito_id')

# Firebase #
fb = json.loads(config.get('firebase'))
firebase = pyrebase.initialize_app(fb)
db = firebase.database()

# Variables #
valid_rr_channels = [config.get('welcome_hall_channel_id'), config.get('role_select_channel_id')]
valid_rp_channels = [config.get('trashposting_channel_id'), config.get('videoposting_channel_id')]

good_emotes = ['ooo','omegateef','omegalul','monkaLMAOXD','kek','AgrLove','LemonJoy']
bad_emotes = ['WHEEZEtyKUNDO','incredi_wut','HonkHonk','_F','Gay']

# Commands #
class ReactionRoles(commands.Cog):
    def __init__(self, client):
        """Reaction Role System.

        Uses a on_raw_reaction_add & on_raw_reaction_remove
        for adding & removing roles.
        Makes Reaction Points work.
        """
        self.client = client


    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if cl: print('START on_raw_reaction_add ', end="")
        # Oh boy
        # Works only in selected channels (see 'valid_rr_channels' variable for their IDs)
        # Also doesn't work when a bot adds an emoji
        if payload.channel_id in valid_rr_channels and not payload.member.bot:
            err_ch = self.client.get_channel(error_channel_id)

            guild = discord.utils.find(lambda g : g.id == payload.guild_id, self.client.guilds)  # Gets the right guild
            role = discord.utils.get(guild.roles, name=payload.emoji.name)  # Role name & Emoji name HAVE to be the same.

            if role is not None:
                member = discord.utils.find(lambda m : m.id == payload.user_id, guild.members)
                if member is not None:
                    await member.add_roles(role)
                else:
                    await err_ch.send(f"on_raw_reaction_add: **Member** *{member}* **not found**")
            else:
                member = discord.utils.find(lambda m : m.id == payload.user_id, guild.members)
                await err_ch.send(f"on_raw_reaction_add: **Role for** *'{payload.emoji.name}'*  **emoji not found for user** {member}")

        # Reaction Points System
        if not payload.member.bot and payload.channel_id in valid_rp_channels:
            emote = payload.emoji.name  # Get the emote to work with it better

            ch = self.client.get_channel(payload.channel_id)
            msg = await ch.fetch_message(payload.message_id)
            uid = msg.author.id

            if uid != payload.user_id:
                # Server Totals Data
                st = db.child('serverTotals').get().val()
                st_rp = st.get('reactionPoints')

                curr_points = db.child('users').child(uid).child('reacc_points').get().val()
                if emote in good_emotes:
                    data = {'reacc_points':curr_points + 1}
                    server_totals = {'reactionPoints':st_rp + 1}
                elif emote in bad_emotes:
                    data = {'reacc_points':curr_points - 1}
                    server_totals = {'reactionPoints':st_rp - 1}

                if emote in good_emotes or emote in bad_emotes:
                    db.child('users').child(uid).update(data)
                    db.child('serverTotals').update(server_totals)


        # Emoji usage counter
        if (hah := self.client.get_emoji(payload.emoji.id)) is not None:
            if hah.guild_id != diskito_id: return
            # Otherwise it'll spit out errors when working with non-diskíto emotes

            emoji_id = payload.emoji.id
            emoji_url = str(payload.emoji.url)

            count = db.child('emojiCounts').child(emoji_id).child('count').get().val()
            if count is None: count = 0

            count_data = {'count':count+1, 'url':emoji_url}
            db.child('emojiCounts').child(emoji_id).update(count_data)

        if cl: print("END")


    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if cl: print('START on_raw_reaction_remove ', end="")
        # Works only in selected channels (see 'valid_rr_channels' variable for their IDs)
        if payload.channel_id in valid_rr_channels:
            err_ch = self.client.get_channel(error_channel_id)

            guild = discord.utils.find(lambda g : g.id == payload.guild_id, self.client.guilds)  # Gets the right guild
            role = discord.utils.get(guild.roles, name=payload.emoji.name)  # Role name & Emoji name HAVE to be the same.

            if role is not None:
                member = discord.utils.find(lambda m : m.id == payload.user_id, guild.members)
                if member is not None:
                    await member.remove_roles(role)
                else:
                    await err_ch.send(f"on_raw_reaction_remove: **Member** *{member}* **not found**")
            else:
                member = discord.utils.find(lambda m : m.id == payload.user_id, guild.members)
                await err_ch.send(f"on_raw_reaction_remove: **Role for** *'{payload.emoji.name}'*  **emoji not found for user** {member}")


        # Emoji usage counter
        if (hah := self.client.get_emoji(payload.emoji.id)) is not None:
            if hah.guild_id != diskito_id: return
            # Otherwise it'll spit out errors when working with non-diskíto emotes

            emoji_id = payload.emoji.id
            emoji_url = str(payload.emoji.url)

            count = db.child('emojiCounts').child(emoji_id).child('count').get().val()
            if count is None: count = 1

            count_data = {'count':count-1, 'url':emoji_url}
            db.child('emojiCounts').child(emoji_id).update(count_data)


        # Reaction Points System
        # Don't wanna count shit unless it's in the correct channels
        if payload.channel_id not in valid_rp_channels:
            return

        emote = payload.emoji.name  # Get the emote to work with it better

        ch = self.client.get_channel(payload.channel_id)
        msg = await ch.fetch_message(payload.message_id)
        uid = msg.author.id

        if uid != payload.user_id:
            # Server Totals Data
            st = db.child('serverTotals').get().val()
            st_rp = st.get('reactionPoints')

            curr_points = db.child('users').child(uid).child('reacc_points').get().val()
            if emote in good_emotes:
                data = {'reacc_points':curr_points - 1}
                server_totals = {'reactionPoints':st_rp - 1}
            elif emote in bad_emotes:
                data = {'reacc_points':curr_points + 1}
                server_totals = {'reactionPoints':st_rp + 1}

            if emote in good_emotes or emote in bad_emotes:
                db.child('users').child(uid).update(data)
                db.child('serverTotals').update(server_totals)

        if cl: print("END")


def setup(client):
    client.add_cog(ReactionRoles(client))
