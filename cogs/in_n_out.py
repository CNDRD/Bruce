from func.firebase_init import db
from func.levels import rank_name
from func.stuff import ordinal

from disnake.utils import get
from disnake.ext import commands

from humanfriendly import format_timespan
from datetime import datetime
import yaml

# Config Load
config = yaml.safe_load(open('config.yml'))
in_n_out_channel_id = config.get('in_n_out_channel_id')
test_account_uid = config.get('test_account_uid')
garrow_emoji = config.get('garrow_emoji')
yarrow_emoji = config.get('yarrow_emoji')
rarrow_emoji = config.get('rarrow_emoji')


class InNOut(commands.Cog):
    def __init__(self, client):
        """Not so simple 'in & out' events."""
        self.client = client

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Do not harrass the in-n-out channel with test account
        if member.id == test_account_uid:
            return

        # No welcome messages for bots
        # and autorole for them too, so they have color
        if member.bot:
            return await member.add_roles(get(member.guild.roles, name='Hosts'))

        users_count = db.child('serverTotals').child('users').get().val()
        db.child('serverTotals').child('users').set(users_count + 1)

        # Basic-ass variables
        ino = self.client.get_channel(in_n_out_channel_id)
        leaves = db.child('users').child(member.id).child('leaves_count').get().val() or 0

        # Get arrows emoji
        garrow = self.client.get_emoji(garrow_emoji)
        yarrow = self.client.get_emoji(yarrow_emoji)

        if leaves > 0:
            # The user has joined the server before at least once
            msg = f"{yarrow} **{member.mention}** has just ***joined*** for the {ordinal(leaves)} time!"

            # Give the user his XP role & main user role
            lvl = db.child('users').child(member.id).child('level').get().val()
            rank = rank_name(lvl)
            role = get(member.guild.roles, name=rank)
            await member.add_roles(role)
            jeetard = get(member.guild.roles, name='Jeetard')
            await member.add_roles(jeetard)

            # Update users individual stats
            data = {'in_server': True}
            db.child('users').child(member.id).update(data)

        else:
            # First join ever
            msg = f"{garrow} **{member.mention}** has just ***joined!***"

            # Give the user the 0-level role
            role = get(member.guild.roles, name=rank_name(0))
            await member.add_roles(role)

            # Get timestamps to when the user joined Discord and the server, and a link to their avatar
            joined_server = int(member.joined_at.timestamp())
            joined_discord = int(member.created_at.timestamp())
            avatar_url = str(member.avatar_url_as(size=4096))

            # Create users individual stats
            d = {'reacc_points': 0,
                 'username': str(member),
                 'xp': 0,
                 'level': 0,
                 'last_xp_get': joined_server,
                 'messages_count': 0,
                 'joined_server': joined_server,
                 'joined_disnake': joined_discord,
                 'avatar_url': avatar_url,
                 'in_server': True,
                 'money': 0,
                 }
            db.child('users').child(member.id).set(d)

        await ino.send(msg)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        # Do not harrass the in-n-out channel with test account
        if member.id == test_account_uid:
            return
            
        # No welcome messages for bots
        if member.bot:
            return

        users_count = db.child('serverTotals').child('users').get().val()
        db.child('serverTotals').child('users').set(users_count - 1)

        # Get arrow emoji
        rarrow = self.client.get_emoji(rarrow_emoji)

        leaves = db.child('users').child(member.id).child('leaves_count').get().val() or 0
        if leaves >= 1:
            count = leaves
        else:
            count = 1

        # Update users individual stats
        data = {'leaves_count': count + 1, 'in_server': False}
        db.child('users').child(member.id).update(data)

        # Basic-ass variables
        ino = self.client.get_channel(in_n_out_channel_id)
        joined = member.joined_at.replace(tzinfo=None)
        left = datetime.utcnow()

        diff = (left - joined)
        stayed = format_timespan(int(diff.total_seconds()))

        username = db.child('users').child(member.id).child('username').get().val()

        msg = None

        bans = await member.guild.bans()
        for banned in bans:
            if banned.user.id == member.id:
                msg = f"{rarrow} **{username}** has just been banned! (Reason: {banned.reason})"

        if not msg:
            if count == 1:
                msg = f"{rarrow} **{username}** has just ***left*** us! Was here for *{stayed}*."
            else:
                msg = f"{rarrow} **{username}** has just ***left*** us for the {ordinal(leaves)} time! Was here for *{stayed}*."

        clown = await ino.send(msg)

        # Automatically adds 🤡 emoji to every leave message
        # if they left within 15 minutes of joining it also adds another clown emoji
        await clown.add_reaction('🤡')
        if int(diff.total_seconds()) < 900:
            e = get(self.client.emojis, name="HonkHonk")
            await clown.add_reaction(e)


def setup(client):
    client.add_cog(InNOut(client))
