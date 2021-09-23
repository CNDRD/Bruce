import os
from r6sapi import *
from collections import OrderedDict

from dotenv import load_dotenv
load_dotenv()

UBISOFT_EMAIL = os.getenv('UBISOFT_EMAIL')
UBISOFT_PASSW = os.getenv('UBISOFT_PASSW')

RANKS = [
    { "name": "Copper 5",   "min_mmr": 1,    "max_mmr": 1199 },
    { "name": "Copper 4",   "min_mmr": 1200, "max_mmr": 1299 },
    { "name": "Copper 3",   "min_mmr": 1300, "max_mmr": 1399 },
    { "name": "Copper 2",   "min_mmr": 1400, "max_mmr": 1499 },
    { "name": "Copper 1",   "min_mmr": 1500, "max_mmr": 1599 },
    { "name": "Bronze 5",   "min_mmr": 1600, "max_mmr": 1699 },
    { "name": "Bronze 4",   "min_mmr": 1700, "max_mmr": 1799 },
    { "name": "Bronze 3",   "min_mmr": 1800, "max_mmr": 1899 },
    { "name": "Bronze 2",   "min_mmr": 1900, "max_mmr": 1999 },
    { "name": "Bronze 1",   "min_mmr": 2000, "max_mmr": 2099 },
    { "name": "Silver 5",   "min_mmr": 2100, "max_mmr": 2199 },
    { "name": "Silver 4",   "min_mmr": 2200, "max_mmr": 2299 },
    { "name": "Silver 3",   "min_mmr": 2300, "max_mmr": 2399 },
    { "name": "Silver 2",   "min_mmr": 2400, "max_mmr": 2499 },
    { "name": "Silver 1",   "min_mmr": 2500, "max_mmr": 2599 },
    { "name": "Gold 3",     "min_mmr": 2600, "max_mmr": 2799 },
    { "name": "Gold 2",     "min_mmr": 2800, "max_mmr": 2999 },
    { "name": "Gold 1",     "min_mmr": 3000, "max_mmr": 3199 },
    { "name": "Platinum 3", "min_mmr": 3200, "max_mmr": 3499 },
    { "name": "Platinum 2", "min_mmr": 3500, "max_mmr": 3799 },
    { "name": "Platinum 1", "min_mmr": 3800, "max_mmr": 4099 },
    { "name": "Diamond 3",  "min_mmr": 4100, "max_mmr": 4399 },
    { "name": "Diamond 2",  "min_mmr": 4400, "max_mmr": 4699 },
    { "name": "Diamond 1",  "min_mmr": 4700, "max_mmr": 4999 },
    { "name": "Champion",   "min_mmr": 5000, "max_mmr": 15000 }
]


def _get_rank_from_MMR(mmr):
    for r in RANKS:
        if r['min_mmr'] <= int(mmr) <= r['max_mmr']:
            return r['name'], r['min_mmr'], r['max_mmr']
    return 'Unranked', 0, 0

def _get_uids(a):
    x = []
    for i in a:
        x.append(i)
    return x

def _sort_atk_def(ops):
    atk,defn = {},{}
    for op in ops:
        op = ops[op]
        if op['atkdef'] == 'attacker':
            atk[op['name']] = op
        elif op['atkdef'] == 'defender':
            defn[op['name']] = op
    return {'atk':atk,'def':defn}

def _get_top_op(ops):
    return OrderedDict(sorted(ops.items(), key=lambda i: i[1]['time_played'])).popitem(last=True)[1]

async def rainbow6stats(id_username_dict, mmr_watch_data):
    xd = {'all_data':{}, 'main_data':{}, 'mmr_watch':{}}
    UIDS = _get_uids(id_username_dict)

    auth = Auth(UBISOFT_EMAIL, UBISOFT_PASSW)

    players = await auth.get_player_batch(uids=UIDS, platform=Platforms.UPLAY)
    ranks = await players.get_rank()
    casuals = await players.get_casual()

    count = 1

    for p in players:
        print(f'Processing [{p.id}].. ({count}/{len(UIDS)})')
        await p.check_general()
        await p.load_level()
        await p.load_queues()
        r = ranks[p.id]
        c = casuals[p.id]

        pr = p.ranked
        pc = p.casual

        ops = await p.load_all_operators()
        operator_data = {}
        for o in ops:
            operator_data[o] = ops[o].get_array()
        operator_data = _sort_atk_def(operator_data)

        top_2_ops = {"atk1": _get_top_op(operator_data['atk']),
                     "def1": _get_top_op(operator_data['def'])}

        casualRankName, casualRankPrev, casualRankNext = _get_rank_from_MMR(c.mmr)

        # Get Weapon type data
        w = await p.check_weapons()
        weapon_type_data = []
        for weapon in w:
            weapon_type_data.append(weapon.get_dict())

        # MMR Watch
        if mmr_watch_data.get(p.id, None) is None:
            mmr_watch_data[p.id] = {'mmr':r.mmr,'playtime':p.time_played}

        mw_mmr = mmr_watch_data[p.id]['mmr']
        mw_plt = mmr_watch_data[p.id]['playtime']
        xd['mmr_watch'][p.id] = {
            "mmr": r.mmr,
            "playtime": p.time_played,
            "adjustment": False,
            "adjustment_value": 0
        }
        if p.time_played == mw_plt and r.mmr != mw_mmr:
            xd['mmr_watch'][p.id]['mmr'] = mw_mmr
            xd['mmr_watch'][p.id]['playtime'] = mw_plt
            xd['mmr_watch'][p.id]['adjustment'] = True
            xd['mmr_watch'][p.id]['adjustment_value'] = r.mmr - mw_mmr
            print("MMR Adjustment detected!")
            print(xd['mmr_watch'][p.id])

        all_data = {
            'operators': operator_data,
            'weapon_types': weapon_type_data,

            'discordUsername': id_username_dict[p.id],
            'seasonName': 'Crimson Heist',
            'season': r.season,

            'currentRankImage': get_rank(r.get_rank_name()),
            'maxRankImage': get_rank(r.get_max_rank_name()),
            'currentRank': r.get_rank_name(),
            'maxRank': r.get_max_rank_name(),
            'maxMMR': r.max_mmr,
            'currentMMR': r.mmr,
            'prevRankMMR': r.prev_rank_mmr,
            'nextRankMMR': r.next_rank_mmr,
            'lastMMRchange': r.last_mmr_change,

            'sWins': r.wins,
            'sLosses': r.losses,
            'sKills': r.kills,
            'sDeaths': r.deaths,
            'sAbandons': r.abandons,

            'currentRankImageCasual': get_rank(casualRankName),
            'currentRankCasual': casualRankName,
            'currentMMRcasual': c.mmr,
            'prevRankMMRcasual': casualRankPrev,
            'nextRankMMRcasual': casualRankNext,
            'lastMMRchangeCasual': c.last_mmr_change,
            'sWinsCasual': c.wins,
            'sLossesCasual': c.losses,
            'sKillsCasual': c.kills,
            'sDeathsCasual': c.deaths,
            'sAbandonsCasual': c.abandons,

            'hs': round((p.headshots/p.kills)*100, 2),
            'xp': p.xp,
            'level': p.level,
            'alphapackProbability': p.lootbox_probability,

            'rankedGames':pr.played,
            'rankedWins':pr.won,
            'rankedLosses':pr.lost,
            'rankedPlaytime':pr.time_played,
            'rankedKills':pr.kills,
            'rankedDeaths':pr.deaths,

            'casualGames':pc.played,
            'casualWins':pc.won,
            'casualLosses':pc.lost,
            'casualPlaytime':pc.time_played,
            'casualKills':pc.kills,
            'casualDeaths':pc.deaths,

            'totalPlaytime': p.time_played,
            'totalHeadshots': p.headshots,
            'totalKills': p.kills,
            'totalDeaths': p.deaths,
            'totalAssists': p.kill_assists,
            'totalMatches': p.matches_played,
            'totalWins': p.matches_won,
            'totalLosses': p.matches_lost,
            'totalBlindKills': p.blind_kills,
            'totalMeleeKills': p.melee_kills,
            'totalPenetrationKills': p.penetration_kills,
            'totalReinforcements': p.reinforcements_deployed,
            'totalBarricades': p.barricades_deployed,
            'totalGadgetsDestroyed': p.gadgets_destroyed,
            'totalSuicides': p.suicides,
            'totalDBNOs': p.dbnos,

            'ubisoftID': p.id,
            'ubisoftUsername': p.name,
        }
        main_data = {
            'ubisoftID': p.id,
            'ubisoftUsername': p.name,

            'currentRankImage': get_rank(r.get_rank_name()),
            'maxRankImage': get_rank(r.get_max_rank_name()),
            'currentRank': r.get_rank_name(),
            'maxRank': r.get_max_rank_name(),
            'maxMMR': r.max_mmr,
            'currentMMR': r.mmr,
            'prevRankMMR': r.prev_rank_mmr,
            'nextRankMMR': r.next_rank_mmr,
            'lastMMRchange': r.last_mmr_change,

            'sWins': r.wins,
            'sLosses': r.losses,
            'sKills': r.kills,
            'sDeaths': r.deaths,
            'sAbandons': r.abandons,

            'alphapackProbability': p.lootbox_probability,

            'operators': top_2_ops,

            'totalPlaytime': p.time_played,
            'casualPlaytime':pc.time_played,
            'rankedPlaytime':pr.time_played,

            'hs': round((p.headshots/p.kills)*100, 2),
        }

        xd['all_data'][p.id] = all_data
        xd['main_data'][p.id] = main_data
        print(f"Done! [{p.id}]")
        count+=1

    await auth.close()
    return xd

def get_rank(rank):
    # A really obscene way to do this, BUT it was easier than to use the Firebase Storage calls every time
    rank_dict = {
        "unranked": "https://i.imgur.com/RpPdtbU.png",
        "copper 5": "https://i.imgur.com/SNSfudP.png",
        "copper 4": "https://i.imgur.com/7PiisA2.png",
        "copper 3": "https://i.imgur.com/aNCvwAI.png",
        "copper 2": "https://i.imgur.com/fUzUApd.png",
        "copper 1": "https://i.imgur.com/eGuxE0k.png",
        "bronze v": "https://i.imgur.com/bbjMf4V.png",
        "bronze 4": "https://i.imgur.com/75IEQkD.png",
        "bronze 3": "https://i.imgur.com/GIt29R0.png",
        "bronze 2": "https://i.imgur.com/sTIXKlh.png",
        "bronze 1": "https://i.imgur.com/zKRDUdK.png",
        "silver 5": "https://i.imgur.com/CbAbvOa.png",
        "silver 4": "https://i.imgur.com/2Y8Yr11.png",
        "silver 3": "https://i.imgur.com/zNUuJSn.png",
        "silver 2": "https://i.imgur.com/utTa5mq.png",
        "silver 1": "https://i.imgur.com/27ISr4q.png",
        "gold 4": "https://i.imgur.com/YIWWNzf.png",
        "gold 3": "https://i.imgur.com/JJvq35l.png",
        "gold 2": "https://i.imgur.com/Fco8pIl.png",
        "gold 1": "https://i.imgur.com/m8FFWGi.png",
        "platinum 3": "https://i.imgur.com/GpEpkDs.png",
        "platinum 2": "https://i.imgur.com/P8IO0Sn.png",
        "platinum 1": "https://i.imgur.com/52Y4EVg.png",
        "diamond 3": "https://i.imgur.com/HHPc5HQ.png",
        "diamond 2": "https://i.imgur.com/HHPc5HQ.png",
        "diamond 1": "https://i.imgur.com/HHPc5HQ.png",
        "champion": "https://i.imgur.com/QHZFdUj.png"
    }
    return rank_dict.get(rank.lower())

# Here only cuz i reall don't want to go through the struggle
# of getting all these links from Firebase storage again
# Same images are on the imgur..
OLD_RANK_DICT = {
    "unranked": "https://firebasestorage.googleapis.com/v0/b/chuckwalla-69.appspot.com/o/R6%20Ranks%2FUnranked.png?alt=media&token=295b2528-9813-4add-a46f-9e5c7e2a13c8",
    "copper 5": "https://firebasestorage.googleapis.com/v0/b/chuckwalla-69.appspot.com/o/R6%20Ranks%2FCopper_05.png?alt=media&token=34112e43-01cd-496a-83ca-a6d2008b1c70",
    "copper 4": "https://firebasestorage.googleapis.com/v0/b/chuckwalla-69.appspot.com/o/R6%20Ranks%2FCopper_04.png?alt=media&token=4e1351b3-25bc-4176-a7a0-f513626be2d7",
    "copper 3": "https://firebasestorage.googleapis.com/v0/b/chuckwalla-69.appspot.com/o/R6%20Ranks%2FCopper_03.png?alt=media&token=b6e0acf8-98d0-4acf-b991-e660ec57be36",
    "copper 2": "https://firebasestorage.googleapis.com/v0/b/chuckwalla-69.appspot.com/o/R6%20Ranks%2FCopper_02.png?alt=media&token=85f9e162-5a17-45ff-bac4-b7ceb08391ff",
    "copper 1": "https://firebasestorage.googleapis.com/v0/b/chuckwalla-69.appspot.com/o/R6%20Ranks%2FCopper_01.png?alt=media&token=f7bdf9c6-a82d-4ca4-a12c-b73dc1a68cd5",
    "bronze v": "https://firebasestorage.googleapis.com/v0/b/chuckwalla-69.appspot.com/o/R6%20Ranks%2FBronze_05.png?alt=media&token=46f3b6d7-22ad-478d-841f-af659a254b6e",
    "bronze 4": "https://firebasestorage.googleapis.com/v0/b/chuckwalla-69.appspot.com/o/R6%20Ranks%2FBronze_04.png?alt=media&token=ccb5e10e-4941-469d-8b2b-2c5b0d1d58bd",
    "bronze 3": "https://firebasestorage.googleapis.com/v0/b/chuckwalla-69.appspot.com/o/R6%20Ranks%2FBronze_03.png?alt=media&token=fa0aa632-b533-44d7-aefc-57a5a1aad708",
    "bronze 2": "https://firebasestorage.googleapis.com/v0/b/chuckwalla-69.appspot.com/o/R6%20Ranks%2FBronze_02.png?alt=media&token=70f6b0c8-307a-4bfb-9f83-c1e98e9748d9",
    "bronze 1": "https://firebasestorage.googleapis.com/v0/b/chuckwalla-69.appspot.com/o/R6%20Ranks%2FBronze_01.png?alt=media&token=a4ef33bb-cebe-49f9-a712-9b0e28af1a14",
    "silver 5": "https://firebasestorage.googleapis.com/v0/b/chuckwalla-69.appspot.com/o/R6%20Ranks%2FSilver_05.png?alt=media&token=85011248-cf4e-4799-bee9-eb758375de7c",
    "silver 4": "https://firebasestorage.googleapis.com/v0/b/chuckwalla-69.appspot.com/o/R6%20Ranks%2FSilver_04.png?alt=media&token=454fe077-5a6e-4c9f-887e-c789265374a9",
    "silver 3": "https://firebasestorage.googleapis.com/v0/b/chuckwalla-69.appspot.com/o/R6%20Ranks%2FSilver_03.png?alt=media&token=9e50ead1-cf08-4f55-a99c-da9160f8f171",
    "silver 2": "https://firebasestorage.googleapis.com/v0/b/chuckwalla-69.appspot.com/o/R6%20Ranks%2FSilver_02.png?alt=media&token=8fd1e6df-67a1-4abd-820a-b5da03cc2e23",
    "silver 1": "https://firebasestorage.googleapis.com/v0/b/chuckwalla-69.appspot.com/o/R6%20Ranks%2FSilver_01.png?alt=media&token=4331a891-e150-4b18-b940-50667ec27185",
    "gold 4": "https://firebasestorage.googleapis.com/v0/b/chuckwalla-69.appspot.com/o/R6%20Ranks%2FGOLD_04.png?alt=media&token=bae67b53-35f3-4f81-a019-a7a69fe82f67",
    "gold 3": "https://firebasestorage.googleapis.com/v0/b/chuckwalla-69.appspot.com/o/R6%20Ranks%2FGOLD_03.png?alt=media&token=9a489888-23ac-4290-97fc-59276dc34044",
    "gold 2": "https://firebasestorage.googleapis.com/v0/b/chuckwalla-69.appspot.com/o/R6%20Ranks%2FGOLD_02.png?alt=media&token=615b0a9f-39c6-4db2-a97e-13fa5b0bf8c1",
    "gold 1": "https://firebasestorage.googleapis.com/v0/b/chuckwalla-69.appspot.com/o/R6%20Ranks%2FGOLD_01.png?alt=media&token=3661b9e6-99d8-4742-a913-9788ac94c810",
    "platinum 3": "https://firebasestorage.googleapis.com/v0/b/chuckwalla-69.appspot.com/o/R6%20Ranks%2FPlatinum_03.png?alt=media&token=e5944dea-8df2-4b33-a6e7-b07800bd870b",
    "platinum 2": "https://firebasestorage.googleapis.com/v0/b/chuckwalla-69.appspot.com/o/R6%20Ranks%2FPlatinum_02.png?alt=media&token=9a09a0f4-2d66-4092-8e26-3d4528c315a4",
    "platinum 1": "https://firebasestorage.googleapis.com/v0/b/chuckwalla-69.appspot.com/o/R6%20Ranks%2FPlatinum_01.png?alt=media&token=00086d17-f099-4c00-a2e8-530392d70ce9",
    "diamond": "https://firebasestorage.googleapis.com/v0/b/chuckwalla-69.appspot.com/o/R6%20Ranks%2FDiamond_01.png?alt=media&token=b64afb2e-4739-4d07-b0d5-41fb74a22b21",
    "champion": "https://firebasestorage.googleapis.com/v0/b/chuckwalla-69.appspot.com/o/R6%20Ranks%2FChampions_01.png?alt=media&token=aefcce88-98cf-48e3-ac76-7acfa2af30c4"
}
