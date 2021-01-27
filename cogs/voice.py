import pyrebase, operator, discord, time, yaml, json, datetime
from discord.ext import commands, tasks
from discord.utils import get
from numerize import numerize
from pytz import timezone

################################################################ Config Load ##
config = yaml.safe_load(open("config.yml"))
cl = config.get('console_logging')
voicelog_channel_id = config.get('voicelog_channel_id')

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
        self.setVoiceDayStatus.start()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if cl: print('START on_voice_state_update ', end="")

        # We ain't counting time for bots
        if member.bot:
            return

        # Basic-ass variables
        now = int(time.time())                              # NOW INT
        uid = member.id                                     # DISCORD USER ID
        username = str(member)                              # DISCORD USER NAME
        today = getTodayTZ()                                # TODAY'S DATE STRING
        currYear = getCurrYearTZ()                          # CURRENT YEAR
        levelUp = False                                     # LEVEL UP BOOL
        ch = self.client.get_channel(voicelog_channel_id)   # VOICE LOGGING CHANNEL

        #voice-log channel logging
        #######################################################################

        # Switched channels
        if before.channel is not None and after.channel is not None and before.channel != after.channel:
            msg = f"{username} switched from **{str(before.channel)}** to **{str(after.channel)}**"
            await ch.send(msg)

        # Joined voice
        elif before.channel is None:
            msg = f"{username} joined **{str(after.channel)}**"
            await ch.send(msg)

        # Left voice
        elif after.channel is None:
            msg = f"{username} left **{str(before.channel)}**"
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
            yearVoice, yearLVS = getYearlyUserData(currYear, uid)

            # Server Totals Data
            st = db.child('serverTotals').get().val()
            stLevels = st.get('levels')
            stVoice = st.get('voice')
            stXP = st.get('xp')

            # hardcore calculations
            stayed = getStayTime(currYear, uid, now)  # how long did the user stay
            newYearlyUserTotal = getYearlyTotal(stayed, yearVoice)  # their yearly new total time
            newYearlyLVS = getYearlyLVS(stayed, yearLVS)  # Longest Voice Session
            newCurrentDayTotalTime = getCurrentDayTime(currYear, today, stayed)  # current day total time
            newUserTotal = getUserTotal(currentATTT, stayed) # users all time total voice time

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

            if newXP >= xpFromLevel(currentLevel+1):
                levelUp = True
                newLevel = levelFromXP(newXP)

                rankToAdd = rankName(newLevel)
                rankToDel = rankName(currentLevel)
                if rankToAdd != rankToDel:
                    addRank = get(member.guild.roles, name=rankToAdd)
                    await member.add_roles(addRank)
                    delRank = get(member.guild.roles, name=rankToDel)
                    await member.remove_roles(delRank)

                userData = {
                    'all_time_total_voice':newUserTotal,
                    f'voice_year_{currYear}':newYearlyUserTotal,
                    'level':newLevel,
                    'xp':newXP
                }
                serverTotalsData = {
                    'levels':stLevels + (newLevel - currentLevel),
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

                embed.add_field(name=f'You have just levelled up to {newLevel}! Congrats!',
                                value=f'You now have **{numerize.numerize(newXP)}** xp',
                                inline=False)
                await dm_ch.send(embed=embed)

        if cl: print("END")


    @tasks.loop(hours=5)
    async def setVoiceDayStatus(self):
        if cl: print('START setVoiceDayStatus loop ', end="")
        # This exists so there is the current day in the database regardless of any voice time being recorded
        # Basically so just the graphs on the web make sense
        # Could be done on the actual website but this was easier
        today = getTodayTZ()            # TODAY'S DATE STRING
        currYear = getCurrYearTZ()      # CURRENT YEAR

        # Check if todays entry exists
        # If it doesn't create it, else fuck off
        today_data = db.child('voice').child(currYear).child('day').child(today).get().val()
        if today_data is None:
            db.child('voice').child(currYear).child('day').child(today).set(0)
        if cl: print("END")

def setup(client):
    client.add_cog(VoiceMove(client))


################################################################## Functions ##
def levelFromXP(xp):
    for i in range(0,100):
        if xpFromLevel(i) <= xp < xpFromLevel(i+1):
            return i

def xpFromLevel(level):
    return int(5 / 6 * level * (2 * level * level + 27 * level + 91))
    # https://github.com/PsKramer/mee6calc/blob/master/calc.js

def rankName(num):
    a = (num - (num%5))
    if num == 0:
        return '[0]'
    return f"[{a}-{a+5}]"
    # https://stackoverflow.com/a/13082705

def addSpaces(numero):
    numero = ''.join(reversed(str(numero)))
    a = [numero[i:i+3] for i in range(0, len(numero), 3)]
    a = ' '.join([numero[i:i+3] for i in range(0, len(numero), 3)])
    a = ''.join(reversed(str(a)))
    return a
    # https://stackoverflow.com/a/15254225/13186339

def getStayTime(currYear, uid, now):
    # Get the time user joined at, delete it, calculate how long they stayed for
    joinedAt = db.child('voice').child(currYear).child('in').child(uid).get().val()
    db.child('voice').child(currYear).child('in').child(uid).remove()
    return now - joinedAt

def getYearlyTotal(stayed, tv):
    if tv is None: tv = 0
    return stayed + tv

def getYearlyLVS(stayed, currentLVS):
    if currentLVS is None: currentLVS = 0
    if stayed > currentLVS: return stayed
    return currentLVS

def getCurrentDayTime(currYear, today, stayed):
    cdt = db.child('voice').child(currYear).child('day').child(today).get().val()
    if cdt is None: cdt = 0
    return cdt + stayed

def getUserTotal(atvs, stayed):
    if atvs is None: atvs = 0
    return atvs + stayed

def getTodayTZ():
    # Timezone-aware date string
    return datetime.datetime.now(timezone('Europe/Prague')).strftime('%Y-%m-%d')

def getCurrYearTZ():
    # Timezone-aware date year
    return datetime.datetime.now(timezone('Europe/Prague')).year

def getYearlyUserData(currYear, uid):
    yud = db.child('voice').child(currYear).child('total').child(uid).get().val()
    if yud is None:
        yearVoice = 0
        yearLVS = 0
    else:
        yearVoice = yud.get('voice')
        yearLVS = yud.get('lvs')

    return yearVoice, yearLVS
