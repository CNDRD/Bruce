from disnake.ext import commands
from dotenv import load_dotenv
import disnake
import os

load_dotenv()
client = commands.Bot(intents=disnake.Intents.all(), reload=True)

cogs = [
    'in_n_out',
    'on_message',
    'on_raw_reaction',
    'on_user_update',
    'on_voice_state_update',
    'message_commands',
    'quote',
    'status',
    'cicina',
    'user',
    'admin',
]

for filename in cogs:
    client.load_extension(f'cogs.{filename}')


@client.event
async def on_ready():
    print(f"\nHere comes {client.user.name}!")


client.run(os.getenv('TOKEN'))
