import pyrebase, yaml, random, json, os
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()

from dislash import *

## Config Load ##
config = yaml.safe_load(open('config.yml'))
slash_guilds = config.get('slash_guilds')

## Firebase Database ##
firebase_config = {"apiKey": "AIzaSyDe_xKKup4lVoPasLmAQW9Csc1zUzsxB0U","authDomain": "chuckwalla-69.firebaseapp.com",
  "databaseURL": "https://chuckwalla-69.firebaseio.com","storageBucket": "chuckwalla-69.appspot.com",
  "serviceAccount": json.loads(os.getenv("serviceAccountKeyJSON"))}
db = pyrebase.initialize_app(firebase_config).database()

class User(commands.Cog):
    def __init__(self, client):
        """
        Collection of short user facing commands.

        - connect
        - code
        - ping
        - coinflip
        """
        self.client = client


    @slash_commands.command(
        guild_ids=slash_guilds,
        description="Connect your Discord account to diskito.eu",
        options=[ Option("code", "The code you got on your profile page", Type.STRING, required=True) ]
        )
    async def connect(self, ctx, code):
        db.child("discordConnection").child(ctx.author.id).set(code)
        await ctx.create_response("Succesfully connected!", ephemeral=True)


    @slash_commands.command(
        guild_ids=slash_guilds,
        description="Link to bot's source code"
    )
    async def code(self, ctx):
        row = ActionRow(
            Button(
                style=ButtonStyle.link,
                label="GitHub",
                url="https://github.com/CNDRD/Bruce"
            )
        )
        await ctx.create_response("Here you go!", components=[row])


    @slash_commands.command(
        guild_ids=slash_guilds,
        description="Bot's ping to Discord"
    )
    async def ping(self, ctx):
        await ctx.create_response(f"Pong `{round(self.client.latency*1000)}ms`")


    @slash_commands.command(
        guild_ids=slash_guilds,
        description="Flips a coin for you",
        options=[
            Option("heads", "Choose something else than 'Heads'", Type.STRING),
            Option("tails", "Choose something else than 'Tails'", Type.STRING)
        ]
    )
    async def flip(self, ctx, heads="Heads", tails="Tails"):
        if random.SystemRandom().randint(0,1) == 0:
            msg = heads
        else:
            msg = tails
        await ctx.create_response(f"**{msg}**")


def setup(client):
    client.add_cog(User(client))
