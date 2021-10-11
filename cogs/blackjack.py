from func.firebase_init import db

from func.blackjack import *

from disnake.ext.commands import Param
from disnake.ext import commands


class BJ(disnake.ui.View):
    def __init__(self, og_inter: disnake.MessageInteraction, bet: int, user_money: int):
        super().__init__()
        self.result = None  # lose: -1; tie: 0; win: 1; user BJ: 2
        self.action = None
        self.og_inter = og_inter
        self.bet = bet
        self.user_money = user_money
        self.deck = new_deck()
        self.player, self.dealer = deal_first_hand(self.deck)

    @disnake.ui.button(label="Stand", style=disnake.ButtonStyle.gray)
    async def stand(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if self.og_inter.author.id != inter.author.id:
            return await inter.response.send_message("You are NOT allowed to do this..", ephemeral=True)

        self.action = 20
        while sum(self.dealer) <= 16:
            self.dealer.append(self.deck.pop(0))

        self.stop()
        await self.og_inter.edit_original_message(embed=generate_game_embed(self), view=None)
        return db.child('users').child(self.og_inter.author.id).update({'money': get_result_money(self)})

    @disnake.ui.button(label="Hit", style=disnake.ButtonStyle.success)
    async def hit(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if self.og_inter.author.id != inter.author.id:
            return await inter.response.send_message("You are NOT allowed to do this..", ephemeral=True)

        self.action = 30
        self.player.append(self.deck.pop(0))

        if sum(self.player) > 21 or sum(self.player) == 21:
            self.stop()
            await self.og_inter.edit_original_message(embed=generate_game_embed(self), view=None)
            return db.child('users').child(self.og_inter.author.id).update({'money': get_result_money(self)})

        await self.og_inter.edit_original_message(embed=generate_game_embed(self), view=self)


class BlackJack(commands.Cog):
    def __init__(self, client):
        """Blackjack game."""
        self.client = client

    @commands.slash_command(name="blackjack", description="Game of Black Jack")
    async def _blackjack(self, inter: disnake.MessageInteraction, bet: int = Param(..., desc="Place your bet!")):

        user_money = db.child('users').child(inter.author.id).child('money').get().val()
        # user_money = 10
        if bet <= 0:
            return await inter.response.send_message("You can't do that, and you know it..", ephemeral=True)
        if bet > user_money:
            message = f"You cannot bet more than you have.. (You have {user_money:,} monies)".replace(',', ' ')
            return await inter.response.send_message(message, ephemeral=True)

        game = BJ(inter, bet, user_money)

        if sum(game.player) == sum(game.dealer) and sum(game.player) == 21:  # Tie
            game.action = 0
            game.result = 0
        elif sum(game.player) != sum(game.dealer) and sum(game.player) == 21:  # Player W
            game.action = 1
            game.result = 0
        elif sum(game.dealer) == 21:  # Dealer W
            game.action = 2
            game.result = -1

        if game.action is not None:
            await inter.response.send_message(embed=generate_game_embed(game))
            return db.child('users').child(inter.author.id).update({'money': get_result_money(game)})

        game.action = 69
        await inter.response.send_message(embed=generate_game_embed(game), view=game)


def setup(client):
    client.add_cog(BlackJack(client))
