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
startup_channel_id = config.get('startup_channel_id')
token = os.getenv('TOKEN')


client = commands.Bot(
    command_prefix=prefix,
    intents=disnake.Intents.all(),
    sync_permissions=True,
    test_guilds=slash_guilds
)


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')


@client.event
async def on_ready():
    print(f"\nHere comes {client.user.name}!")
    startup = client.get_channel(startup_channel_id)
    await startup.send(f"\nHere comes {client.user.name}!\n<t:{int(time.time())}:f>\n<t:{int(time.time())}:R>")


client.run(token)
