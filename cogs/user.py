from func.firebase_init import db

import disnake
from disnake.ext.commands import Param
from disnake.ext import commands

import random


class User(commands.Cog):
    def __init__(self, client):
        """Collection of short user facing commands."""
        self.client = client

    @commands.slash_command(name="connect", description="Connects your Discord account to the diskíto account")
    async def connect(
            self,
            inter: disnake.ApplicationCommandInteraction,
            code: str = Param(..., desc="Connects your Discord account to the diskíto account")
    ):
        # Check if user already connected their account
        website_users = db.child("websiteProfiles").get().val()
        for wu in website_users:
            if inter.author.id == int(website_users[wu]['discordUID']):
                return await inter.response.send_message(content="You have already connected your account!", ephemeral=True)

        # Connect their account
        db.child("discordConnection").child(inter.author.id).set(code)
        await inter.response.send_message(content="Successfully connected!", ephemeral=True)

    @commands.slash_command(name="ping", description="Gets the bot's ping")
    async def ping(self, inter):
        await inter.response.send_message(f"Pong ({round(self.client.latency * 1000)}ms)")

    @commands.slash_command(name="code", description="Link to the source code on GitHub")
    async def code(self, inter):
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
        monies = db.child('users').child(inter.author.id).child('money').get().val()
        await inter.response.send_message(f"You have {monies:,} shekels", ephemeral=True)


def setup(client):
    client.add_cog(User(client))
