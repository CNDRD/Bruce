from func.firebase_init import db

import disnake
from disnake.ext.commands import Param
from disnake.ext import commands

from datetime import datetime
from pytz import timezone
import random
import yaml


# Config Load
local_timezone = yaml.safe_load(open("config.yml")).get("local_timezone")


class User(commands.Cog):
    def __init__(self, client):
        """Collection of short user facing commands."""
        self.client = client

    @commands.slash_command(name="claim", description="Claim your daily shekel bonus")
    async def _claim(self, inter: disnake.ApplicationCommandInteraction):
        today = datetime.now(timezone(local_timezone)).strftime("%Y-%m-%d")
        usr = db.child("users").child(inter.author.id).get().val()
        last_claim = usr.get("last_money_claim", "0000-00-00")
        monies = usr.get("money")
        lvl = usr.get("level")
        claim_money = lvl * 1_000

        if last_claim != today:

            total_claimed = int(db.child("moneyTotals").child("claim").get().val() or 0)
            db.child("moneyTotals").child("claim").set(str(total_claimed + claim_money))

            db.child("users").child(inter.author.id).update({"money": monies + claim_money, "last_money_claim": today})
            return await inter.send(f"You have successfully claimed **{claim_money:,}** shekels!".replace(",", " "))

        midnight_ts = int(datetime.now(timezone(local_timezone)).replace(hour=0, minute=0, second=0).timestamp() + 86400)
        return await inter.send(content=f"You already claimed your money today! (Next claim available ~<t:{midnight_ts}:R>)")

    @commands.slash_command(name="send", description="Send shekels to someone")
    async def _send(
            self,
            inter: disnake.ApplicationCommandInteraction,
            user: disnake.Member = Param(..., desc="Who are you sending the shekels to?"),
            shekels: int = Param(..., desc="How much shekels are you sending?")
    ):
        if inter.author.id == user.id:
            return await inter.response.send_message(f"Successfully sent **{shekels:,}** shekel{'s' if shekels > 1 else ''} to yourself, you dumb fuck..", ephemeral=True)
        
        if user.bot:
            return await inter.response.send_message("You can't send money to a bot..", ephemeral=True)
        
        author_money = db.child("users").child(inter.author.id).child("money").get().val() or 0
        
        if shekels > author_money:
            return await inter.response.send_message("Cannot send more shekels than you have..", ephemeral=True)
        
        user_money = db.child("users").child(user.id).child("money").get().val() or 0
        
        db.child("users").child(inter.author.id).update({ "money": (author_money - shekels) })
        db.child("users").child(user.id).update({ "money": (user_money + shekels) })
        
        await inter.response.send_message(f"Successfully sent **{shekels:,}** shekel{'s' if shekels > 1 else ''} to {user.name}.\nYou now have {(author_money - shekels):,} shekels", ephemeral=True)
        
    @commands.slash_command(name="ping", description="Gets the bot's ping")
    async def ping(self, inter):
        await inter.response.send_message(f"Pong ({round(self.client.latency * 1000)}ms)")

    @commands.slash_command(name="code", description="Link to the source code on GitHub")
    async def code(self, inter):
        view = disnake.ui.View()
        view.add_item(disnake.ui.Button(label="GitHub", url="https://github.com/CNDRD/Bruce"))
        await inter.response.send_message(content="Here you go:", view=view)

    @commands.slash_command(name="coinflip", description="Flips a coin")
    async def coinflip(
            self,
            inter: disnake.ApplicationCommandInteraction,
            heads: str = Param("Heads", desc="What to send"),
            tails: str = Param("Tails", desc="What to send")
    ):
        outcomes = (heads, tails)
        msg = outcomes[random.SystemRandom().randint(0, 1)]
        await inter.response.send_message(f"**{msg}**", ephemeral=True)

    @commands.slash_command(name="money", description="Shows your balance")
    async def money(self, inter: disnake.ApplicationCommandInteraction):
        monies = db.child("users").child(inter.author.id).child("money").get().val()
        await inter.response.send_message(f"You have {monies:,} shekels", ephemeral=True)

def setup(client):
    client.add_cog(User(client))
