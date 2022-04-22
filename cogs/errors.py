from disnake.ext import commands


class Errors(commands.Cog):
    def __init__(self, client):
        """Errors."""
        self.client = client

    @commands.Cog.listener()
    async def on_slash_command_error(self, inter, error):
        # All errors under "CheckFailure" (https://disnake.readthedocs.io/en/latest/ext/commands/api.html#exception-hierarchy)
        match error:
            case commands.CheckAnyFailure:
                message = "Some check failed. That means you're probably missing permissions to do this.."
            case commands.PrivateMessageOnly:
                message = "This command can only be used in PM's"
            case commands.NoPrivateMessage:
                message = "This command cannot be used in PM's"
            case commands.NotOwner:
                message = "You need to be the owner of this bot to use this command.."
            case commands.MissingPermissions:
                message = "You're missing permissions to do this."
            case commands.BotMissingPermissions:
                message = "I am missing permissions to do this."
            case commands.MissingRole:
                message = "You're missing a role to do this."
            case commands.BotMissingRole:
                message = "I am missing a role to do this."
            case commands.MissingAnyRole:
                message = "You're missing a role to do this."
            case commands.BotMissingAnyRole:
                message = "I am missing a role to do this."
            case commands.NSFWChannelRequired:
                message = "This command can only be used in a NSFW channel."
            case _:
                message = "This is an unexpected error. Please notify someone about this if the issue persists."

        if inter.response.is_done():
            return await inter.edit_original_message(content=message)

        await inter.response.send_message(message, ephemeral=True)


def setup(client):
    client.add_cog(Errors(client))
