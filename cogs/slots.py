from func.firebase_init import db
from func.slots import get_slots, int_to_slots, calc_winnings

from disnake.ext.commands import Param
from disnake.ext import commands
import disnake


class Slots(commands.Cog):
    def __init__(self, client):
        """Casino Slots game simulator"""
        self.client = client

    @commands.slash_command(name="slots", description="Casino Slots")
    async def _slots(
            self,
            inter: disnake.CommandInteraction,
            bet: int = Param(10, desc="How much are you betting?")
    ):
        if bet <= 0:
            return await inter.send("Funny guy..", ephemeral=True)

        user_money = db.child("users").child(inter.author.id).child("money").get().val()
        if bet > user_money:
            return await inter.send("You cannot bet more shekels than you have breh..", ephemeral=True)

        user_money -= bet

        a, b, c = get_slots()
        winnings = calc_winnings((a, b, c), bet)
        sa, sb, sc = int_to_slots(a), int_to_slots(b), int_to_slots(c)

        db.child("users").child(inter.author.id).update({"money": int(user_money + winnings)})

        await inter.send(f"{sa} {sb} {sc}\nYou win **{winnings:,}** shekels!".replace(",", " "))


def setup(client):
    client.add_cog(Slots(client))
