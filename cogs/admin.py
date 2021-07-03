import pyrebase, yaml, json, discord, os
from discord.ext import commands

from dotenv import load_dotenv
load_dotenv()

## Config Load ##
config = yaml.safe_load(open('config.yml'))
owner_role_id = config.get('owner_role_id')
bot_mod_role_id = config.get('bot_mod_role_id')
mod_role_id = config.get('mod_role_id')

## Firebase Database ##
firebase_config = {"apiKey": "AIzaSyDe_xKKup4lVoPasLmAQW9Csc1zUzsxB0U","authDomain": "chuckwalla-69.firebaseapp.com",
  "databaseURL": "https://chuckwalla-69.firebaseio.com","storageBucket": "chuckwalla-69.appspot.com",
  "serviceAccount": json.loads(os.getenv("serviceAccountKeyJSON"))}
db = pyrebase.initialize_app(firebase_config).database()


class Admin(commands.Cog):
    def __init__(self, client):
        """
        Admin commands.

        - backup_db
        - clear
        - add_reaction
        - say
        - edit
        """
        self.client = client


    @commands.command(aliases=['bdb'])
    @commands.has_role(owner_role_id)
    async def backup_db(self, ctx):
        dm_ch = await ctx.author.create_dm()
        with open("db_backup.json","w") as f:
            f.write(json.dumps(db.get().val(), indent=2))
        with open("db_backup.json", "rb") as f:
            await dm_ch.send(file=discord.File(f, "db_backup.json"))


    @commands.command()
    @commands.has_any_role(bot_mod_role_id, mod_role_id)
    async def clear(self, ctx, amount: int = 1):
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
