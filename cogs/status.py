from discord.ext import commands
import discord, yaml

################################################################ Config Load ##
config = yaml.safe_load(open("config.yml"))
cl = config.get('console_logging')
diagnostics_role_id = config.get('diagnostics_role_id')

################################################################### Commands ##
class Status(commands.Cog):
    def __init__(self, client):
        """Status command.

        Can be used to set custom statuses

        Example commands:
        (,)status watching you all -> Watching you all
        (,)status listening everything -> Listening to everything
        (,)status playing games -> Playing games
        (,)status everyone -> Playing everyone
        (,)status clear -> Clears the status
        """
        self.client = client

    @commands.command()
    @commands.has_role(diagnostics_role_id)  # Diagnostics
    async def status(self, ctx, *args):
        if cl: print('START status ', end="")

        if args == ():
            await ctx.send('You have to type some arguments!')
            await ctx.message.add_reaction('❌')
            return

        arg0 = (args[0]).lower()

        if arg0 == 'watching':
            activity = discord.ActivityType.watching
            msg = ' '.join(map(str, args[1:]))
        elif arg0 == 'playing':
            activity = discord.ActivityType.playing
            msg = ' '.join(map(str, args[1:]))
        elif arg0 == 'listening':
            activity = discord.ActivityType.listening
            msg = ' '.join(map(str, args[1:]))
        else:
            activity = discord.ActivityType.playing  # Defaults to playing
            msg = ' '.join(map(str, args))

        if arg0 == 'clear':
            await self.client.change_presence(activity=None)
            await ctx.message.add_reaction('✅')
        else:
            a = discord.Activity(type=activity, name=msg)
            await self.client.change_presence(activity=a)
            await ctx.message.add_reaction('✅')
        if cl: print("END")

def setup(client):
    client.add_cog(Status(client))
