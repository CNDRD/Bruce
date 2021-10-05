from typing import List, Tuple
import random
import disnake

number_of_decks = 4
default_message = "Diskíto Black Jack"


def new_deck() -> List:
    deck = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11] * 4
    deck = deck * number_of_decks
    random.shuffle(deck)
    return deck


def deal_first_hand(deck: List[int]) -> Tuple[List[int], List[int]]:
    player = [deck.pop(0)]
    dealer = [deck.pop(0)]
    player.append(deck.pop(0))
    dealer.append(deck.pop(0))

    while sum(player) > 21:
        deck.extend(player)
        player = [deck.pop(0), deck.pop(0)]

    while sum(dealer) > 21:
        deck.extend(dealer)
        dealer = [deck.pop(0), deck.pop(0)]

    return player, dealer


def generate_game_embed(game) -> disnake.Embed():
    mess = _get_embed_message(game)

    embed = disnake.Embed(color=_get_embed_color(game))
    embed.set_author(name=mess)
    embed.set_footer(text=_get_embed_footer(game))
    embed.add_field(name="Dealer", value=sum(game.dealer), inline=True)
    embed.add_field(name="You", value=sum(game.player), inline=True)
    return embed


def _get_embed_footer(game) -> str:
    if game.result is not None:
        result_money = get_result_money(game)
        res_mon = result_money - game.user_money
        money_outcome = res_mon+game.bet if game.result == 1 or game.result == 2 else res_mon
        return f"Bet: {game.bet:,} monies | Result: {money_outcome:,} | Monies remaining: {result_money:,}".replace(',', ' ')
    return f"Bet: {game.bet}"


def get_result_money(game) -> int:
    if game.result is None or game.result == 0:  # XD
        return game.user_money
    if game.result == -1:  # L
        return game.user_money - game.bet
    if game.result == 1:  # W
        return game.user_money + game.bet
    if game.result == 2:  # BJ
        return int(game.user_money + (game.bet * 1.5))


def _get_embed_color(game) -> disnake.Color:
    if game.result is None:
        return disnake.Color.blurple()
    if game.result == -1:  # Dealer W
        return disnake.Color.red()
    if game.result == 0:  # Tie
        return disnake.Color.greyple()
    if game.result == 1 or game.result == 2:
        return disnake.Color.green()
    return disnake.Color.yellow()


def _get_embed_message(game) -> str:
    # default tie (both BJ)
    if game.action == 0:
        game.result = 0
        return "Both you and the dealer have Black Jacks!"

    # default win (player BJ)
    if game.action == 1:
        game.result = 2
        return "Black Jack! You've won!"

    # default lose (dealer BJ)
    if game.action == 2:
        game.result = -1
        return "Dealer has Black Jack.\nYou lose.."

    # Stand
    if game.action == 20:
        if sum(game.dealer) > 21:
            game.result = 1
            return "You Win! Dealer bust."

        if sum(game.dealer) == sum(game.player) <= 21:
            game.result = 0
            return "Draw!"

        if sum(game.dealer) == 21:
            game.result = -1
            return "You Lose! Dealer has Black Jack."

        if sum(game.player) > sum(game.dealer):
            game.result = 1
            return "You Win!"

        if sum(game.player) < sum(game.dealer):
            game.result = -1
            return "You lose.. Dealer wins."

        return default_message

    # Hit
    if game.action == 30:
        if sum(game.player) > 21:
            game.result = -1
            return "Bust! You lose.."

        if sum(game.player) == 21:
            game.result = 2
            return "Black Jack! You win!!"

        return default_message

    # uh oh
    if game.action == 69:
        return default_message

    #  Neither of the following should ever happen
    if game.action is None:
        return "action is None"

    return "WHAT HOW"

