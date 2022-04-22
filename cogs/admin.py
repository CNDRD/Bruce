import disnake
from disnake.ext.commands import Param
from disnake.ext import commands

from PIL import Image
import colorsys
import requests
import math
import yaml
import io

import os
from dotenv import load_dotenv
load_dotenv()
LED_URL = os.getenv("LED_URL")

# Config Load
config = yaml.safe_load(open('config.yml'))
slash_guilds = config.get('slash_guilds')
server_id = config.get('server_id')
owner_role_id = config.get('owner_role_id')
bot_mod_role_id = config.get('bot_mod_role_id')
mod_role_id = config.get('mod_role_id')
yeetard_role_id = config.get('yeetard_role_id')
leds_role_id = config.get('leds_role_id')
leds_alert_channel_id = config.get('leds_alert_channel_id')


class Admin(commands.Cog):
    def __init__(self, client):
        """Admin commands."""
        self.client = client

    @commands.guild_permissions(server_id, role_ids={yeetard_role_id: False, leds_role_id: True})
    @commands.slash_command(name="leds", description="Controls the LEDs I have behind my desk")
    async def leds(
            self,
            inter: disnake.ApplicationCommandInteraction,
            hue: int = Param(0, desc="Hue", min_value=0, max_value=360),
            saturation: int = Param(0, desc="Saturation", min_value=0, max_value=100),
            value: int = Param(0, desc="Value", min_value=0, max_value=100)
    ):
        requests.post(f"{LED_URL}/{int(hue)}/{int(saturation*10)}/{int(value*10)}")

        r, g, b = colorsys.hsv_to_rgb(hue / 360, saturation / 100, value / 100)
        r, g, b = math.ceil(r * 255), math.ceil(g * 255), math.ceil(b * 255)

        with io.BytesIO() as image_binary:
            image = Image.new(mode="RGB", size=(200, 100), color=(r, g, b))
            image.save(image_binary, "PNG")
            image_binary.seek(0)

            await inter.response.send_message(
                f"Set the LED's to this 👇 color `hsv({hue}, {saturation}, {value})` or `rgb({r}, {g}, {b})`",
                file=disnake.File(fp=image_binary, filename="color.png"),
                ephemeral=True
            )
            await self.client.get_channel(leds_alert_channel_id).send(
                f"**{inter.author.name}** set the LED's to `hsv({hue}, {saturation}, {value})` or `rgb({r}, {g}, {b})`"
            )

    @commands.guild_permissions(server_id, role_ids={yeetard_role_id: False, mod_role_id: True, bot_mod_role_id: True})
    @commands.slash_command(name="clear", description="Clears amount of messages. Default is 1")
    async def clear(
            self,
            inter: disnake.ApplicationCommandInteraction,
            amount: int = Param(1, desc="Amount of messages to delete")
    ):
        await inter.channel.purge(limit=amount)
        await inter.response.send_message(f'Successfully purged {amount} messages!', ephemeral=True)

    @commands.guild_permissions(server_id, role_ids={yeetard_role_id: False, mod_role_id: True, bot_mod_role_id: True})
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

    @commands.guild_permissions(server_id, role_ids={yeetard_role_id: False, mod_role_id: True, bot_mod_role_id: True})
    @commands.slash_command(name="say", description="The bot will send what you want as himself")
    async def say(
            self,
            inter: disnake.ApplicationCommandInteraction,
            text: str = Param(..., desc="What to send")
    ):
        await inter.channel.send(text)
        await inter.response.defer()
        return await inter.delete_original_message()

    @commands.guild_permissions(server_id, role_ids={yeetard_role_id: False, mod_role_id: True, bot_mod_role_id: True})
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
