from func.firebase_init import db
from func.stuff import add_spaces

import discord, yaml, random
from discord.ext import commands

## Config Load ##
config = yaml.safe_load(open('config.yml'))
mod_role_id = config.get('mod_role_id')
succes_emoji = config.get('succes_emoji')


class User(commands.Cog):
    def __init__(self, client):
        """
        Collection of short user facing commands.
        - connect (to web)
        - code
        - ping
        - vanish
        - coinflip
        - flipflop
        """
        self.client = client


    @commands.command()
    async def connect(self, ctx, code=None):
        if code is None: return await ctx.send("You forgot the code chump")
        db.child("discordConnection").child(ctx.author.id).set(code)
        await ctx.message.add_reaction('✅')


    @commands.command()
    async def code(self, ctx):
        embed = discord.Embed(colour=discord.Colour.random())
        embed.set_author(name='GitHub Repo', url='https://github.com/CNDRD/Bruce')
        await ctx.send(embed=embed)


    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f"Pong ({round(self.client.latency*1000)}ms)")


    @commands.command()
    async def vanish(self, ctx):
        await ctx.message.add_reaction('✅')
        await ctx.author.kick(reason='Self-kick')


    @commands.command(aliases=['coin', 'flip'])
    async def coinflip(self, ctx, *args):
        if len(args) == 0 or len(args) == 1:
            outcomes = ('Heads', 'Tails')
            msg = outcomes[random.SystemRandom().randint(0,1)]
        else:
            msg = args[random.SystemRandom().randint(0,len(args)-1)]
        await ctx.send(f"**{msg}**")


    @commands.command(aliases=['flip-flop'])
    async def flipflop(self, ctx):
        e = discord.utils.get(ctx.guild.emojis, name="kapp")
        await ctx.message.add_reaction(e)


def setup(client):
    client.add_cog(User(client))
