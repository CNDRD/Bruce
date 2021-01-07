import pyrebase, discord, yaml, time, os, json
from humanfriendly import format_timespan
from discord.ext import commands, tasks
from datetime import datetime

print('Starting to load..')
start_time = time.time()

################################################################ Config Load ##
config = yaml.safe_load(open("config.yml"))
cl = config.get('console_logging')
prefix = str(config.get('prefix'))
error_channel_id = config.get('error_channel_id')
startup_channel_id = config.get('startup_channel_id')
db_auto_backup_loop = config.get('db_auto_backup_loop')

################################################################### Firebase ##
fb = json.loads(config.get('firebase'))
firebase = pyrebase.initialize_app(fb)
db = firebase.database()

############################################################ Basic Bot Setup ##
intents = discord.Intents.all()
client = commands.Bot(command_prefix=prefix, intents=intents)
client.remove_command('help')
token = 'NjkwMzYyMTI5MTI3MzA5MzUy.Xo-3Kw.iBWBkRnfE72qnlzlcbqX48I5xfY'
cog_count = 0

################################################################# Cog Loader ##
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')
        cog_count += 1

################################################################### Commands ##
@client.event
async def on_ready():
    if cl: print('START on_ready() ', end="")
    if db_auto_backup_loop: dbAutoBackup.start()
    snowmenRoleGiving.start()

    tn = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    load_time = format_timespan(time.time() - start_time)
    msg = f"\nHere comes Bruce!\n[With {cog_count} cogs]\n[{tn}]\n[{load_time}]\n"
    startup = client.get_channel(startup_channel_id)

    if cl: print("END")
    print(msg)
    await startup.send(msg)

############################################################# Error Handlers ##
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.message.add_reaction('❌')
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


@tasks.loop(hours=12.0)
async def dbAutoBackup():
    if cl: print('START dbAutoBackup loop ', end="")
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"dbAutoBackup_{stamp}.json"

    with open(filename,"w") as f:
        f.write(json.dumps(db.get().val(), indent=2))

    for guild in client.guilds:
        if guild.id == 703307518230790274:
            for channel in guild.channels:
                if channel.id == 764488011911004210:
                    with open(filename, "rb") as f:
                        await channel.send(file=discord.File(f, filename))
    if cl: print("END")


@tasks.loop(minutes=15.0)
async def snowmenRoleGiving():
    mess = "```fix\n snowmen \n"
    snowmenDB = db.child('snowmen').get()
    if snowmenDB.val() is not None:
        for s in snowmenDB.each():
            un = s.val()['username']
            mess += f"{un}\n"
            db.child('snowmen').child(s.key()).remove()

            for guild in client.guilds:
                for member in guild.members:
                    if member.id == 210471447649320970:
                        dm_ch = await member.create_dm()
        mess += '```'
        await dm_ch.send(mess)


client.run(token)
