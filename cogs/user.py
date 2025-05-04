from func.supabase import supabase

import disnake
from disnake.ext.commands import Param
from disnake.ext import commands

from datetime import datetime
import pytimeparse
import random


class User(commands.Cog):
    def __init__(self, client):
        """Collection of short user facing commands."""
        self.client = client

    @commands.slash_command(name="timer", description="Set a timer for a certain amount of time.")
    async def _timer(
            self,
            inter: disnake.ApplicationCommandInteraction,
            time: str = Param(..., desc="Amount of time to set the timer for. Format: 1h 30m 15s"),
            message: str = Param('Timer will end', desc="Message that will be shown next to the timer. Defaults to 'Timer will end'"),
            relative: bool = Param(True, desc="Whether the timer should be relative to the current time or not."),
            public: bool = Param(True, desc="Whether or not to make the timer public. Defaults to True.")
    ):
        """Set a timer for a certain amount of time."""
        timestamp = int(pytimeparse.parse(time) + datetime.now().timestamp())
        await inter.response.send_message(f"{message} <t:{timestamp}:{'R' if relative else 'T'}>", ephemeral=not public)

    @commands.slash_command(name="ping", description="Gets the bot's ping")
    async def ping(
            self,
            inter: disnake.ApplicationCommandInteraction
    ):
        await inter.response.send_message(f"Pong ({round(self.client.latency * 1000)}ms)")

    @commands.slash_command(name="code", description="Link to the source code on GitHub")
    async def code(
            self,
            inter: disnake.ApplicationCommandInteraction
    ):
        view = disnake.ui.View()
        view.add_item(disnake.ui.Button(label="GitHub", url="https://github.com/CNDRD/Bruce"))
        await inter.response.send_message(content="Here you go:", view=view)

    @commands.slash_command(name="coinflip", description="Flips a coin")
    async def coinflip(
            self,
            inter: disnake.ApplicationCommandInteraction,
            heads: str = Param("Heads", desc="What to send"),
            tails: str = Param("Tails", desc="What to send")
    ):
        outcomes = (heads, tails)
        msg = outcomes[random.SystemRandom().randint(0, 1)]
        await inter.response.send_message(f"**{msg}**", ephemeral=True)

    @commands.slash_command(name="money", description="Shows your balance")
    async def money(self, inter: disnake.ApplicationCommandInteraction):
        monies = supabase.from_('users').select('money').eq('id', inter.author.id).execute().data[0].get('money', 0)
        await inter.response.send_message(f"You have ★{monies:,}", ephemeral=True)


def setup(client):
    client.add_cog(User(client))
