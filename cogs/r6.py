import requests, pyrebase, asyncio, yaml, json
from discord.ext import commands, tasks
from bs4 import BeautifulSoup

# Config Load
config = yaml.safe_load(open("config.yml"))
cl = config.get('console_logging')
error_channel_id = config.get('error_channel_id')
r6s_role_id = config.get('r6s_role_id')
diagnostics_role_id = config.get('diagnostics_role_id')
r6_stats_loop = config.get('r6_stats_loop')
R6STATS_API_KEY = config.get('R6STATS_API_KEY')

# Firebase #
fb = json.loads(config.get('firebase'))
firebase = pyrebase.initialize_app(fb)
db = firebase.database()


# Commands #
class R6Stats(commands.Cog):
    def __init__(self, client):
        """Rainbow Six Siege stats commands.

        Goes to r6.tracker.network where it converts UBI ID to UBI Username;
        Using r6stats.com API gathers all the useful data
        & stores them in the Firebase Database
        """
        self.client = client
        if r6_stats_loop: self.dbr6_v2.start()

    @tasks.loop(hours=3)
    async def dbr6_v2(self):
        if cl: print('START dbr6V2 loop ', end="")

        # Get all user Ubi IDs & Discord usernames
        users = db.child('R6S').child('IDs').get()

        # Get Siege stats from every Ubi ID stored in 'users' variable and store it in the database
        for u in users.each():
            if (ubi_id := u.val().get('ubiID')) is not None:
                print(ubi_id)
                discord_username = u.val().get('discordUsername')
                data = rainbow6stats_v2(ubi_id, discord_username)
                db.child('R6S').child('stats').child(ubi_id).update(data)
                print(ubi_id)

        if cl: print("END")

    @commands.command(aliases=['su'])
    @commands.has_role(diagnostics_role_id)
    async def stats_update(self, ctx):
        if cl: print('START stats_update ', end="")
        # Since the 'dbr6V2' loop runs only every hour if there is a need
        # to manually update the stats this is the only way
        # Well the only way other than restarting the bot..
        self.dbr6_v2.cancel()
        # This 0.5s delay needs to be here because who the fuck knows why
        await asyncio.sleep(0.5)
        self.dbr6_v2.start()
        await ctx.message.add_reaction('✅')
        if cl: print("END")

    @commands.command()
    @commands.has_role(r6s_role_id)
    async def r6set(self, ctx, link: str):
        if cl: print('START r6set ', end="")
        user_id = ctx.author.id
        try:
            # Remove the hyperlink part of the message if necessary
            if link.startswith("https://r6.tracker.network/profile/id/"):
                link = link.replace('https://r6.tracker.network/profile/id/', '')

            # Set up the Ubi ID under the users database entry
            data = {'ubiID': link, 'discordUsername': str(ctx.author)}
            db.child('R6S').child('IDs').child(user_id).update(data)

            # Update the stats with the new person in now
            self.dbr6_v2.cancel()
            # This 0.5s delay needs to be here because who the fuck knows why
            await asyncio.sleep(0.5)
            self.dbr6_v2.start()

            await ctx.message.add_reaction('✅')

        except Exception as e:
            await ctx.message.add_reaction('❌')
            await ctx.send("Something went wrong")
            err_ch = self.client.get_channel(error_channel_id)
            await err_ch.send(f'**r6set:**\nlink: {link}\nuid: {user_id}\ncould not set link\n`{e}`')
        if cl: print("END")


def setup(client):
    client.add_cog(R6Stats(client))


# Functions #
def rainbow6stats_v2(ubi_id, discord_username):
    genericStats, seasonalStats = fetch_api_data(ubi_id)

    # (Hopefully) get the current season
    # Should always be the first so this should work
    cs = list(seasonalStats['seasons'].keys())[0]

    stats = {}
    stats['discordUsername'] = discordUsername

    stats['level'] = genericStats['progression']['level']
    stats['xp'] = genericStats['progression']['total_xp']
    stats['totalMatches'] = genericStats['stats']['general']['games_played']
    stats['totalPlaytime'] = genericStats['stats']['general']['playtime']
    stats['totalSuicides'] = genericStats['stats']['general']['suicides']
    stats['totalMeleeKills'] = genericStats['stats']['general']['melee_kills']
    stats['totalKills'] = genericStats['stats']['general']['kills']
    stats['totalDeaths'] = genericStats['stats']['general']['deaths']
    stats['totalAssists'] = genericStats['stats']['general']['assists']
    stats['totalDBNOs'] = genericStats['stats']['general']['dbnos']
    stats['totalHeadshots'] = genericStats['stats']['general']['headshots']
    stats['totalPenetrationKills'] = genericStats['stats']['general']['penetration_kills']
    stats['totalReinforcements'] = genericStats['stats']['general']['reinforcements_deployed']
    stats['totalGadgetsDestroyed'] = genericStats['stats']['general']['gadgets_destroyed']
    stats['hs'] = (genericStats['stats']['general']['headshots'] / genericStats['stats']['general']['kills']) * 100

    stats['rankedGames'] = genericStats['stats']['queue']['ranked']['games_played']
    stats['rankedPlaytime'] = genericStats['stats']['queue']['ranked']['playtime']
    stats['rankedKills'] = genericStats['stats']['queue']['ranked']['kills']
    stats['rankedDeaths'] = genericStats['stats']['queue']['ranked']['deaths']
    stats['rankedWins'] = genericStats['stats']['queue']['ranked']['wins']
    stats['rankedLosses'] = genericStats['stats']['queue']['ranked']['losses']

    stats['casualGames'] = genericStats['stats']['queue']['casual']['games_played']
    stats['casualPlaytime'] = genericStats['stats']['queue']['casual']['playtime']
    stats['casualKills'] = genericStats['stats']['queue']['casual']['kills']
    stats['casualDeaths'] = genericStats['stats']['queue']['casual']['deaths']
    stats['casualWins'] = genericStats['stats']['queue']['casual']['wins']
    stats['casualLosses'] = genericStats['stats']['queue']['casual']['losses']

    stats['ubisoftID'] = seasonalStats['ubisoft_id']
    stats['ubisoftUsername'] = seasonalStats['username']
    stats['platform'] = seasonalStats['platform']

    stats['seasonName'] = seasonalStats['seasons'][cs]['name']
    stats['currentRank'] = seasonalStats['seasons'][cs]['regions']['emea'][0]['rank_text']
    stats['currentMMR'] = seasonalStats['seasons'][cs]['regions']['emea'][0]['mmr']
    stats['currentRankImage'] = getRankV2(seasonalStats['seasons'][cs]['regions']['emea'][0]['rank_text'])
    stats['maxRank'] = seasonalStats['seasons'][cs]['regions']['emea'][0]['max_rank_text']
    stats['maxMMR'] = seasonalStats['seasons'][cs]['regions']['emea'][0]['max_mmr']
    stats['maxRankImage'] = getRankV2(seasonalStats['seasons'][cs]['regions']['emea'][0]['max_rank_text'])

    stats['nextRankMMR'] = seasonalStats['seasons'][cs]['regions']['emea'][0]['next_rank_mmr']
    stats['prevRankMMR'] = seasonalStats['seasons'][cs]['regions']['emea'][0]['prev_rank_mmr']

    stats['sAbandons'] = seasonalStats['seasons'][cs]['regions']['emea'][0]['abandons']
    stats['sKills'] = seasonalStats['seasons'][cs]['regions']['emea'][0]['kills']
    stats['sDeaths'] = seasonalStats['seasons'][cs]['regions']['emea'][0]['deaths']
    stats['sWins'] = seasonalStats['seasons'][cs]['regions']['emea'][0]['wins']
    stats['sLosses'] = seasonalStats['seasons'][cs]['regions']['emea'][0]['losses']

    return stats


def get_rank_v2(rank):
    # A really obscene way to do this, BUT it was easier than to use the Firebase Storage calls every time
    rank_dict = {
        "unranked": "https://firebasestorage.googleapis.com/v0/b/chuckwalla-69.appspot.com/o/R6%20Ranks%2FUnranked.png?alt=media&token=295b2528-9813-4add-a46f-9e5c7e2a13c8",
        "copper v": "https://firebasestorage.googleapis.com/v0/b/chuckwalla-69.appspot.com/o/R6%20Ranks%2FCopper_05.png?alt=media&token=34112e43-01cd-496a-83ca-a6d2008b1c70",
        "copper iv": "https://firebasestorage.googleapis.com/v0/b/chuckwalla-69.appspot.com/o/R6%20Ranks%2FCopper_04.png?alt=media&token=4e1351b3-25bc-4176-a7a0-f513626be2d7",
        "copper iii": "https://firebasestorage.googleapis.com/v0/b/chuckwalla-69.appspot.com/o/R6%20Ranks%2FCopper_03.png?alt=media&token=b6e0acf8-98d0-4acf-b991-e660ec57be36",
        "copper ii": "https://firebasestorage.googleapis.com/v0/b/chuckwalla-69.appspot.com/o/R6%20Ranks%2FCopper_02.png?alt=media&token=85f9e162-5a17-45ff-bac4-b7ceb08391ff",
        "copper i": "https://firebasestorage.googleapis.com/v0/b/chuckwalla-69.appspot.com/o/R6%20Ranks%2FCopper_01.png?alt=media&token=f7bdf9c6-a82d-4ca4-a12c-b73dc1a68cd5",
        "bronze v": "https://firebasestorage.googleapis.com/v0/b/chuckwalla-69.appspot.com/o/R6%20Ranks%2FBronze_05.png?alt=media&token=46f3b6d7-22ad-478d-841f-af659a254b6e",
        "bronze iv": "https://firebasestorage.googleapis.com/v0/b/chuckwalla-69.appspot.com/o/R6%20Ranks%2FBronze_04.png?alt=media&token=ccb5e10e-4941-469d-8b2b-2c5b0d1d58bd",
        "bronze iii": "https://firebasestorage.googleapis.com/v0/b/chuckwalla-69.appspot.com/o/R6%20Ranks%2FBronze_03.png?alt=media&token=fa0aa632-b533-44d7-aefc-57a5a1aad708",
        "bronze ii": "https://firebasestorage.googleapis.com/v0/b/chuckwalla-69.appspot.com/o/R6%20Ranks%2FBronze_02.png?alt=media&token=70f6b0c8-307a-4bfb-9f83-c1e98e9748d9",
        "bronze i": "https://firebasestorage.googleapis.com/v0/b/chuckwalla-69.appspot.com/o/R6%20Ranks%2FBronze_01.png?alt=media&token=a4ef33bb-cebe-49f9-a712-9b0e28af1a14",
        "silver v": "https://firebasestorage.googleapis.com/v0/b/chuckwalla-69.appspot.com/o/R6%20Ranks%2FSilver_05.png?alt=media&token=85011248-cf4e-4799-bee9-eb758375de7c",
        "silver iv": "https://firebasestorage.googleapis.com/v0/b/chuckwalla-69.appspot.com/o/R6%20Ranks%2FSilver_04.png?alt=media&token=454fe077-5a6e-4c9f-887e-c789265374a9",
        "silver iii": "https://firebasestorage.googleapis.com/v0/b/chuckwalla-69.appspot.com/o/R6%20Ranks%2FSilver_03.png?alt=media&token=9e50ead1-cf08-4f55-a99c-da9160f8f171",
        "silver ii": "https://firebasestorage.googleapis.com/v0/b/chuckwalla-69.appspot.com/o/R6%20Ranks%2FSilver_02.png?alt=media&token=8fd1e6df-67a1-4abd-820a-b5da03cc2e23",
        "silver i": "https://firebasestorage.googleapis.com/v0/b/chuckwalla-69.appspot.com/o/R6%20Ranks%2FSilver_01.png?alt=media&token=4331a891-e150-4b18-b940-50667ec27185",
        "gold iv": "https://firebasestorage.googleapis.com/v0/b/chuckwalla-69.appspot.com/o/R6%20Ranks%2FGOLD_04.png?alt=media&token=bae67b53-35f3-4f81-a019-a7a69fe82f67",
        "gold iii": "https://firebasestorage.googleapis.com/v0/b/chuckwalla-69.appspot.com/o/R6%20Ranks%2FGOLD_03.png?alt=media&token=9a489888-23ac-4290-97fc-59276dc34044",
        "gold ii": "https://firebasestorage.googleapis.com/v0/b/chuckwalla-69.appspot.com/o/R6%20Ranks%2FGOLD_02.png?alt=media&token=615b0a9f-39c6-4db2-a97e-13fa5b0bf8c1",
        "gold i": "https://firebasestorage.googleapis.com/v0/b/chuckwalla-69.appspot.com/o/R6%20Ranks%2FGOLD_01.png?alt=media&token=3661b9e6-99d8-4742-a913-9788ac94c810",
        "platinum iii": "https://firebasestorage.googleapis.com/v0/b/chuckwalla-69.appspot.com/o/R6%20Ranks%2FPlatinum_03.png?alt=media&token=e5944dea-8df2-4b33-a6e7-b07800bd870b",
        "platinum ii": "https://firebasestorage.googleapis.com/v0/b/chuckwalla-69.appspot.com/o/R6%20Ranks%2FPlatinum_02.png?alt=media&token=9a09a0f4-2d66-4092-8e26-3d4528c315a4",
        "platinum i": "https://firebasestorage.googleapis.com/v0/b/chuckwalla-69.appspot.com/o/R6%20Ranks%2FPlatinum_01.png?alt=media&token=00086d17-f099-4c00-a2e8-530392d70ce9",
        "diamond": "https://firebasestorage.googleapis.com/v0/b/chuckwalla-69.appspot.com/o/R6%20Ranks%2FDiamond_01.png?alt=media&token=b64afb2e-4739-4d07-b0d5-41fb74a22b21",
        "champion": "https://firebasestorage.googleapis.com/v0/b/chuckwalla-69.appspot.com/o/R6%20Ranks%2FChampions_01.png?alt=media&token=aefcce88-98cf-48e3-ac76-7acfa2af30c4"
    }
    return rank_dict.get(rank.lower())


def ubi_id_to_name(ubi_id):
    response = requests.get(f"https://r6.tracker.network/profile/id/{ubi_id}")
    soup = BeautifulSoup(response.content, 'html.parser')
    name = soup.find("h1", {"class", "trn-profile-header__name"})
    return name.find("span").get_text()


def fetch_api_data(ubi_id):
    """
    auth header: 'Authorization: Bearer API_KEY_HERE'

    stats endpoint: https://api2.r6stats.com/public-api/stats/<username>/<platform>/<type>
    <username> = username
    <platform> = pc / xbox? / psn?
    <type> = generic / seasonal / operators / weapon-categories / weapons

    leaderboard endpoint: https://api2.r6stats.com/public-api/leaderboard/<platform>/<region>
    <platform> = pc / xbox? / psn?
    <region> = ncsa / emea / apac / all (defaults to 'all')
    """
    ubi_username = ubi_id_to_name(ubi_id)
    headers = {"Authorization": f"Bearer {R6STATS_API_KEY}"}

    generic_end = f"https://api2.r6stats.com/public-api/stats/{ubi_username}/pc/generic"
    generic_req = requests.get(generic_end, headers=headers)
    generic_stats = generic_req.json()
    seasonalEnd = f"https://api2.r6stats.com/public-api/stats/{ubi_username}/pc/seasonal"
    seasonalREQ = requests.get(seasonalEnd, headers=headers)
    seasonalStats = seasonalREQ.json()

    return generic_stats, seasonalStats
