from func.firebase_init import db
import pyrebase, yaml, datetime, time, json, os
from discord.ext import commands
from pytz import timezone

from dotenv import load_dotenv
load_dotenv()

## Config Load ##
config = yaml.safe_load(open('config.yml'))
bot_mod_role_id = config.get('bot_mod_role_id')


class Quote(commands.Cog):
    def __init__(self, client):
        """
        Quote command.
        """
        self.client = client

    @commands.command()
    async def quote(self, ctx, *quote):

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
            await mess.edit(content=f'Quote now looks like this: \n***{quote}*** *-{quote_by.content}* \n*You now have 20 seconds to reply with a date or type `now` for now.*\n`dd.mm.yyyy` is a preferred format.')

            try:
                quote_when = await self.client.wait_for('message', timeout=20.0, check=check)
            except:
                await mess.edit(content=f'Final quote: \n***{quote}*** *-{quote_by.content}*\nQuote can be deleted using this ID: `{quote_id}`')
                data = {"quote": quote, "by": quote_by.content, "when": "unknown"}
            else:
                await quote_when.delete()
                when = quote_when.content

                if when == "now":
                    datetime.datetime.now(timezone('Europe/Prague')).strftime('%d.%m.%Y')

                await mess.edit(content=f'Final quote: \n***{quote}*** *-{quote_by.content}*, {when}\nQuote can be deleted using this ID: `{quote_id}`')
                data = {"quote": quote, "by": quote_by.content, "when": when}

        data['timestamp'] = int(time.time())

        db.child('quotes').child(quote_id).update(data)
        await mess.add_reaction('✅')


def setup(client):
    client.add_cog(Quote(client))
