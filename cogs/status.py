import disnake
from disnake.ext import commands


class Status(commands.Cog):
    def __init__(self, client):
        """Custom status command"""
        self.client = client


    @commands.slash_command(
        name="status",
        description="Change the status of the bot",
        options=[
            disnake.Option(
                name="activity",
                description="The activity type",
                choices=[
                    disnake.OptionChoice(name="Watching", value="watching"),
                    disnake.OptionChoice(name="Listening", value="listening"),
                    disnake.OptionChoice(name="Playing", value="playing"),
                ],
                required=True
            ),
            disnake.Option(
                name="what_doing",
                description="The text after the activity. Leave black to clear the status.",
                type=disnake.OptionType.string
            )
        ]
    )
    async def status(self, inter, activity, what_doing=None):
        if activity == 'watching':
            activity = disnake.ActivityType.watching
        elif activity == 'listening':
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
