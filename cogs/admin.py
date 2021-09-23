from func.firebase_init import db

from disnake.ext import commands
import disnake

import yaml


## Config Load ##
config = yaml.safe_load(open('config.yml'))
slash_guilds = config.get('slash_guilds')
owner_role_id = config.get('owner_role_id')
bot_mod_role_id = config.get('bot_mod_role_id')
mod_role_id = config.get('mod_role_id')


class Admin(commands.Cog):
    def __init__(self, client):
        """
        Admin commands.
        - clear
        - add_reaction
        - say
        - edit
        """
        self.client = client


    @commands.slash_command(
        name="clear",
        description="Clears amount of messages. Default is 1",
        options=[
            disnake.Option(
                name="amount",
                description="Amount of messages to delete (+1)",
                type=disnake.OptionType.integer
            )
        ]
    )
    @commands.has_any_role(bot_mod_role_id, mod_role_id)
    async def clear(self, inter, amount: int = 1):
        await inter.channel.purge(limit=(amount+1))
        await inter.response.send_message(f'Succesfully purged {amount+1} messages!', ephemeral=True)


    @commands.slash_command(
        name="add_reaction",
        description="Adds a reaction to the message above",
        options=[
            disnake.Option(
                name="reaction",
                description="Reaction to add",
                type=disnake.OptionType.string,
                required=True
            )
        ]
    )
    async def add_reaction(self, inter, reaction):
        messages = await inter.channel.history(limit=1).flatten()
        await messages[0].add_reaction(reaction)
        await inter.response.defer()
        return await inter.delete_original_message()


    @commands.slash_command(
        name="say",
        description="The bot will send what you want as himself",
        options=[
            disnake.Option(
                name="text",
                description="What to send",
                type=disnake.OptionType.string,
                required=True
            )
        ]
    )
    async def say(self, inter, text):
        await inter.channel.send(text)
        await inter.response.defer()
        return await inter.delete_original_message()


    @commands.slash_command(
        name="edit",
        description="Edit the message",
        options=[
            disnake.Option(
                name="text",
                description="What to edit the message with",
                type=disnake.OptionType.string,
                required=True
            ),
            disnake.Option(
                name="message_id_to_edit",
                description="ID of message to edit",
                type=disnake.OptionType.string,
                required=True
            )
        ]
    )
    async def edit(self, inter, text, message_id_to_edit):
        try:
            message = await inter.channel.fetch_message(message_id_to_edit)
        except Exception as e:
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
