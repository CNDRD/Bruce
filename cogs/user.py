from func.console_logging import cl
from func.stuff import add_spaces

import pyrebase, discord, yaml, discord, random, json
from discord.ext import commands

## Config Load ##
config = yaml.safe_load(open('config.yml'))
mod_role_id = config.get('mod_role_id')
succes_emoji = config.get('succes_emoji')


class User(commands.Cog):
    def __init__(self, client):
        """
        Collection of short user facing commands.

        - code
        - ping
        - vanish
        - coinflip
        - flipflop
        """
        self.client = client


    @commands.command()
    async def code(self, ctx):
        cl(ctx)
        embed = discord.Embed(colour=discord.Colour.random())
        embed.set_author(name='GitHub Repo', url='https://github.com/CNDRD/Bruce')
        await ctx.send(embed=embed)


    @commands.command()
    async def ping(self, ctx):
        cl(ctx)
        await ctx.send(f"Pong ({round(self.client.latency*1000)}ms)")


    @commands.command()
    async def vanish(self, ctx):
        cl(ctx)
        await ctx.message.add_reaction('✅')
        await ctx.author.kick(reason='Self-kick')


    @commands.command(aliases=['coin', 'flip'])
    async def coinflip(self, ctx, heads: str = "Heads", tails: str = "Tails"):
        cl(ctx)
        if random.SystemRandom().randint(1,100) % 2 == 0:
            msg = heads
        else:
            msg = tails
        await ctx.send(f"**{msg}**")


    @commands.command(aliases=['flip-flop'])
    async def flipflop(self, ctx):
        cl(ctx)
        e = discord.utils.get(ctx.guild.emojis, name="kapp")
        await ctx.message.add_reaction(e)


def setup(client):
    client.add_cog(User(client))
