from func.firebase_init import db

import disnake
from disnake.ext.commands import Param
from disnake.ext import commands

import yaml
import datetime
import time
from pytz import timezone


## Config Load ##
local_timezone = yaml.safe_load(open('config.yml')).get('local_timezone')


class Quote(commands.Cog):
    def __init__(self, client):
        """Quote command."""
        self.client = client

    @commands.slash_command(name="quote", description="Creates a quote")
    async def quote(
            self,
            inter: disnake.ApplicationCommandInteraction,
            quote: str = Param(..., desc="The quote itself"),
            author: str = Param(..., desc="Who said it"),
            when: str = Param(..., desc="When did they (\"now\" for today)")
        ):
        quote_id = db.generate_key()

        if when.lower() == "now":
            when = datetime.datetime.now(timezone(local_timezone)).strftime('%d.%m.%Y')

        data = {
            "quote": quote,
            "by": author,
            "when": when,
            "timestamp": int(time.time())
        }

        db.child('quotes').child(quote_id).update(data)
        await inter.response.send_message(f'Successfully set-up the quote with an id `{quote_id}`', ephemeral=True)


def setup(client):
    client.add_cog(Quote(client))
