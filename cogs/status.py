import disnake
from disnake.ext.commands import Param
from disnake.ext import commands


Activities = commands.option_enum({"Watching": "watching", "Listening": "listening", "Playing": "playing"})


class Status(commands.Cog):
    def __init__(self, client):
        """Custom status command."""
        self.client = client

    @commands.slash_command(name="status", description="Change the status of the bot")
    async def status(
            self,
            inter: disnake.ApplicationCommandInteraction,
            activity: Activities = Param(..., desc="The activity type"),
            what_doing: str = Param(None, desc="The text after the activity. Leave blank to clear the status.")
    ):
        if activity == "watching":
            activity = disnake.ActivityType.watching
        elif activity == "listening":
            activity = disnake.ActivityType.listening
        else:
            activity = disnake.ActivityType.playing

        if what_doing is None:
            act = None
            message = "Status cleared!"
        else:
            act = disnake.Activity(type=activity, name=what_doing)
            message = "Status set!"

        await self.client.change_presence(activity=act)
        await inter.response.send_message(message, ephemeral=True)


def setup(client):
    client.add_cog(Status(client))
