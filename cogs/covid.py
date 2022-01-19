from func.covid import get_nakazeni_reinfekce_embed

import disnake
from disnake.ext import commands


class Covid(commands.Cog):
    def __init__(self, client):
        """Covid-19 data."""
        self.client = client

    @commands.slash_command(name="covid", description="Latest COVID-19 data")
    async def _covid(self, inter: disnake.ApplicationCommandInteraction):
        embed = get_nakazeni_reinfekce_embed()
        await inter.send(embed=embed)


def setup(client):
    client.add_cog(Covid(client))
