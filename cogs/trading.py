from func.firebase_init import db
from func.trading import get_current_price, get_multiple_prices, get_trading_buy_db

from disnake.ext.commands import Param
from disnake.ext import commands
import disnake

from typing import Literal


class AvailableTokens(disnake.ui.View):
    def __init__(self):
        super().__init__()
        url = "https://github.com/redstone-finance/redstone-api/blob/main/docs/ALL_SUPPORTED_TOKENS.md"
        self.add_item(disnake.ui.Button(label="List of available tokens", url=url))


class Trading(commands.Cog):
    def __init__(self, client):
        """Trading simulator with real stocks."""
        self.client = client

    @commands.slash_command(name="trade", description="Trading bruh")
    async def _trade(
            self,
            inter: disnake.MessageInteraction,
            operation: Literal["Buy", "Sell", "View"] = Param(..., desc="Are you buying, selling or just wanna view your portfolio?"),
            stock: str = Param(None, desc="Symbol for the stock you wish to trade (Required when buying or selling; optional when viewing)"),
            amount: int = Param(None, desc="How many stocks do you wish to buy/sell (Required only when buying)")
    ):
        await inter.response.defer()

        if stock is not None:
            stock = stock.upper()

        user_money = db.child("users").child(inter.author.id).child("money").get().val()
        currently_owns = db.child("trading").child(inter.author.id).get().val() or None

        match operation:
            case 'Buy':
                if stock is None or amount is None:
                    return await inter.edit_original_message(content=f"**All** parameters are **required** when buying!")
                if currently_owns is not None and stock in currently_owns:
                    return await inter.edit_original_message(content=f"You already own shares of **{stock}**")

                current_price = get_current_price(stock)

                if current_price is None:
                    return await inter.edit_original_message(content=f"Symbol *{stock}* either doesn't exist or I don't have access to it", view=AvailableTokens())

                buying_cost = current_price * amount
                if buying_cost > user_money:
                    return await inter.edit_original_message(content=f"You don't have enough money for this ({int(buying_cost):,} > {user_money:,})".replace(',', ' '))

                db.child("trading").child(inter.author.id).update(get_trading_buy_db(stock, amount, current_price))
                db.child("users").child(inter.author.id).update({"money": int(user_money - buying_cost)})
                return await inter.edit_original_message(content=f"Successfully bought *{amount:,}* shares of **{stock}** for *{int(buying_cost):,}* shekels".replace(',', ' '))

            case 'Sell':
                if currently_owns is None:
                    return await inter.edit_original_message(content="You don't own any stocks!")
                if stock is None:
                    return await inter.edit_original_message(content="You have to specify which stock to sell!")
                if stock not in currently_owns:
                    return await inter.edit_original_message(content="You cannot sell a stock that you don't own!")

                bought_at = currently_owns.get(stock).get("boughtAt")
                amount_bought = currently_owns.get(stock).get("amount")
                bought_cost = bought_at * amount_bought

                current_price = get_current_price(stock)
                selling_cost = current_price * amount_bought

                outcome_money = selling_cost - bought_cost

                profit_loss = "profit" if outcome_money >= 0 else "loss"

                db.child("trading").child(inter.author.id).child(stock).remove()
                db.child("users").child(inter.author.id).update({"money": int(user_money + selling_cost)})

                msg = f"Successfully sold *{amount_bought:,}* stocks of **{stock}** for a {profit_loss} of `{int(outcome_money):,}` shekels".replace(',', ' ')
                return await inter.edit_original_message(content=msg)

            case "View":
                if currently_owns is None:
                    return await inter.edit_original_message(content="You don't own any stocks!")

                if stock is not None:
                    current_price = get_current_price(stock)

                    if stock not in currently_owns:
                        if current_price is None:
                            return await inter.edit_original_message(content=f"Symbol *{stock}* either doesn't exist or I don't have access to it", view=AvailableTokens())

                        msg = f"**{stock}** - Current Price: **{current_price:,}**"
                        return await inter.edit_original_message(content=msg.replace(',', ' '))

                    bought_at = currently_owns.get(stock).get("boughtAt")
                    amount_bought = currently_owns.get(stock).get("amount")
                    bought_cost = bought_at * amount_bought
                    selling_cost = current_price * amount_bought
                    outcome_money = selling_cost - bought_cost

                    current_price = round(current_price, 2) if current_price >= .01 else current_price
                    selling_cost = round(selling_cost, 2) if selling_cost >= .01 else selling_cost
                    bought_at = round(bought_at, 2) if bought_at >= .01 else bought_at
                    bought_cost = round(bought_cost, 2) if bought_cost >= .01 else bought_cost

                    position_worth = current_price * amount_bought
                    position_worth = round(position_worth, 2) if position_worth >= .01 else position_worth

                    msg = f"Your **{stock}** position is worth **{position_worth:,}** shekels\n" \
                          f"Current Price: **{current_price:,}**\n" \
                          f"Bought at: **{bought_at:,}** worth *{bought_cost:,}* shekels\n" \
                          f"Profit: **{int(outcome_money):,}** | " \
                          f"*{amount_bought:,} stock{'s' if amount_bought > 1 else ''}*\n\n"
                    return await inter.edit_original_message(content=msg.replace(',', ' '))

                msg = "__Your current stonks sir:__\n\n"
                currently_owns_prices = get_multiple_prices(currently_owns)
                total_profit = 0

                for stonk in currently_owns:
                    current_price = currently_owns_prices[stonk]
                    bought_price = currently_owns[stonk]['boughtAt']
                    amount_bought = currently_owns[stonk]['amount']
                    profit = (current_price * amount_bought) - (bought_price * amount_bought)
                    total_profit += profit

                    if current_price >= .01:
                        current_price = round(current_price, 2)

                    if bought_price >= .01:
                        bought_price = round(bought_price, 2)

                    msg += f"**{stonk}** - Current Price: **{current_price:,}** | " \
                           f"Bought at: **{bought_price:,}** | " \
                           f"Profit: **{round(profit, 2):,}**\n"

                msg += f"\n*Your total profit is **{int(total_profit):,}** shekels*"

                return await inter.edit_original_message(content=msg.replace(',', ' '))


def setup(client):
    client.add_cog(Trading(client))
