from func.firebase_init import db
from func.levels import xp_from_level, level_from_xp, rank_name
from func.voice import (get_today_tz, get_yesterday_tz, get_curr_year_tz,
                        get_yearly_user_data, get_stay_time, get_yearly_total,
                        get_yearly_lvs, get_user_total, get_day_time)

from disnake.ext import commands
from disnake.utils import get

import yaml
import time
import datetime
from pytz import timezone


# Config Load
config = yaml.safe_load(open("config.yml"))
voice_log_channel_id = config.get("voice_log_channel_id")
local_timezone = config.get("local_timezone")


class OnVoiceStateUpdate(commands.Cog):
    def __init__(self, client):
        """Generates and stores voice usage statistics."""
        self.client = client

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
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

        # voice-log channel logging

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
        widget_voice_state = {
            "voice": {
                "deaf": after.deaf,
                "mute": after.mute,
                "self_mute": after.self_mute,
                "self_deaf": after.self_deaf,
                "self_stream": after.self_stream,
                "self_video": after.self_video
            }
        }
        if after.channel is None:
            widget_voice_state = {"voice": "none"}
        db.child("widget").child(uid).update(widget_voice_state)

        #######################################################################

        #######################################################################

        # Joined voice
        if before.channel is None:
            # Set the channel session timestamp
            db.child("voice").child(curr_year).child("in").child(uid).set(now)

        #######################################################################

        # Left voice
        elif after.channel is None:
            # User data
            ud = db.child("users").child(uid).get().val()
            current_level = ud.get("level", 0)
            current_xp = ud.get("xp", 0)
            current_attt = ud.get("all_time_total_voice", 0)
            current_money = ud.get("money", 0)

            # Yearly User Data
            year_voice, year_lvs = get_yearly_user_data(curr_year, uid)

            # Server Totals Data
            st = db.child("serverTotals").get().val()
            st_levels = st.get("levels", 0)
            st_voice = st.get("voice", 0)
            st_xp = st.get("xp", 0)

            # Hardcore calculations
            stayed = get_stay_time(curr_year, uid, now)  # how long did the user stay
            new_yearly_user_total = get_yearly_total(stayed, year_voice)  # their yearly new total time
            new_yearly_lvs = get_yearly_lvs(stayed, year_lvs)  # Longest Voice Session
            new_user_total = get_user_total(current_attt, stayed)  # users all time total voice time
            new_current_day_total_time, new_yesterday_total_time = get_day_time(curr_year, today, yesterday, stayed, now)  # current day and yesterday total time

            user_year_total_data = {
                "name": str(member),
                "voice": new_yearly_user_total,
                "lvs": new_yearly_lvs
            }
            today_day_data = {
                today: new_current_day_total_time,
                yesterday: new_yesterday_total_time
            }

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

                user_data = {
                    "all_time_total_voice": new_user_total,
                    f"voice_year_{curr_year}": new_yearly_user_total,
                    "level": new_level,
                    "xp": new_xp,
                    "money": current_money + xp_to_add,
                }
                server_totals_data = {
                    "levels": st_levels + (new_level - current_level),
                    "voice": st_voice + stayed,
                    "xp": st_xp + xp_to_add
                }

            else:
                user_data = {
                    "all_time_total_voice": new_user_total,
                    f"voice_year_{curr_year}": new_yearly_user_total,
                    "xp": new_xp,
                    "money": current_money + xp_to_add,
                }
                server_totals_data = {
                    "voice": st_voice + stayed,
                    "xp": st_xp + xp_to_add
                }

            # Update all the gathered data in the database
            db.child("voice").child(curr_year).child("total").child(uid).update(user_year_total_data)
            db.child("voice").child(curr_year).child("day").update(today_day_data)
            db.child("users").child(uid).update(user_data)
            db.child("serverTotals").update(server_totals_data)


def setup(client):
    client.add_cog(OnVoiceStateUpdate(client))
