from func.supabase import supabase
from func.levels import xp_from_level, level_from_xp, rank_name
from func.voice import (get_today_tz, get_yesterday_tz, get_curr_year_tz,
                        get_yearly_total, get_yearly_lvs, get_user_total, get_day_time)

from disnake.ext import commands
from disnake.utils import get
from disnake import Member, VoiceState

import time
import datetime
from pytz import timezone


voice_log_channel_id = 802111450021232640
local_timezone = 'Europe/Prague'


class OnVoiceStateUpdate(commands.Cog):
    def __init__(self, client):
        """Generates and stores voice usage statistics."""
        self.client = client

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: Member, before: VoiceState, after: VoiceState):
        # We ain't counting time for bots
        if member.bot:
            return

        # Basic-ass variables
        now = int(time.time())                                                          # NOW INT
        now_r = datetime.datetime.now(timezone(local_timezone)).strftime("%H:%M:%S")    # NOW READABLE STRING
        uid = member.id                                                                 # DISCORD USER ID
        username = str(member)                                                          # DISCORD USER NAME
        today = get_today_tz()                                                          # TODAY'S DATE STRING
        yesterday = get_yesterday_tz()                                                  # YESTERDAY'S DATE STRING
        curr_year = get_curr_year_tz()                                                  # CURRENT YEAR
        ch = self.client.get_channel(voice_log_channel_id)                              # VOICE LOGGING CHANNEL

        #######################################################################

        #######################################################################
        # Voice logging

        # Switched channels
        if before.channel is not None and after.channel is not None and before.channel != after.channel:
            msg = f"{username} switched from **{str(before.channel)}** to **{str(after.channel)}** *{now_r}*"
            await ch.send(msg)

        # Joined voice
        elif before.channel is None:
            msg = f"{username} joined **{str(after.channel)}** *{now_r}*"
            await ch.send(msg)

        # Left voice
        elif after.channel is None:
            msg = f"{username} left **{str(before.channel)}** *{now_r}*"
            await ch.send(msg)

        #######################################################################

        #######################################################################
        # Widget voice state update

        # widget_voice_state = {
        #     "voice": {
        #         "deaf": after.deaf,
        #         "mute": after.mute,
        #         "self_mute": after.self_mute,
        #         "self_deaf": after.self_deaf,
        #         "self_stream": after.self_stream,
        #         "self_video": after.self_video
        #     }
        # }
        # if after.channel is None:
        #     widget_voice_state = {"voice": "none"}
        # db.child("widget").child(uid).update(widget_voice_state)

        #######################################################################

        #######################################################################
        # Joined voice

        if before.channel is None:
            # Set the channel session timestamp
            supabase.from_('current_voice').insert({'id': uid, 'since': now, 'channel': after.channel.id}).execute()

        #######################################################################

        #######################################################################
        # Left voice

        elif after.channel is None:
            member_data = supabase.from_('users').select('level, xp, total_voice').eq('id', member.id).execute()
            current_level = member_data.data[0]['level']
            current_xp = member_data.data[0]['xp']
            current_attt = member_data.data[0]['total_voice']

            # Yearly User Data
            yearly_voice_data = supabase.from_('yearly_voice').select('total, longest').eq('id', member.id).eq('year', curr_year).execute()
            year_voice = yearly_voice_data.data[0]['total']
            year_lvs = yearly_voice_data.data[0]['longest']

            current_voice_data = supabase.from_('current_voice').select('since, channel').eq('id', member.id).execute()
            supabase.from_('current_voice').delete().eq('id', member.id).execute()

            # Hardcore calculations
            stayed = now - current_voice_data.data[0]['since']  # how long did the user stay
            new_yearly_user_total = get_yearly_total(stayed, year_voice)  # their yearly new total time
            new_yearly_lvs = get_yearly_lvs(stayed, year_lvs)  # Longest Voice Session
            new_user_total = get_user_total(current_attt, stayed)  # users all time total voice time
            new_current_day_total_time, new_yesterday_total_time = get_day_time(today, yesterday, stayed, now)  # current day and yesterday total time

            # Hardcore XP calculations
            xp_to_add = int(stayed/7)
            new_xp = current_xp + xp_to_add

            if new_xp >= xp_from_level(current_level + 1):
                new_level = level_from_xp(new_xp)

                rank_to_add = rank_name(new_level)
                rank_to_del = rank_name(current_level)
                if rank_to_add != rank_to_del:
                    add_rank = get(member.guild.roles, name=rank_to_add)
                    await member.add_roles(add_rank)
                    del_rank = get(member.guild.roles, name=rank_to_del)
                    await member.remove_roles(del_rank)

                user_data = {"total_voice": new_user_total, "level": new_level, "xp": new_xp}

            else:
                user_data = {"total_voice": new_user_total, "xp": new_xp}

            # Update all the gathered data in the database
            supabase.from_('yearly_voice').upsert({'id': member.id, 'year': curr_year, 'total': new_yearly_user_total, 'longest': new_yearly_lvs}).execute()
            daily_voice = [
                {'date': today, 'seconds': new_current_day_total_time},
                {'date': yesterday, 'seconds': new_yesterday_total_time}
            ]
            supabase.from_('daily_voice').upsert(daily_voice).execute()
            supabase.from_('users').update(user_data).eq('id', member.id).execute()


def setup(client):
    client.add_cog(OnVoiceStateUpdate(client))
