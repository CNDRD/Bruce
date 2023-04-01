from func.supabase import supabase

import disnake
from disnake.ext.commands import Param
from disnake.ext import commands

import datetime
from pytz import timezone


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
            when: str = Param('now', desc="When did they (\"now\" for today)")
    ):
        if when.lower() == "now":
            when = datetime.datetime.now(timezone('Europe/Prague')).strftime("%d.%m.%Y")

        lmao = supabase.from_('quotes').insert({"quote": quote, "by": author, "when": when}).execute()
        await inter.response.send_message(f"Successfully set-up the quote with an id `{lmao.data[0]['id']}`", ephemeral=True)


def setup(client):
    client.add_cog(Quote(client))
