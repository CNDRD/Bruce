import disnake
from disnake.ext import commands
import yaml
import os
import time
from dotenv import load_dotenv
load_dotenv()


config = yaml.safe_load(open('config.yml'))
prefix = str(config.get('prefix'))
slash_guilds = config.get('slash_guilds')
token = os.getenv('TOKEN')


client = commands.Bot(
    intents=disnake.Intents.all(),
    reload=True,
    # command_prefix=prefix,
    # test_guilds=slash_guilds
)


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')


@client.event
async def on_ready():
    print(f"\nHere comes {client.user.name}!")

client.run(token)
