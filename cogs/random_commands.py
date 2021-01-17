import pyrebase, random, discord, json, yaml, datetime, time
from humanfriendly import format_timespan
from discord.ext import commands, tasks
from pytz import timezone

################################################################ Config Load ##
config = yaml.safe_load(open("config.yml"))
cl = config.get('console_logging')
diagnostics_role_id = config.get('diagnostics_role_id')
lord_farquaad_role_id = config.get('lord_farquaad_role_id')

################################################################### Firebase ##
fb = json.loads(config.get('firebase'))
firebase = pyrebase.initialize_app(fb)
db = firebase.database()

################################################################## Functions ##
def get_sheriff(e):
    msg =   '\u200b        🤠\n'
    msg += f'\u200b  {e}{e}{e}\n'
    msg += f'\u200b{e}  {e}   {e}\n'
    msg += f'\u200b👇  {e}    👇\n'
    msg += f'\u200b     {e}  {e}\n'
    msg += f'\u200b    {e}   {e}\n'
    msg +=  '\u200b     👢    👢'
    return msg

def get_square(e, size):
    msg=''
    for _ in range(0,size):
        for _ in range(0, size):
            msg+=f"{e}"
        msg+="\n"
    return msg

def get_cicina():
    rng = random.SystemRandom()
    c1 = rng.randint(0,45)
    c2 = rng.randint(0,45)
    l = (c1,c2)
    return l[l.index(min(l))]

################################################################### Commands ##
class RandomCommands(commands.Cog):
    def __init__(self, client):
        """Random commands."""
        self.client = client


    @commands.command()
    async def vanish(self, ctx):
        if cl: print('START vanish ', end="")
        await ctx.message.add_reaction('✅')
        await ctx.author.kick(reason='Self-kick')
        if cl: print("END")


    @commands.command()
    async def ping(self, ctx):
        if cl: print('START ping ', end="")
        await ctx.send(f"Pong ({round(self.client.latency*1000)}ms)")
        if cl: print("END")


    @commands.command()
    @commands.has_role(diagnostics_role_id)
    async def clear(self, ctx, amount: int = 1):
        if cl: print('START clear ', end="")
        await ctx.channel.purge(limit=(amount+1))
        if cl: print("END")


    @commands.command(aliases=['bdb'])
    @commands.is_owner()
    async def backup_db(self, ctx):
        if cl: print('START backup_db ', end="")
        dm_ch = await ctx.author.create_dm()
        with open("db_backup.json","w") as f:
            f.write(json.dumps(db.get().val(), indent=2))
        with open("db_backup.json", "rb") as f:
            await dm_ch.send(file=discord.File(f, "db_backup.json"))
        if cl: print("END")


    @commands.command(aliases=["joined"])
    @commands.is_owner()
    async def manually_add_to_db(self, ctx, uid = None):
        if cl: print('START manually_add_to_db ', end="")
        if uid is None:
            await ctx.message.add_reaction('❌')
            return

        member = discord.utils.get(ctx.guild.members, id=uid)
        joinedServer = int((member.joined_at).timestamp())
        joinedDiscord = int((member.created_at).timestamp())
        avatarURL = str(member.avatar_url_as(size=4096))

        d = {'reacc_points':0,
             'username':str(member),
             'xp':0,
             'level':0,
             'last_xp_get':0,
             'messages_count':0,
             'joined_server':joinedServer,
             'joined_discord':joinedDiscord,
             'avatar_url':avatarURL,
             'in_server':True
            }
        db.child('users').child(member.id).set(d)
        await ctx.message.add_reaction('✅')
        if cl: print("END")


    @commands.command()
    async def sheriff(self, ctx, e=None):
        if cl: print('START sheriff ', end="")
        if e is None:
            e = '🖕'
        elif '<' in e and '>' in e:
            e = e.split(':')
            e = discord.utils.get(ctx.guild.emojis, name=str(e[1]))
        else:
            e = e.replace(':','')
            e = discord.utils.get(ctx.guild.emojis, name=str(e))
        await ctx.send(get_sheriff(e))
        await ctx.message.delete()
        if cl: print("END")


    @commands.command(aliases=['flip-flop'])
    async def flipflop(self, ctx):
        if cl: print('START flipflop ', end="")
        e = discord.utils.get(ctx.guild.emojis, name="kapp")
        await ctx.message.add_reaction(e)
        if cl: print("END")


    @commands.command(aliases=['coin', 'flip'])
    async def coinflip(self, ctx, heads: str = "Heads", tails: str = "Tails"):
        if cl: print('START coinflip ', end="")
        rng = random.SystemRandom()
        why = rng.randint(1,100) % 2

        if why == 0:
            msg = heads
        else:
            msg = tails
        await ctx.send(f"**{msg}**")
        if cl: print("END")


    @commands.command(aliases=['es'])
    async def emoji_square(self, ctx, e=None, size: int = 5):
        if cl: print('START emoji_square ', end="")
        if e is None:
            e = '🖕'
        elif '<' in e and '>' in e:
            e = e.split(':')
            e = discord.utils.get(ctx.guild.emojis, name=str(e[1]))
        else:
            e = e.replace(':','')
            e = discord.utils.get(ctx.guild.emojis, name=str(e))

        if (msg_len := len(get_square(e, size))) > 2000:
            await ctx.message.add_reaction('❌')
            await ctx.send(f'Maximum length of a message is 2000 characters.. ({msg_len} chars)')
        else:
            await ctx.send(get_square(e,size))
        if cl: print("END")


    @commands.command()
    async def code(self, ctx):
        if cl: print('START code ', end="")

        embed = discord.Embed(colour=discord.Colour.random())
        embed.set_author(name='GitHub Repo', url='https://github.com/CNDRD/Bruce')
        await ctx.send(embed=embed)

        if cl: print("END")


    @commands.command()
    async def cicina(self, ctx):
        if cl: print('START cicina ', end="")
        uid = ctx.author.id
        today = datetime.datetime.now(timezone('Europe/Prague')).strftime('%Y-%m-%d')
        cicina = get_cicina()

        cicinaLast = db.child('users').child(uid).child('cicina_last').get().val()
        if cicinaLast is None: cicinaLast = 0

        cicinaLongest = db.child('users').child(uid).child('cicina_longest').get().val()
        if cicinaLongest is None: cicinaLongest = 0

        if cicinaLast != today:
            emote = discord.utils.get(ctx.guild.emojis, name="resttHA")
            msg = f'{ctx.author.mention} - Dĺžka tvojej ciciny je {cicina} centimetrov {emote}'

        else:
            msg = f'{ctx.author.mention} - Cicina sa ti resetuje zajtra'


        if cicina > cicinaLongest:
            cicina_for_db = cicina
        else:
            cicina_for_db = cicinaLongest


        cicinaAvg = db.child('users').child(uid).child('cicina_avg').get().val()
        cicinaCount = db.child('users').child(uid).child('cicina_count').get().val()


        if cicinaCount is None:
            new_count = 1
            new_avg = cicina

        else:
            new_avg = (cicinaAvg * cicinaCount + cicina) / (cicinaCount + 1)
            new_count = cicinaCount + 1

        data = {
            'cicina_longest':cicina_for_db,
            'cicina_last':today,

            'cicina_avg':new_avg,
            'cicina_count':new_count}

        db.child('users').child(uid).update(data)
        await ctx.send(msg)
        if cl: print("END")


    @commands.command()
    @commands.has_role(lord_farquaad_role_id)
    async def quote(self, ctx, *quote):
        if cl: print('START quote ', end="")

        if quote == ():
            await ctx.message.add_reaction('❌')
            await ctx.send('You have to input at least the quote dude..')
            return

        quote = " ".join(quote[:])

        if quote.startswith('-'):
            db.child('quotes').child(quote).remove()
            await ctx.message.add_reaction('✅')
            return

        quote_id = db.generate_key()

        mess = await ctx.send(f'Your Quote: \n***{quote}***\n*You have 10 seconds to reply with an author.*')

        def check(m):
            return m.content is not None and m.channel == ctx.channel

        try:
            quote_by = await self.client.wait_for('message', timeout=10.0, check=check)
        except:
            await mess.edit(content=f'Final quote: \n***{quote}***\nQuote can be deleted using this ID: `{quote_id}`')
            data = {"quote": quote, "by": "unknown", "when": "unknown"}

        else:
            await quote_by.delete()
            await mess.edit(content=f'Quote now looks like this: \n***{quote}*** *-{quote_by.content}* \n*You now have 20 seconds to reply with a date.*\n`dd. mm. yyyy` is a preferred format.')

            try:
                quote_when = await self.client.wait_for('message', timeout=20.0, check=check)
            except:
                await mess.edit(content=f'Final quote: \n***{quote}*** *-{quote_by.content}*\nQuote can be deleted using this ID: `{quote_id}`')
                data = {"quote": quote, "by": quote_by.content, "when": "unknown"}
            else:
                await quote_when.delete()
                await mess.edit(content=f'Final quote: \n***{quote}*** *-{quote_by.content}*, {quote_when.content}\nQuote can be deleted using this ID: `{quote_id}`')

                data = {"quote": quote, "by": quote_by.content, "when": quote_when.content}

        data['timestamp'] = int(time.time())

        db.child('quotes').child(quote_id).update(data)
        await mess.add_reaction('✅')

        if cl: print("END")

def setup(client):
    client.add_cog(RandomCommands(client))
