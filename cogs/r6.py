import requests, pyrebase, asyncio, discord, yaml, json
from discord.ext import commands, tasks
from bs4 import BeautifulSoup

################################################################ Config Load ##
config = yaml.safe_load(open("config.yml"))
cl = config.get('console_logging')
error_channel_id = config.get('error_channel_id')
r6s_role_id = config.get('r6s_role_id')
diagnostics_role_id = config.get('diagnostics_role_id')
r6_stats_loop = config.get('r6_stats_loop')

################################################################### Firebase ##
fb = json.loads(config.get('firebase'))
firebase = pyrebase.initialize_app(fb)
db = firebase.database()

################################################################## Variables ##
current_operation = db.child('current_r6_op').get().val()

################################################################### Commands ##
class R6Stats(commands.Cog):
    def __init__(self, client):
        """Rainbow Six Siege stats commands.

        Goes to r6.tracker.network & tabstats.com,
        scrapes some stats,
        and displays them in an embed.
        Loop gets the R6 stats data and sends it to the DB.
        """
        self.client = client
        if r6_stats_loop: self.dbr6.start()


    @tasks.loop(hours=1)
    async def dbr6(self):
        if cl: print('START dbr6 loop ', end="")
        # Get all user Ubi IDs and set them into a variable
        usrs = db.child('users').get()

        # Get Siege stats from every Ubi ID stored in 'usrs' variable and store it in the database
        for u in usrs.each():
            if (ubi_id := u.val().get('ubi_id')) is not None:
                inServer = u.val().get('in_server')
                discordUsername = u.val().get('username')
                data = Rainbow6Stats(ubi_id, inServer, discordUsername)
                db.child('R6').child(ubi_id).update(data)

        if cl: print("END")


    @commands.command(aliases=['su'])
    @commands.has_role(diagnostics_role_id)
    async def stats_update(self, ctx):
        if cl: print('START stats_update ', end="")
        # Since the 'dbr6' loop runs only every hour if there is a need to manually update the stats this is the only way
        # Well the only way other than restarting the bot..
        self.dbr6.cancel()
        # This 0.5s delay needs to be here because who the fuck knows why
        await asyncio.sleep(0.5)
        self.dbr6.start()
        await ctx.message.add_reaction('✅')
        if cl: print("END")


    @commands.command()
    @commands.has_role(r6s_role_id)
    async def r6set(self, ctx, link:str):
        if cl: print('START r6set ', end="")
        try:
            # Remove the hyperlink part of the message if neccesarry
            if link.startswith("https://r6.tracker.network/profile/id/"):
                link = link.replace('https://r6.tracker.network/profile/id/','')
            user_id = ctx.author.id

            # Set up the Ubi ID under the users database entry
            data = {'ubi_id':link}
            db.child('users').child(user_id).update(data)

            # Update the stats with the new person in now
            self.dbr6.cancel()
            # This 0.5s delay needs to be here because who the fuck knows why
            await asyncio.sleep(0.5)
            self.dbr6.start()

            await ctx.message.add_reaction('✅')

        except Exception as e:
            await ctx.message.add_reaction('❌')
            await ctx.send("Something went wrong")
            err_ch = self.client.get_channel(error_channel_id)
            await err_ch.send(f'**r6set:**\nlink: {link}\nuid: {user_id}\ncould not set link\n`{e}`')
        if cl: print("END")


def setup(client):
    client.add_cog(R6Stats(client))

################################################################## Functions ##
def get_rank(rank):
    # A really obscene way to do this, BUT it was easier than to use the Firebase Storage calls every time
    rank_dict = {
        "not ranked yet.": "https://firebasestorage.googleapis.com/v0/b/chuckwalla-69.appspot.com/o/R6%20Ranks%2FUnranked.png?alt=media&token=295b2528-9813-4add-a46f-9e5c7e2a13c8",
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
        "9999004": "https://firebasestorage.googleapis.com/v0/b/chuckwalla-69.appspot.com/o/R6%20Ranks%2FSilver_05.png?alt=media&token=85011248-cf4e-4799-bee9-eb758375de7c",
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

    if rank_dict.get(rank) == None:
        return rank_dict.get("not ranked yet.")
    return rank_dict.get(rank)


def Rainbow6Stats(UbisoftID, inServer, discordUsername):
    # I know it's long as fuck and probably also dumb but until
    # there is a public API i don't see any other way..
    # I also patched it a few times so it probably makes zero sense
    stats = {}
    ranked = True

    url = f"https://r6.tracker.network/profile/id/{UbisoftID}"

    try:
        response = requests.get(url)
        status_code = (response.status_code)
        if status_code != 200:
            print(f"STATUS CODE ERROR [{status_code}]")
        else:
            soup = BeautifulSoup(response.content,'html.parser')
            defstats = soup.find_all("div", {"class","trn-defstat__value"})

            '''
            for i in range(0, len(defstats)):
                print(f'{i}. {defstats[i]}')
            '''

            if defstats is None:
                return None

            # Rank Image Link
            try:
                rank = str(defstats[66]).replace('<div class="trn-defstat__value">','').replace('</div>','')
                stats['rank_link'] = get_rank(rank.lower())
                stats['ranked'] = True


                if get_rank(None) == stats['rank_link']:
                    stats['rank_link'] = get_rank(None)
                    stats['ranked'] = False
                    ranked = False


            except:
                stats['rank_link'] = get_rank(None)
                stats['ranked'] = False
                ranked = False

            # When the user haven't played in the latest season
            # the page will show the last one that he played in as 'current'
            op = soup.find_all("h2", {"class","trn-card__header-title"})
            op = op[4].get_text().replace('Operation: ','').title()

            if op != current_operation:
                stats['rank_link'] = get_rank(None)
                stats['ranked'] = False
                ranked = False

            if len(defstats) < 70:
                stats['rank_link'] = get_rank(None)
                stats['ranked'] = False
                ranked = False

            # Diskíto thingies
            stats['inServer'] = inServer
            stats['discordUsername'] = discordUsername

            # Username
            name = soup.find("h1", {"class","trn-profile-header__name"})
            stats['username'] = name.find("span").get_text()
            # Level
            stats['level'] = int(str(defstats[0]).replace('<div class="trn-defstat__value">','').replace('</div>','').replace('\n','').replace(',',''))
            # Total Matches (Ranked + Casual)
            stats['total_matches'] = int(soup.find("div", {"class","trn-card__header-subline"}).get_text().replace(' Matches','').replace(',',''))

        #### Fields
            if ranked:
                # Current MMR
                stats['mmr'] = int(defstats[68].get_text().replace(',',''))
                # S. Max MMR
                stats['s_max_mmr'] = int(defstats[69].get_text().replace(',',''))
                # S. Wins
                stats['s_wins'] = int(defstats[63].get_text().replace(',',''))
                # S. Losses
                stats['s_losses'] = int(defstats[64].get_text().replace(',',''))
                # S. Kills
                stats['s_kills'] = int(defstats[60].get_text().replace(',',''))
                # S. Deaths
                stats['s_deaths'] = int(defstats[61].get_text().replace(',',''))

                # S. K/D + S. W/L
                stats['s_kd'] = round( (stats['s_kills'] / stats['s_deaths']), 2)
                stats['s_wl'] = round( (stats['s_wins'] / (stats['s_wins'] + stats['s_losses']) )*100, 2)

                # Current Operation Name
                op_name = soup.find_all("h2", {"class","trn-card__header-title"})
                stats['operation'] = op_name[4].get_text().replace('Operation: ','').title()
                # S. Time Played
                stats['s_time_played'] = str(defstats[11]).replace('<div class="trn-defstat__value">','').replace('</div>','')
                # S. Abandons
                stats['s_abandons'] = int(defstats[65].get_text().replace(' ',''))
                # Current Rank
                stats['current_rank'] = str(defstats[66]).replace('<div class="trn-defstat__value">','').replace('</div>','')
                if stats['current_rank'] == '9999004':
                    stats['current_rank'] = 'SILVER V'

                # Headshot %
                stats['hs'] = float(str(defstats[16].get_text()).replace('\n','').replace(' ','').replace('%',''))

            else:
                # Operation Name
                op_name = soup.find("div", {"class","r6-quickseason"})
                op_name = op_name.find_all("div")
                stats['operation'] = op_name[-2].get_text().title()
                # Headshot %
                stats['hs'] = float(str(defstats[16].get_text()).replace('\n','').replace(' ','').replace('%',''))
                # Zero out some stats
                stats['current_rank'] = "Unranked"
                stats['s_time_played'] = "None"

                stats['mmr'] = stats['s_max_mmr'] = stats['s_abandons'] = 0
                stats['s_wins'] = stats['s_losses'] = 0
                stats['s_kills'] = stats['s_deaths'] = 0
                stats['s_wl'] = stats['s_kd'] = 0

            return stats

    except Exception as e:
        print(e)
        return "Error"
