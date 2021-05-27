from func.console_logging import cl

import pyrebase, discord, yaml, json, os
from discord.ext import commands

## Config Load ##
config = yaml.safe_load(open('config.yml'))
valid_rp_channels = config.get('valid_rp_channels')
valid_rr_channels = config.get('valid_rr_channels')
error_channel_id = config.get('error_channel_id')
diskito_id = config.get('diskito_id')
good_emotes = config.get('good_emotes')
bad_emotes = config.get('bad_emotes')

## Firebase Database ##
firebase_config = {"apiKey": "AIzaSyDe_xKKup4lVoPasLmAQW9Csc1zUzsxB0U","authDomain": "chuckwalla-69.firebaseapp.com",
  "databaseURL": "https://chuckwalla-69.firebaseio.com","storageBucket": "chuckwalla-69.appspot.com",
  "serviceAccount": json.loads(os.getenv("serviceAccountKeyJSON"))}
db = pyrebase.initialize_app(firebase_config).database()


class RrRpEc(commands.Cog):
    def __init__(self, client):
        """
        Reaction Roles
        Reaction Points
        Emotes Count
        """
        self.client = client


    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        cl('', 'RrRpEc', 'on_raw_reaction_add')
        # Oh boy
        # Works only in selected channels (see 'valid_rr_channels' variable for their IDs)

        # Also doesn't work when a bot adds an emoji
        if payload.member.bot:
            return

        if payload.channel_id in valid_rr_channels:
            err_ch = self.client.get_channel(error_channel_id)

            guild = self.client.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)
            role = discord.utils.get(guild.roles, name = payload.emoji.name)  # Role name & Emoji name HAVE to be the same.

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


        # Reaction Points System
        if payload.channel_id in valid_rp_channels:
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


    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        cl('', 'RrRpEc', 'on_raw_reaction_remove')
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


def setup(client):
    client.add_cog(RrRpEc(client))
