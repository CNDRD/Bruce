import disnake
from disnake.ext import commands
import yaml
import os
from cogwatch import Watcher
from dotenv import load_dotenv
load_dotenv()

config = yaml.safe_load(open('config.yml'))
prefix = str(config.get('prefix'))
slash_guilds = config.get('slash_guilds')
token = os.getenv('TOKEN')

client = commands.Bot(command_prefix=prefix, intents=disnake.Intents.all(), test_guilds=slash_guilds)


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')


@client.event
async def on_ready():
    print(f'Logged in as {client.user.name} (ID: {client.user.id})')
    watcher = Watcher(client, path='cogs', preload=True)
    await watcher.start()

client.run(token)
