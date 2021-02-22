from func.console_logging import cl
from func.siege import rainbow6stats

from discord.ext import commands, tasks
import pyrebase, yaml, json, asyncio

## Config Load ##
config = yaml.safe_load(open('config.yml'))
bot_mod_role_id = config.get('bot_mod_role_id')
r6s_role_id = config.get('r6s_role_id')

error_channel_id = config.get('error_channel_id')

dbr6_loop_time = config.get('dbr6_loop_time')
r6_stats_loop = config.get('r6_stats_loop')

## Firebase Database ##
db = pyrebase.initialize_app( json.loads(config.get('firebase')) ).database()


class Siege(commands.Cog):
    def __init__(self, client):
        """
        Rainbow Six Siege stats commands.

        - dbr6 (loop)
        - stats_update
        - r6set

        Goes to r6.tracker.network where it converts UBI ID to UBI Username;
        Using r6stats.com API gathers all the useful data
        & stores them in the Firebase Database
        """
        self.client = client
        if r6_stats_loop: self.dbr6.start()

    @tasks.loop(minutes=dbr6_loop_time)
    async def dbr6(self):
        cl('', 'Siege', 'dbr6')

        # Get all user Ubi IDs & Discord usernames
        users = db.child('R6S').child('IDs').get()

        # Get Siege stats from every Ubi ID stored in 'users' variable and store it in the database
        for u in users.each():
            if (ubi_id := u.val().get('ubiID')) is not None:
                discord_username = u.val().get('discordUsername')
                data = rainbow6stats(ubi_id, discord_username)
                db.child('R6S').child('stats').child(ubi_id).update(data)


    @commands.command(aliases=['su'])
    @commands.has_role(bot_mod_role_id)
    async def stats_update(self, ctx):
        cl(ctx)
        # Since the 'dbr6V2' loop runs only every hour if there is a need
        # to manually update the stats this is the only way
        # Well the only way other than restarting the bot..
        self.dbr6.cancel()
        # This 0.5s delay needs to be here because who the fuck knows why
        await asyncio.sleep(0.5)
        self.dbr6.start()
        await ctx.message.add_reaction('✅')


    @commands.command()
    @commands.has_role(r6s_role_id)
    async def r6set(self, ctx, link: str):
        cl(ctx)
        user_id = ctx.author.id
        try:
            # Remove the hyperlink part of the message if necessary
            if link.startswith("https://r6.tracker.network/profile/id/"):
                link = link.replace('https://r6.tracker.network/profile/id/', '')

            # Set up the Ubi ID under the users database entry
            data = {'ubiID': link, 'discordUsername': str(ctx.author)}
            db.child('R6S').child('IDs').child(user_id).update(data)

            # Update the stats with the new person in now straight away
            data = rainbow6stats(link, str(ctx.author))
            db.child('R6S').child('stats').child(link).update(data)

            await ctx.message.add_reaction('✅')

        except Exception as e:
            await ctx.message.add_reaction('❌')
            await ctx.send("Something went wrong")
            err_ch = self.client.get_channel(error_channel_id)
            await err_ch.send(f'**r6set:**\nlink: {link}\nuid: {user_id}\ncould not set link\n`{e}`')


def setup(client):
    client.add_cog(Siege(client))
