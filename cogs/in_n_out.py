from func.console_logging import cl
from func.levels import rank_name
from func.stuff import ordinal

from discord.ext import commands
from discord.utils import get
from datetime import datetime
import pyrebase, yaml, json

## Config Load ##
config = yaml.safe_load(open('config.yml'))

in_n_out_channel_id = config.get('in_n_out_channel_id')

test_account_uid = config.get('test_account_uid')

honkhonk_emoji = config.get('honkhonk_emoji')
garrow_emoji = config.get('garrow_emoji')
yarrow_emoji = config.get('yarrow_emoji')
rarrow_emoji = config.get('rarrow_emoji')

## Firebase Database ##
db = pyrebase.initialize_app( json.loads(config.get('firebase')) ).database()


class InNOut(commands.Cog):
    def __init__(self, client):
        """
        Not so simple 'in & out' events.

        - Sets up users in database
        - Shames users who leave too soon
        """
        self.client = client


    @commands.Cog.listener()
    async def on_member_join(self, member):
        cl('', 'InNOut', 'on_member_join')

        # No welcome messages for bots and my test account
        if member.bot == True or member.id == test_account_uid:
            return

        # Basic-ass variables
        ino = self.client.get_channel(in_n_out_channel_id)
        leaves = leave_counts(member.id)

        # Get arrows emoji
        garrow = self.client.get_emoji(garrow_emoji)
        yarrow = self.client.get_emoji(yarrow_emoji)

        if leaves > 0:
            # The user has joined the server before at least once
            msg = f"{yarrow} **{member.mention}** has just ***joined*** for the {ordinal(leaves)} time!"

            # Give the user his XP role & main user role
            lvl = db.child('users').child(member.id).child('level').get().val()
            rank = rank_name(lvl)
            role = get(member.guild.roles, name=rank)
            await member.add_roles(role)
            jeetard = get(member.guild.roles, name='Jeetard')
            await member.add_roles(jeetard)

            # Update users individial stats
            data = {'in_server':True}
            db.child('users').child(member.id).update(data)

        else:
            # First join ever
            msg = f"{garrow} **{member.mention}** has just ***joined!***"

            # Give the user the 0-level role
            role = get(member.guild.roles, name=rank_name(0))
            await member.add_roles(role)

            # Get timestamps to when the user joined Discord and the server, and a link to their avatar
            joinedServer = int(member.joined_at.timestamp())
            joinedDiscord = int(member.created_at.timestamp())
            avatarURL = str(member.avatar_url_as(size=4096))

            # Create users individial stats
            d = {'reacc_points':0,
                 'username':str(member),
                 'xp':0,
                 'level':0,
                 'last_xp_get':joinedServer,
                 'messages_count':0,
                 'joined_server':joinedServer,
                 'joined_discord':joinedDiscord,
                 'avatar_url':avatarURL,
                 'in_server':True
                 }
            db.child('users').child(member.id).set(d)

        await ino.send(msg)


    @commands.Cog.listener()
    async def on_member_remove(self, member):
        cl('', 'InNOut', 'on_member_remove')

        # No welcome messages for bots and my test account
        if member.bot == True or member.id == test_account_uid:
            return

        # Get arrow emoji
        rarrow = self.client.get_emoji(rarrow_emoji)

        leaves = leave_counts(member.id)
        if leaves >= 1:
            count = leaves
        else:
            count = 1

        # Update users individial stats
        data = {'leaves_count':count+1, 'in_server':False}
        db.child('users').child(member.id).update(data)

        # Basic-ass variables
        ino = self.client.get_channel(in_n_out_channel_id)
        joined = member.joined_at
        left = datetime.utcnow()

        diff = (left - joined)
        stayed = format_timespan(int(diff.total_seconds()))

        username = db.child('users').child(member.id).child('username').get().val()

        if count == 1:
            msg = f"{rarrow} **{username}** has just ***left*** us! Was here for *{stayed}*."
        else:
            msg = f"{rarrow} **{username}** has just ***left*** us for the {ordinal(leaves)} time! Was here for *{stayed}*."
        clown = await ino.send(msg)

        # Automatically adds 🤡 emoji to every leave message
        # if they left within 15 minutes of joining it also adds another clown emoji
        await clown.add_reaction('🤡')
        if int(diff.total_seconds()) < 900:
            e = self.client.get_emoji(honkhonk_emoji) # :HonkHonk:
            await clown.add_reaction(e)


def setup(client):
    client.add_cog(InNOut(client))


def leave_counts(user_id):
    leaves = db.child('users').child(user_id).child('leaves_count').get().val()
    if leaves is None:
        return 0
    return leaves
