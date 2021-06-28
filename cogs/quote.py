import pyrebase, yaml, discord, datetime, time, json, os
from discord.ext import commands
from pytz import timezone

from dislash import *

from dotenv import load_dotenv
load_dotenv()

## Config Load ##
config = yaml.safe_load(open('config.yml'))
bot_mod_role_id = config.get('bot_mod_role_id')
slash_guilds = config.get('slash_guilds')

## Firebase Database ##
firebase_config = {"apiKey": "AIzaSyDe_xKKup4lVoPasLmAQW9Csc1zUzsxB0U","authDomain": "chuckwalla-69.firebaseapp.com",
  "databaseURL": "https://chuckwalla-69.firebaseio.com","storageBucket": "chuckwalla-69.appspot.com",
  "serviceAccount": json.loads(os.getenv("serviceAccountKeyJSON"))}
db = pyrebase.initialize_app(firebase_config).database()

class Quote(commands.Cog):
    def __init__(self, client):
        """
        Quote command.
        """
        self.client = client


    @slash_commands.command(
        guild_ids=slash_guilds,
        description="Set the quote to be shown on diskito.eu/quotes",
        options=[
            Option(
                name="quote",
                description="The quote itself",
                required=True
            ),
            Option(
                name="author",
                description="Who said this"
            ),
            Option(
                name="when",
                description="When did they say this. Type 'now' for today"
            )
        ]
    )
    async def quote(self, ctx, quote, author=None, when=None):
        quote_id = db.generate_key()

        data = {"quote": quote}

        if author is not None:
            data["by"] = author
        else:
            data["by"] = "unknown"

        if when is not None:
            if when.lower() == "now":
                when = datetime.datetime.now(timezone('Europe/Prague')).strftime('%d.%m.%Y')
            data["when"] = when
        else:
            data["when"] = "unknown"

        data['timestamp'] = int(time.time())
        db.child('quotes').child(quote_id).update(data)

        await ctx.create_response("Success!", ephemeral=True)


def setup(client):
    client.add_cog(Quote(client))
