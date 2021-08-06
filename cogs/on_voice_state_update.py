from func.firebase_init import db
from func.levels import *
from func.voice import *

import pyrebase, yaml, json, discord, time, datetime, os
from discord.ext import commands
from discord.utils import get
from numerize import numerize
from pytz import timezone

from dotenv import load_dotenv
load_dotenv()

## Config Load ##
config = yaml.safe_load(open('config.yml'))
voice_log_channel_id = config.get('voice_log_channel_id')


class OnVoiceStateUpdate(commands.Cog):
    def __init__(self, client):
        """
        Generate and store voice usage statistics.
        Connected to Firebase to store the data.
        Stores the data in seconds.
        """
        self.client = client


    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # We ain't counting time for bots
        if member.bot:
            return

        # Basic-ass variables
        now = int(time.time())                                                          # NOW INT
        nowR = datetime.datetime.now(timezone('Europe/Prague')).strftime('%H:%M:%S')    # NOW READABLE STRING
        uid = member.id                                                                 # DISCORD USER ID
        username = str(member)                                                          # DISCORD USER NAME
        today = get_today_tz()                                                          # TODAY'S DATE STRING
        yesterday = get_yesterday_tz()                                                  # YESTERDAY'S DATE STRING
        currYear = get_curr_year_tz()                                                   # CURRENT YEAR
        levelUp = False                                                                 # LEVEL UP BOOL
        ch = self.client.get_channel(voice_log_channel_id)                              # VOICE LOGGING CHANNEL

        #voice-log channel logging

        # Switched channels
        if before.channel is not None and after.channel is not None and before.channel != after.channel:
            msg = f"{username} switched from **{str(before.channel)}** to **{str(after.channel)}** *{nowR}*"
            await ch.send(msg)

        # Joined voice
        elif before.channel is None:
            msg = f"{username} joined **{str(after.channel)}** *{nowR}*"
            await ch.send(msg)

        # Left voice
        elif after.channel is None:
            msg = f"{username} left **{str(before.channel)}** *{nowR}*"
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
            widget_voice_state = {"voice":"none"}
        db.child("widget").child(uid).update(widget_voice_state)

        #######################################################################

        #######################################################################

        # Joined voice
        if before.channel is None:
            # Set the channel session timestamp
            db.child('voice').child(currYear).child('in').child(uid).set(now)

        #######################################################################

        # Left voice
        elif after.channel is None:
        #########################
        ## Data gathering part ##
        #########################
            # User data
            ud = db.child('users').child(uid).get().val()
            currentLevel = ud.get('level', 0)
            currentXP = ud.get('xp', 0)
            currentATTT = ud.get('all_time_total_voice', 0)
            currentMoney = ud.get('money', 0)

            # Yearly User Data
            yearVoice, yearLVS = get_yearly_user_data(currYear, uid)

            # Server Totals Data
            st = db.child('serverTotals').get().val()
            stLevels = st.get('levels', 0)
            stVoice = st.get('voice', 0)
            stXP = st.get('xp', 0)

            # Hardcore calculations
            stayed = get_stay_time(currYear, uid, now)  # how long did the user stay
            newYearlyUserTotal = get_yearly_total(stayed, yearVoice)  # their yearly new total time
            newYearlyLVS = get_yearly_lvs(stayed, yearLVS)  # Longest Voice Session
            newUserTotal = get_user_total(currentATTT, stayed) # users all time total voice time
            newCurrentDayTotalTime, newYesterdayTotalTime = get_day_time(currYear, today, yesterday, stayed, now)  # current day and yesterday total time

            userYearTotalData = {
                'name': str(member),
                'voice': newYearlyUserTotal,
                'lvs': newYearlyLVS
            }
            todayDayData = {
                today: newCurrentDayTotalTime,
                yesterday: newYesterdayTotalTime
            }

        #############
        ## XP part ##
        #############
            # hardcore calculations
            xpToAdd = int(stayed/7)
            newXP = currentXP + xpToAdd

            if newXP >= xp_from_level(currentLevel + 1):
                levelUp = True
                new_level = level_from_xp(newXP)

                rankToAdd = rank_name(new_level)
                rankToDel = rank_name(currentLevel)
                if rankToAdd != rankToDel:
                    addRank = get(member.guild.roles, name=rankToAdd)
                    await member.add_roles(addRank)
                    delRank = get(member.guild.roles, name=rankToDel)
                    await member.remove_roles(delRank)

                userData = {
                    'all_time_total_voice':newUserTotal,
                    f'voice_year_{currYear}':newYearlyUserTotal,
                    'level':new_level,
                    'xp':newXP,
                    'money': currentMoney + xpToAdd,
                }
                serverTotalsData = {
                    'levels':stLevels + (new_level - currentLevel),
                    'voice':stVoice + stayed,
                    'xp':stXP + xpToAdd
                }

            else:
                userData = {
                    'all_time_total_voice':newUserTotal,
                    f'voice_year_{currYear}':newYearlyUserTotal,
                    'xp':newXP,
                    'money': currentMoney + xpToAdd,
                }
                serverTotalsData = {
                    'voice': stVoice + stayed,
                    'xp': stXP + xpToAdd
                }

        ######################
        ## Data update part ##
        ######################
            db.child('voice').child(currYear).child('total').child(uid).update(userYearTotalData)
            db.child('voice').child(currYear).child('day').update(todayDayData)
            db.child('users').child(uid).update(userData)
            db.child('serverTotals').update(serverTotalsData)

        ######################
        ## Level up message ##
        ######################
            if levelUp:
                dm_ch = await member.create_dm()
                embed = discord.Embed(colour=discord.Colour.random())
                embed.set_author(name=member, url='https://diskito.eu/leader.html')

                embed.add_field(name=f'You have just levelled up to {new_level}! Congrats!',
                                value=f'You now have **{numerize.numerize(newXP)}** xp',
                                inline=False)
                await dm_ch.send(embed=embed)



def setup(client):
    client.add_cog(OnVoiceStateUpdate(client))
