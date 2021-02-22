from func.console_logging import cl

import pyrebase, yaml, json, discord
from discord.ext import commands

## Config Load ##
config = yaml.safe_load(open('config.yml'))

## Firebase Database ##
db = pyrebase.initialize_app( json.loads(config.get('firebase')) ).database()


class Admin(commands.Cog):
    def __init__(self, client):
        """
        Admin commands.

        - backup_db
        - clear
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
    async def clear(self, ctx, amount: int = 1):
        cl(ctx)
        await ctx.channel.purge(limit=(amount+1))


def setup(client):
    client.add_cog(Admin(client))
