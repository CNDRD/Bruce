from func.firebase_init import db
import pyrebase, discord, yaml, time, os, json
from humanfriendly import format_timespan
from discord.ext import commands
from datetime import datetime
from pytz import timezone

print('Starting to load..')
start_time = time.time()

## Config Load ##
config = yaml.safe_load(open("config.yml"))
prefix = str(config.get('prefix'))
error_channel_id = config.get('error_channel_id')
startup_channel_id = config.get('startup_channel_id')
db_auto_backup_loop = config.get('db_auto_backup_loop')
token = os.getenv('bruce_token')


## Basic Bot Setup ##
client = commands.Bot(command_prefix=prefix, intents=discord.Intents.all())
client.remove_command('help')
cog_count = 0

## Cog Loader ##
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')
        cog_count += 1

## Commands ##
@client.event
async def on_ready():
    tn = datetime.now(timezone('Europe/Prague')).strftime("%d/%m/%Y %H:%M:%S")
    load_time = format_timespan(time.time() - start_time)
    msg = f"\nHere comes Bruce!\n[With {cog_count} cogs]\n[{tn}]\n[{load_time}]\n<t:{int(time.time())}:R>"
    startup = client.get_channel(startup_channel_id)

    print(msg)
    await startup.send(msg)

## Error Handlers ##
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.message.add_reaction('❓')
    elif isinstance(error, commands.MissingRole):
        await ctx.message.add_reaction('❌')
        await ctx.send('This command requires a role you don\'t have.')
    elif isinstance(error, commands.CheckFailure):
        await ctx.message.add_reaction('❌')
        await ctx.send('This command requires something you don\'t have.')
    else:
        print(error)
        err = client.get_channel(error_channel_id)
        await err.send(f"on_command_error: \n ```{error}```")

        await ctx.send('Some unforseen error occured. Someone has been notified about this.')
        await ctx.message.add_reaction('❌')


client.run(token)
