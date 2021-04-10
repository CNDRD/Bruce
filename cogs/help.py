from func.stuff import user_has_role as role
from func.console_logging import cl

from discord.ext import commands
import discord, yaml

## Config Load ##
config = yaml.safe_load(open('config.yml'))
owner_role_id = config.get('owner_role_id')
mod_role_id = config.get('mod_role_id')
bot_mod_role_id = config.get('bot_mod_role_id')
r6s_role_id = config.get('r6s_role_id')


class Help(commands.Cog):
    def __init__(self, client):
        """Halp."""
        self.client = client


    @commands.command(aliases=['h'])
    async def help(self, ctx):
        cl(ctx)
        prfx = ctx.prefix

        embed = discord.Embed(colour=discord.Colour.random())
        embed.set_author(name=f'Help command for {ctx.author.name}')

        # game_stats.py
        if role(ctx, bot_mod_role_id):
            msg = ''
            msg += f'\n`{prfx}stats_update`* - Restarts all stats loops'
            embed.add_field(name='→ **Game Stats**', value=msg, inline=False)
        # game_stats.py

        # user.py
        msg = ''
        msg += f'`{prfx}code` - Link to the GitHub repo'
        msg += f'\n`{prfx}ping` - Show bots ping.'
        msg += f'\n`{prfx}vanish` - You\'ll disappear. Magic.'
        msg += f'\n`{prfx}coinflip <A> <B>` - Flips a coin. A: `{prfx}coin` / `{prfx}flip`'
        msg += f'\n`{prfx}flipflop` - Pro debílky'
        ## technically not from 'user.py'
        msg += f'\n`{prfx}cicina` - Can be used once per day.'
        msg += f'\n`{prfx}quote` - Create a quote on https://diskito.eu/quotes'

        embed.add_field(name='→ **User**', value=msg, inline=False)
        # user.py

        # admin.py
        if role(ctx, bot_mod_role_id) or role(ctx, mod_role_id):
            msg = ''
            if role(ctx, owner_role_id):
                msg += f'\n`{prfx}backup_db`* - Backs up the DB into DMs. A: `{prfx}bdb`'
                msg += f'\n`{prfx}manually_add_to_db [@user]`* - Manually add [@user] to DB. A: `{prfx}mdb`'

            msg += f'\n`{prfx}clear <amount=1>`* - Clears `amount` of messages.'
            msg += f'\n`{prfx}add_reaction [emoji]`* - Adds `emoji` to the message this replies to. A: `{prfx}add`'
            msg += f'\n`{prfx}say [content]`* - The bot will send `content`'
            msg += f'\n`{prfx}edit [content]`* - Edits the message this replies to with `content`'

            embed.add_field(name='→ **Admin**', value=msg, inline=False)
        # admin.py

        # status.py
        if role(ctx, bot_mod_role_id):
            msg = ''
            msg += f'\n`{prfx}status <activity> [message]` - `<activity>` as "clear" to clear status'

            embed.add_field(name='→ **Status**', value=msg, inline=False)
        # status.py

        embed.set_footer(text="[arg] - required | <arg> - optional | A - Alias(es) | * - Role specific")
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Help(client))
