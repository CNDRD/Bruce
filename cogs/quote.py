from func.firebase_init import db

import disnake
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

    @commands.slash_command(
        name="quote",
        description="Creates a quote",
        options=[
            disnake.Option(
                name="quote",
                description="The quote itself",
                type=disnake.OptionType.string,
                required=True
            ),
            disnake.Option(
                name="author",
                description="Who said it",
                type=disnake.OptionType.string,
                required=True
            ),
            disnake.Option(
                name="when",
                description="When did they (\"now\" for today)",
                type=disnake.OptionType.string,
                required=True
            )
        ]
    )
    async def quote(self, inter, quote, author, when):
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
