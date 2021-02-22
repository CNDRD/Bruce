from func.console_logging import cl

import pyrebase, yaml, json, discord
from discord.ext import commands

## Config Load ##
config = yaml.safe_load(open('config.yml'))
bot_mod_role_id = config.get('bot_mod_role_id')

## Firebase Database ##
db = pyrebase.initialize_app( json.loads(config.get('firebase')) ).database()


class Status(commands.Cog):
    def __init__(self, client):
        """
        Status command.

        Can be used to set custom statuses

        Example usage:
        (,)status watching you all -> Watching you all
        (,)status listening everything -> Listening to everything
        (,)status playing games -> Playing games
        (,)status everyone -> Playing everyone
        (,)status clear -> Clears the status
        """
        self.client = client


    @commands.command()
    @commands.has_role(bot_mod_role_id)  # Diagnostics
    async def status(self, ctx, *args):
        cl(ctx)

        # For when a clown comes along and types a blank command without arguments
        if args == ():
            await ctx.send('You have to type some arguments!')
            await ctx.message.add_reaction('❌')
            return

        # Because autocorrect is a fucking bitch
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
            # Defaults to playing
            activity = discord.ActivityType.playing
            msg = ' '.join(map(str, args))

        # Use the keyword 'clear' to remove the status
        if arg0 == 'clear':
            await self.client.change_presence(activity=None)
            await ctx.message.add_reaction('✅')
        # Else set the desired status
        else:
            a = discord.Activity(type=activity, name=msg)
            await self.client.change_presence(activity=a)
            await ctx.message.add_reaction('✅')


def setup(client):
    client.add_cog(Status(client))
