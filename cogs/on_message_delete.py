from func.firebase_init import db

import disnake
from disnake.ext import commands

import yaml


# Config Load
config = yaml.safe_load(open('config.yml'))
deleted_messages_channel_id = config.get('deleted_messages_channel_id')


class OnMessageDelete(commands.Cog):
    def __init__(self, client):
        """Waits for a message to get deleted and stores that message in a locked channel."""
        self.client = client

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        # Don't really care about bot messages, nor do we care about DM's
        if message.author.bot or isinstance(message.channel, disnake.channel.DMChannel):
            return

        await self.client.get_channel(deleted_messages_channel_id).send(
            content=f"{message.author}\n```{message.content}```",
            embeds=message.embeds,
            stickers=message.stickers,
        )


def setup(client):
    client.add_cog(OnMessageDelete(client))
