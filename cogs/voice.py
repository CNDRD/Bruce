import pyrebase, discord, time, yaml, json, datetime
from discord.ext import commands, tasks
from discord.utils import get
from numerize import numerize
from pytz import timezone

################################################################ Config Load ##
config = yaml.safe_load(open("config.yml"))
cl = config.get('console_logging')
voice_log_channel_id = config.get('voicelog_channel_id')

################################################################### Firebase ##
fb = json.loads(config.get('firebase'))
firebase = pyrebase.initialize_app(fb)
db = firebase.database()

################################################################### Commands ##
class VoiceMove(commands.Cog):
    def __init__(self, client):
        """Generate and store voice usage statistics.

        Is connected to Firebase to store the data.
        Stores the data in seconds.
        """
        self.client = client
        self.set_voice_day_status.start()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if cl: print('START on_voice_state_update ', end="")

        # We ain't counting time for bots
        if member.bot:
            return

        # Basic-ass variables
        now = int(time.time()  )                            # NOW INT
        nowR = time.strftime("%x %X", time.gmtime(now))     # NOW READABLE STRING
        uid = member.id                                     # DISCORD USER ID
        username = str(member)                              # DISCORD USER NAME
        today = get_today_tz()                              # TODAY'S DATE STRING
        currYear = get_curr_year_tz()                       # CURRENT YEAR
        levelUp = False                                     # LEVEL UP BOOL
        ch = self.client.get_channel(voice_log_channel_id)  # VOICE LOGGING CHANNEL

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
            currentLevel = ud.get('level')
            currentXP = ud.get('xp')
            currentATTT = ud.get('all_time_total_voice')

            # Yearly User Data
            yearVoice, yearLVS = get_yearly_user_data(currYear, uid)

            # Server Totals Data
            st = db.child('serverTotals').get().val()
            stLevels = st.get('levels')
            stVoice = st.get('voice')
            stXP = st.get('xp')

            # hardcore calculations
            stayed = get_stay_time(currYear, uid, now)  # how long did the user stay
            newYearlyUserTotal = get_yearly_total(stayed, yearVoice)  # their yearly new total time
            newYearlyLVS = get_yearly_lvs(stayed, yearLVS)  # Longest Voice Session
            newCurrentDayTotalTime = get_current_day_time(currYear, today, stayed)  # current day total time
            newUserTotal = get_user_total(currentATTT, stayed) # users all time total voice time

            userYearTotalData = {
                'name': str(member),
                'voice': newYearlyUserTotal,
                'lvs': newYearlyLVS
            }
            newDayData = {
                today: newCurrentDayTotalTime
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
                    'xp':newXP
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
                    'xp':newXP
                }
                serverTotalsData = {
                    'voice': stVoice + stayed,
                    'xp': stXP + xpToAdd
                }

        ######################
        ## Data update part ##
        ######################
            db.child('voice').child(currYear).child('total').child(uid).update(userYearTotalData)
            db.child('voice').child(currYear).child('day').update(newDayData)
            db.child('users').child(uid).update(userData)
            db.child('serverTotals').update(serverTotalsData)

        ######################
        ## Level up message ##
        ######################
            if levelUp:
                dm_ch = await member.create_dm()
                embed = discord.Embed(colour=discord.Colour(0x0be881))
                embed.set_author(name=member, url='https://chuckwalla-69.web.app/leader.html')

                embed.add_field(name=f'You have just levelled up to {new_level}! Congrats!',
                                value=f'You now have **{numerize.numerize(newXP)}** xp',
                                inline=False)
                await dm_ch.send(embed=embed)

        if cl: print("END")


    @tasks.loop(hours=5)
    async def set_voice_day_status(self):
        if cl: print('START setVoiceDayStatus loop ', end="")
        # This exists so there is the current day in the database regardless of any voice time being recorded
        # Basically so just the graphs on the web make sense
        # Could be done on the actual website but this was easier
        today = get_today_tz()            # TODAY'S DATE STRING
        currYear = get_curr_year_tz()      # CURRENT YEAR

        # Check if today's entry exists
        # If it doesn't create it, else fuck off
        today_data = db.child('voice').child(currYear).child('day').child(today).get().val()
        if today_data is None:
            db.child('voice').child(currYear).child('day').child(today).set(0)
        if cl: print("END")

def setup(client):
    client.add_cog(VoiceMove(client))


################################################################## Functions ##
def level_from_xp(xp):
    for i in range(0,100):
        if xp_from_level(i) <= xp < xp_from_level(i + 1):
            return i

def xp_from_level(level):
    return int(5 / 6 * level * (2 * level * level + 27 * level + 91))
    # https://github.com/PsKramer/mee6calc/blob/master/calc.js

def rank_name(num):
    a = (num - (num%5))
    if num == 0:
        return '[0]'
    return f"[{a}-{a+5}]"
    # https://stackoverflow.com/a/13082705

def add_spaces(numero):
    numero = ''.join(reversed(str(numero)))
    a = [numero[i:i+3] for i in range(0, len(numero), 3)]
    a = ' '.join([numero[i:i+3] for i in range(0, len(numero), 3)])
    a = ''.join(reversed(str(a)))
    return a
    # https://stackoverflow.com/a/15254225/13186339

def get_stay_time(curr_year, uid, now):
    # Get the time user joined at, delete it, calculate how long they stayed for
    joinedAt = db.child('voice').child(curr_year).child('in').child(uid).get().val()
    db.child('voice').child(curr_year).child('in').child(uid).remove()
    return now - joinedAt

def get_yearly_total(stayed, tv):
    if tv is None: tv = 0
    return stayed + tv

def get_yearly_lvs(stayed, current_lvs):
    if current_lvs is None: current_lvs = 0
    if stayed > current_lvs: return stayed
    return current_lvs

def get_current_day_time(curr_year, today, stayed):
    cdt = db.child('voice').child(curr_year).child('day').child(today).get().val()
    if cdt is None: cdt = 0
    return cdt + stayed

def get_user_total(atvs, stayed):
    if atvs is None: atvs = 0
    return atvs + stayed

def get_today_tz():
    # Timezone-aware date string
    return datetime.datetime.now(timezone('Europe/Prague')).strftime('%Y-%m-%d')

def get_curr_year_tz():
    # Timezone-aware date year
    return datetime.datetime.now(timezone('Europe/Prague')).year

def get_yearly_user_data(curr_year, uid):
    yud = db.child('voice').child(curr_year).child('total').child(uid).get().val()
    if yud is None:
        yearVoice = 0
        yearLVS = 0
    else:
        yearVoice = yud.get('voice')
        yearLVS = yud.get('lvs')

    return yearVoice, yearLVS
