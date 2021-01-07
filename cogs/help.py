from discord.ext import commands
import discord, yaml

################################################################ Config Load ##
config = yaml.safe_load(open("config.yml"))
cl = config.get('console_logging')
fudge_supreme_role_id = config.get('fudge_supreme_role_id')
lord_farquaad_role_id = config.get('lord_farquaad_role_id')
diagnostics_role_id = config.get('diagnostics_role_id')
r6s_role_id = config.get('r6s_role_id')

################################################################## Functions ##
def role(ctx, role_check):
    roles = ctx.author.roles
    for role in roles:
        if role.id == role_check:
            return True
    return False

################################################################### Commands ##
class HelpCommand(commands.Cog):
    def __init__(self, client):
        """Help."""
        self.client = client

    @commands.command(aliases=['h'])
    async def help(self, ctx):
        print('START help ', end="")
        prfx = ctx.prefix

        embed = discord.Embed(colour=discord.Colour(0xff6d10))
        embed.set_author(name=f'Help command for {ctx.author.name}')

        #######################################################################
        # r6.py
        msg = ''
        msg += f'\n`{prfx}r6set [ubi id]` - Ubi ID or r6.tracker.netrwork permanent link'

        if role(ctx, diagnostics_role_id):
            msg += f'\n`{prfx}stats_update`* - Manually update R6S stats'

        embed.add_field(name='→ **Rainbow Six: Siege**', value=msg, inline=False)
        # r6.py
        #######################################################################

        #######################################################################
        # random_stuff.py
        msg = ''
        msg += f'`{prfx}vanish` - You\'ll disappear. Magic.'
        msg += f'\n`{prfx}ping` - Show bots ping.'
        msg += f'\n`{prfx}sheriff <emote>` - Sends emote sheriff. <emote> can be emote or emote name'
        msg += f'\n`{prfx}coinflip <A> <B>` - Flips a coin. A: `{prfx}coin` / `{prfx}flip`'
        msg += f'\n`{prfx}flipflop` - Pro debílky'
        msg += f'\n`{prfx}emoji_square <emoji> <size>` - Square of emojis. A: `{prfx}es`'
        msg += f'\n`{prfx}cicina` - Can be used once per day.'

        if role(ctx, diagnostics_role_id):
            msg += f'\n`{prfx}clear <amount=1>`* - Clears `amount` of messages.'

        if role(ctx, fudge_supreme_role_id):
            msg += f'\n`{prfx}backup_db`* - Backs up the DB into DMs. A: `{prfx}bdb`'
            msg += f'\n`{prfx}manually_add_to_db`* - Backs up the DB into DMs'

        embed.add_field(name='→ **Random commands**', value=msg, inline=False)
        # random_stuff.py
        #######################################################################

        #######################################################################
        # status.py
        if role(ctx, diagnostics_role_id):
            msg = ''
            msg += f'\n`{prfx}status <activity> [message]` - `<activity>` as "clear" to clear status'

            embed.add_field(name='→ **Status**', value=msg, inline=False)
        # status.py
        #######################################################################
        # msg += f'\n`{prfx}` - '

        embed.set_footer(text="[arg] - required | <arg> - optional | A - Alias(es) | * - Role specific")
        await ctx.send(embed=embed)
        print("END")

def setup(client):
    client.add_cog(HelpCommand(client))
