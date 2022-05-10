from func.firebase_init import db

import disnake
from disnake.ext import commands


class UserCommands(commands.Cog):
    def __init__(self, client):
        """User commands."""
        self.client = client

    @commands.user_command(name="User Info")
    async def user_info(self, inter: disnake.ApplicationCommandInteraction):
        u = db.child("users").child(inter.target.id).get().val()

        embed = disnake.Embed(color=inter.target.top_role.color)
        embed.set_author(name=inter.target.name)
        embed.set_thumbnail(url=inter.target.display_avatar.url)
        embed.set_footer(text=f"ID: {inter.target.id}")

        if inter.target.bot:
            embed.add_field(name="Bot", value="This is a bot account", inline=True)
        else:
            embed.add_field(name="Level", value=f"{u.get('level'):,}".replace(",", " "), inline=True)
            embed.add_field(name="Reaction Points", value=f"{u.get('reacc_points'):,}".replace(",", " "), inline=True)
            embed.add_field(name="Money", value=f"{u.get('money'):,}".replace(',', ' '), inline=True)

            embed.add_field(name="XP", value=f"{u.get('xp'):,}".replace(",", " "), inline=True)
            embed.add_field(name="Messages sent", value=f"{u.get('messages_count'):,}".replace(",", " "), inline=True)
            embed.add_field(name="Average Cicina", value=round(u.get("cicina_avg"), 2), inline=True)

            embed.add_field(name="Hours in Voice", value=round(u.get("all_time_total_voice") / 60 / 60, 2), inline=True)

        t_format = "%d %b %Y @ %H:%M:%S"
        embed.add_field(name="Joined this server:", value=inter.target.joined_at.strftime(t_format), inline=False)
        embed.add_field(name="Joined Discord:", value=inter.target.created_at.strftime(t_format), inline=False)

        await inter.response.send_message(embed=embed)


def setup(client):
    client.add_cog(UserCommands(client))
