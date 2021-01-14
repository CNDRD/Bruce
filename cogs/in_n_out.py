import pyrebase, yaml, json, discord, time
from humanfriendly import format_timespan
from discord.ext import commands
from discord.utils import get
from datetime import datetime

################################################################ Config Load ##
config = yaml.safe_load(open("config.yml"))
cl = config.get('console_logging')
emote_server_id = config.get('emote_server_id')
in_n_out_channel_id = config.get('in_n_out_channel_id')
#in_n_out_channel_id = 694165272155783248 # yeet

################################################################### Firebase ##
fb = json.loads(config.get('firebase'))
firebase = pyrebase.initialize_app(fb)
db = firebase.database()

################################################################### Commands ##
class InNOut(commands.Cog):
    def __init__(self, client):
        """Simple join/leave."""
        self.client = client

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if cl: print('START on_member_join ', end="")

        # No welcome messages for bots and my test account
        if member.bot == True or member.id == 552570700171313187:
            return

        # Basic-ass variables
        ino = self.client.get_channel(in_n_out_channel_id)
        leaves = leave_counts(member.id)
        now = int(time.time())

        # Get arrows emoji
        garrow = self.client.get_emoji(784822110723112974)
        yarrow = self.client.get_emoji(784822110622974014)

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
            joinedServer = int((member.joined_at).timestamp())
            joinedDiscord = int((member.created_at).timestamp())
            avatarURL = str(member.avatar_url_as(size=4096))

            # Create users individial stats
            d = {'reacc_points':0,
                 'username':str(member),
                 'xp':0,
                 'level':0,
                 'last_xp_get':now,
                 'messages_count':0,
                 'joined_server':joinedServer,
                 'joined_discord':joinedDiscord,
                 'avatar_url':avatarURL,
                 'in_server':True
                 }
            db.child('users').child(member.id).set(d)

        await ino.send(msg)
        if cl: print("END")


    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if cl: print('START on_member_remove ', end="")

        # No welcome messages for bots and my test account
        if member.bot == True or member.id == 552570700171313187:
            return

        # Get arrow emoji
        rarrow = self.client.get_emoji(784822110836097094)

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
            e = self.client.get_emoji(570667900529147914) # :HonkHonk:
            await clown.add_reaction(e)

        if cl: print("END")


def setup(client):
    client.add_cog(InNOut(client))

################################################################## Functions ##
def leave_counts(uID):
    leaves = db.child('users').child(uID).child('leaves_count').get().val()
    if leaves is None:
        return 0
    return leaves

ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n/10%10!=1)*(n%10<4)*n%10::4])
# https://stackoverflow.com/a/20007730

def rank_name(num):
    a = (num - (num%5))
    if num == 0:
        return '[0]'
    return f"[{a}-{a+5}]"
# https://stackoverflow.com/a/13082705
