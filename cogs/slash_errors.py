import yaml, discord, dislash
from discord.ext import commands

from dislash import *

## Config Load ##
config = yaml.safe_load(open('config.yml'))
slash_guilds = config.get('slash_guilds')


class DislashErrors(commands.Cog):
    def __init__(self, client):
        """
        Dislash error handlers
        """
        self.client = client


    @commands.Cog.listener()
    async def on_slash_command_error(self, interaction, error):
        if isinstance(error, dislash.slash_commands.errors.CheckAnyFailure):
            await interaction.create_response("You're missing a some permissions needed to use this command!", ephemeral=True)

        elif isinstance(error, dislash.slash_commands.errors.MissingRole):
            await interaction.create_response("You're missing a role needed to use this command!", ephemeral=True)

        elif isinstance(error, dislash.slash_commands.errors.MissingAnyRole):
            await interaction.create_response("You're missing a role needed to use this command!", ephemeral=True)

        elif isinstance(error, dislash.slash_commands.errors.PrivateMessageOnly):
            await interaction.create_response("This command only works in DM's!", ephemeral=True)

        elif isinstance(error, dislash.slash_commands.errors.NoPrivateMessage):
            await interaction.create_response("This command doesn't workw in DM's!", ephemeral=True)

        elif isinstance(error, dislash.slash_commands.errors.CommandOnCooldown):
            await interaction.create_response("This command is on cooldown! Try again later.", ephemeral=True)

        else:
            await interaction.create_response("Some unforseen error happened. Try again.", ephemeral=True)
            print(error)


def setup(client):
    client.add_cog(DislashErrors(client))
