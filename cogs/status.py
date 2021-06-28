import yaml, discord
from discord.ext import commands

from dislash import *

## Config Load ##
config = yaml.safe_load(open('config.yml'))
bot_mod_role_id = config.get('bot_mod_role_id')
slash_guilds = config.get('slash_guilds')


class Status(commands.Cog):
    def __init__(self, client):
        """
        Status command.

        Can be used to set custom statuses
        """
        self.client = client


    @slash_commands.command(
        guild_ids=slash_guilds,
        description="Changes the bot's status message",
        options=[
            Option(
                name="activity",
                description="The activity type. Defaults to 'Playing'",
                choices=[
                    OptionChoice(name="Playing", value="playing"),
                    OptionChoice(name="Watching", value="watching"),
                    OptionChoice(name="Listening", value="listening"),
                ]
            ),
            Option(
                name="message",
                description="The status message. Leave empty to remove status"
            )
        ]
    )
    @slash_commands.has_role(bot_mod_role_id)
    async def status(self, ctx, activity=None, message=None):
        if activity == "playing":
            act = discord.ActivityType.playing
        elif activity == "watching":
            act = discord.ActivityType.watching
        elif activity == "listening":
            act = discord.ActivityType.listening
        else:
            act = discord.ActivityType.playing

        if message is None:
            await self.client.change_presence(activity=None)
            await ctx.create_response("Status cleared!", ephemeral=True)
        else:
            await self.client.change_presence(activity=discord.Activity(type=act, name=message))
            await ctx.create_response("Status changed!", ephemeral=True)


def setup(client):
    client.add_cog(Status(client))
