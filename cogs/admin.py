import disnake
from disnake.ext.commands import Param
from disnake.ext import commands

bot_mod_role_id = 553150973581721600
mod_role_id = 475345534723555339
yeetard_role_id = 488342364570779650


class Admin(commands.Cog):
    def __init__(self, client):
        """Admin commands."""
        self.client = client

    @commands.has_role(mod_role_id)
    @commands.has_role(bot_mod_role_id)
    @commands.slash_command(name="clear", description="Clears amount of messages. Default is 1")
    async def clear(
            self,
            inter: disnake.ApplicationCommandInteraction,
            amount: int = Param(1, desc="Amount of messages to delete")
    ):
        await inter.channel.purge(limit=amount)
        await inter.response.send_message(f'Successfully purged {amount} messages!', ephemeral=True)

    @commands.has_role(mod_role_id)
    @commands.has_role(bot_mod_role_id)
    @commands.slash_command(name="add_reaction", description="Adds a reaction to the message above")
    async def add_reaction(
            self,
            inter: disnake.ApplicationCommandInteraction,
            reaction: disnake.Emoji = Param(..., desc="Reaction to add", )
    ):
        messages = await inter.channel.history(limit=1).flatten()
        await messages[0].add_reaction(reaction)
        await inter.response.defer()
        return await inter.delete_original_message()

    @commands.has_role(mod_role_id)
    @commands.has_role(bot_mod_role_id)
    @commands.slash_command(name="say", description="The bot will send what you want as himself")
    async def say(
            self,
            inter: disnake.ApplicationCommandInteraction,
            text: str = Param(..., desc="What to send")
    ):
        await inter.channel.send(text)
        await inter.response.defer()
        return await inter.delete_original_message()

    @commands.has_role(mod_role_id)
    @commands.has_role(bot_mod_role_id)
    @commands.slash_command(name="edit", description="Edit the message")
    async def edit(
            self,
            inter: disnake.ApplicationCommandInteraction,
            text: str = Param(..., desc="What to edit the message with"),
            message_id_to_edit: str = Param(..., desc="ID of message to edit")
    ):
        try:
            message = await inter.channel.fetch_message(message_id_to_edit)
        except Exception as e:
            err_msg = "Huh"
            if isinstance(e, disnake.errors.NotFound):
                err_msg = f'No message with an ID of `{message_id_to_edit}` was found..'
            if isinstance(e, disnake.errors.Forbidden):
                err_msg = f'You do not have permission to edit the message with an ID of `{message_id_to_edit}`'
            if isinstance(e, disnake.errors.HTTPException):
                err_msg = f'Retrieving the message with an ID of `{message_id_to_edit}` failed'
            return await inter.response.send_message(err_msg, ephemeral=True)

        await message.edit(content=text)
        await inter.response.defer()
        return await inter.delete_original_message()


def setup(client):
    client.add_cog(Admin(client))
