from func.console_logging import cl

import pyrebase, yaml, json, discord
from discord.ext import commands

## Config Load ##
config = yaml.safe_load(open('config.yml'))
bot_mod_role_id = config.get('bot_mod_role_id')
mod_role_id = config.get('mod_role_id')

## Firebase Database ##
db = pyrebase.initialize_app( json.loads(config.get('firebase')) ).database()


class Admin(commands.Cog):
    def __init__(self, client):
        """
        Admin commands.

        - backup_db
        - clear
        - add_reaction
        """
        self.client = client


    @commands.command(aliases=['bdb'])
    @commands.is_owner()
    async def backup_db(self, ctx):
        cl(ctx)
        dm_ch = await ctx.author.create_dm()
        with open("db_backup.json","w") as f:
            f.write(json.dumps(db.get().val(), indent=2))
        with open("db_backup.json", "rb") as f:
            await dm_ch.send(file=discord.File(f, "db_backup.json"))


    @commands.command()
    @commands.has_any_role(bot_mod_role_id, mod_role_id)
    async def clear(self, ctx, amount: int = 1):
        cl(ctx)
        await ctx.channel.purge(limit=(amount+1))


    @commands.command(aliases=['add'])
    @commands.has_any_role(bot_mod_role_id, mod_role_id)
    async def add_reaction(self, ctx, e):
        ref_ch = self.client.get_channel(ctx.message.reference.channel_id)
        ref_msg = await ref_ch.fetch_message(ctx.message.reference.message_id)
        await ref_msg.add_reaction(e)
        await ctx.message.delete()


    @commands.command()
    @commands.has_any_role(bot_mod_role_id, mod_role_id)
    async def say(self, ctx, *, a):
        await ctx.send(a)
        await ctx.message.delete()


    @commands.command()
    @commands.has_any_role(bot_mod_role_id, mod_role_id)
    async def edit(self, ctx, *, a):
        ref_ch = self.client.get_channel(ctx.message.reference.channel_id)
        ref_msg = await ref_ch.fetch_message(ctx.message.reference.message_id)
        await ref_msg.edit(content=a)
        await ctx.message.delete()


def setup(client):
    client.add_cog(Admin(client))
