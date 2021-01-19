import pyrebase, yaml, json, time, datetime
from discord.ext import commands, tasks
from pytz import timezone

################################################################ Config Load ##
config = yaml.safe_load(open("config.yml"))
cl = config.get('console_logging')

################################################################### Firebase ##
fb = json.loads(config.get('firebase'))
firebase = pyrebase.initialize_app(fb)
db = firebase.database()

################################################################### Commands ##
class RandomEvents(commands.Cog):
    def __init__(self, client):
        """Random events."""
        self.client = client


    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        if cl: print('START on_user_update ', end="")
        data = {
        "username": str(after),
        "avatar_url":str(after.avatar_url_as(size=4096))
        }
        db.child('users').child(after.id).update(data)
        if cl: print("END")


    @commands.Cog.listener()
    async def on_command(self, ctx):
        if cl: print('START on_command ', end="")

        # Basic-ass variables
        now = int(time.time())

        # Get shit to update in DB for dashboard
        dash_data = {
        "authorName":str(ctx.author),
        "authorID":ctx.message.author.id,
        "authorPfpLink":str(ctx.message.author.avatar_url_as(size=4096)),
        "bot":True if ctx.bot else False,
        "botName":str(ctx.me),
        "botPfpLink":str(ctx.me.avatar_url_as(size=4096)),
        "channelName":str(ctx.channel),
        "channelID":ctx.message.channel.id,
        "cog":"bot.py" if ctx.cog is None else ctx.cog.qualified_name,
        "command":str(ctx.command),
        "commandFailed":ctx.command_failed,
        "guild":str(ctx.guild),
        "invokedSubcommand":ctx.invoked_subcommand,
        "invokedWith":ctx.invoked_with,
        "kwargs":ctx.kwargs,
        "messageID":ctx.message.id,
        "prefix":ctx.prefix,
        "subcommandPassed":ctx.subcommand_passed,
        "valid":ctx.valid,
        "voiceClient":ctx.voice_client,
        "timestamp":now
        }

        # Individual command usage count
        command_data_db = db.child('dashboard').child('commandsUsage').child(str(ctx.command)).get().val()
        if command_data_db is None: command_data = {str(ctx.command): 1}
        else: command_data = {str(ctx.command): command_data_db+1}

        # Server-wide command usage count
        totalCommandUsesCount = db.child('serverTotals').child('commandUses').get().val()
        serverTotalsData = {"commandUses":totalCommandUsesCount+1}

        # Update the shit in Database
        db.child('dashboard').child('lastCommand').set(dash_data)
        db.child('dashboard').child('commandsUsage').update(command_data)
        db.child('serverTotals').update(serverTotalsData)

        if cl: print("END")

def setup(client):
    client.add_cog(RandomEvents(client))
