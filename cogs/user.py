from func.firebase_init import db

import disnake
from disnake.ext import commands

import random


class User(commands.Cog):
    def __init__(self, client):
        """Collection of short user facing commands"""
        self.client = client


    @commands.slash_command(
        name="connect",
        description="Connects your Discord account to the diskíto account",
        options=[
            disnake.Option(
                name="code",
                description="Connection Code",
                type=disnake.OptionType.string,
                required=True
            )
        ]
    )
    async def connect(self, inter, code):
        # Check if user already connected their account
        website_users = db.child("websiteProfiles").get().val()
        for wu in website_users:
            if inter.author.id == int(website_users[wu]['discordUID']):
                return await inter.response.send_message(content="You have already connected your account!", ephemeral=True)

        # Connect their account
        db.child("discordConnection").child(inter.author.id).set(code)
        await inter.response.send_message(content="Succesfully connected!", ephemeral=True)


    @commands.slash_command(
        name="ping",
        description="Gets the bot's ping"
    )
    async def ping(self, inter):
        await inter.response.send_message(f"Pong ({round(self.client.latency*1000)}ms)")


    @commands.slash_command(
        name="code",
        description="Link to the source code on GitHub"
    )
    async def code(self, inter):
        view = disnake.ui.View()
        view.add_item(disnake.ui.Button(label="GitHub", url="https://github.com/CNDRD/Bruce"))
        await inter.response.send_message(content="Here you go:", view=view)


    @commands.slash_command(
        name="coinflip",
        description="Flips a coin",
        options=[
            disnake.Option(
                name="heads",
                description="Outcome 1",
                type=disnake.OptionType.string
            ),
            disnake.Option(
                name="tails",
                description="Outcome 2",
                type=disnake.OptionType.string
            )
        ]
    )
    async def coinflip(self, inter, heads='Heads', tails='Tails'):
        outcomes = (heads, tails)
        msg = outcomes[random.SystemRandom().randint(0,1)]
        await inter.response.send_message(f"**{msg}**", ephemeral=True)


def setup(client):
    client.add_cog(User(client))
