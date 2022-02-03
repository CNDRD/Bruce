import os
from siegeapi import Auth, Platforms
from collections import OrderedDict

from dotenv import load_dotenv

load_dotenv()

UBISOFT_EMAIL = os.getenv("UBISOFT_EMAIL")
UBISOFT_PASSW = os.getenv("UBISOFT_PASSW")

RANKS = [
    {"name": "Copper 5", "min_mmr": 1, "max_mmr": 1199},
    {"name": "Copper 4", "min_mmr": 1200, "max_mmr": 1299},
    {"name": "Copper 3", "min_mmr": 1300, "max_mmr": 1399},
    {"name": "Copper 2", "min_mmr": 1400, "max_mmr": 1499},
    {"name": "Copper 1", "min_mmr": 1500, "max_mmr": 1599},
    {"name": "Bronze 5", "min_mmr": 1600, "max_mmr": 1699},
    {"name": "Bronze 4", "min_mmr": 1700, "max_mmr": 1799},
    {"name": "Bronze 3", "min_mmr": 1800, "max_mmr": 1899},
    {"name": "Bronze 2", "min_mmr": 1900, "max_mmr": 1999},
    {"name": "Bronze 1", "min_mmr": 2000, "max_mmr": 2099},
    {"name": "Silver 5", "min_mmr": 2100, "max_mmr": 2199},
    {"name": "Silver 4", "min_mmr": 2200, "max_mmr": 2299},
    {"name": "Silver 3", "min_mmr": 2300, "max_mmr": 2399},
    {"name": "Silver 2", "min_mmr": 2400, "max_mmr": 2499},
    {"name": "Silver 1", "min_mmr": 2500, "max_mmr": 2599},
    {"name": "Gold 3", "min_mmr": 2600, "max_mmr": 2799},
    {"name": "Gold 2", "min_mmr": 2800, "max_mmr": 2999},
    {"name": "Gold 1", "min_mmr": 3000, "max_mmr": 3199},
    {"name": "Platinum 3", "min_mmr": 3200, "max_mmr": 3499},
    {"name": "Platinum 2", "min_mmr": 3500, "max_mmr": 3799},
    {"name": "Platinum 1", "min_mmr": 3800, "max_mmr": 4099},
    {"name": "Diamond 3", "min_mmr": 4100, "max_mmr": 4399},
    {"name": "Diamond 2", "min_mmr": 4400, "max_mmr": 4699},
    {"name": "Diamond 1", "min_mmr": 4700, "max_mmr": 4999},
    {"name": "Champion", "min_mmr": 5000, "max_mmr": 15000}
]


def _get_rank_from_mmr(mmr) -> tuple[str, int, int]:
    for r in RANKS:
        if r["min_mmr"] <= int(mmr) <= r["max_mmr"]:
            return r["name"], r["min_mmr"], r["max_mmr"]
    return "Unranked", 0, 0


def _get_uids(a) -> list[str]:
    return [i for i in a]


def _sort_atk_def(ops) -> dict[str: dict[str: dict[str: int | str | dict[str: dict[str: str | int]]]]]:
    atk, defn = {}, {}
    for op in ops:
        op = ops[op]
        if op["atkdef"] == "attacker":
            atk[op["name"]] = op
        elif op["atkdef"] == "defender":
            defn[op["name"]] = op
    return {"atk": atk, "def": defn}


def _get_top_op(ops) -> OrderedDict:
    return OrderedDict(sorted(ops.items(), key=lambda i: i[1]["time_played"])).popitem(last=True)[1]


async def rainbow6stats(id_username_dict, mmr_watch_data, last_db_update) -> (dict, str):
    xd = {"all_data": {}, "main_data": {}, "mmr_watch": {}}
    mmr_watch_message = ""
    uids = _get_uids(id_username_dict)

    auth = Auth(UBISOFT_EMAIL, UBISOFT_PASSW)

    players = await auth.get_player_batch(uids=uids, platform=Platforms.UPLAY)

    ranks = await players.load_rank()
    casuals = await players.load_casual()

    count = 1

    for p in players:
        print(f"Processing [{p.id}].. ({count}/{len(uids)})")
        await p.load_playtime()
        await p.load_general()
        await p.load_level()
        await p.load_gamemodes()

        r = ranks[p.id]
        c = casuals[p.id]

        pr = p.ranked
        pc = p.casual

        ops = await p.load_all_operators()
        operator_data = {}
        for o in ops:
            operator_data[o] = ops[o].get_dict()
        operator_data = _sort_atk_def(operator_data)

        top_2_ops = {
            "atk1": _get_top_op(operator_data["atk"]),
            "def1": _get_top_op(operator_data["def"])
        }

        casual_rank_name, casual_rank_prev, casual_rank_next = _get_rank_from_mmr(c.mmr)

        # Get Weapon type data
        await p.load_weapon_types()
        weapon_type_data = []
        for weapon in p.weapons:
            weapon_type_data.append(weapon.get_dict())

        # MMR Watch
        if mmr_watch_data.get(p.id, None) is None:
            mmr_watch_data[p.id] = {"mmr": r.mmr, "playtime": p.time_played}

        mw_mmr = mmr_watch_data[p.id]["mmr"]
        mw_plt = mmr_watch_data[p.id]["playtime"]
        xd["mmr_watch"][p.id] = {
            "mmr": r.mmr,
            "playtime": p.time_played,
            "adjustment": False,
            "adjustment_value": 0
        }

        if p.time_played == mw_plt and r.mmr != mw_mmr:
            print(f"MMR Adjustment detected! \n {xd['mmr_watch'][p.id]}")
            xd["mmr_watch"][p.id] = {
                "mmr": mw_mmr,
                "playtime": mw_plt,
                "adjustment": True,
                "adjustment_value": mw_mmr - r.mmr
            }

            if not mmr_watch_data[p.id].get("message_sent", False):
                mmr_watch_message += f"**{p.name}** just __*{'lost' if (mw_mmr-r.mmr) < 0 else 'gained'}*__ ***{int(mw_mmr-r.mmr)}*** MMR"
                xd["mmr_watch"][p.id]["message_sent"] = True

        all_data = {
            'operators': operator_data,
            'weapon_types': weapon_type_data,

            'discordUsername': id_username_dict[p.id],
            'season': r.season,

            'currentRankImage': get_rank(r.rank),
            'maxRankImage': get_rank(r.max_rank),
            'currentRank': r.rank,
            'maxRank': r.max_rank,
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

            'currentRankImageCasual': get_rank(casual_rank_name),
            'currentRankCasual': casual_rank_name,
            'currentMMRcasual': c.mmr,
            'prevRankMMRcasual': casual_rank_prev,
            'nextRankMMRcasual': casual_rank_next,
            'lastMMRchangeCasual': c.last_mmr_change,
            'sWinsCasual': c.wins,
            'sLossesCasual': c.losses,
            'sKillsCasual': c.kills,
            'sDeathsCasual': c.deaths,
            'sAbandonsCasual': c.abandons,

            'hs': round((p.headshots / p.kills) * 100, 2),
            'xp': p.xp,
            'level': p.level,
            'alphapackProbability': p.lootbox_probability,

            'rankedGames': pr.played,
            'rankedWins': pr.won,
            'rankedLosses': pr.lost,
            'rankedPlaytime': pr.time_played,
            'rankedKills': pr.kills,
            'rankedDeaths': pr.deaths,

            'casualGames': pc.played,
            'casualWins': pc.won,
            'casualLosses': pc.lost,
            'casualPlaytime': pc.time_played,
            'casualKills': pc.kills,
            'casualDeaths': pc.deaths,

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

            'currentRankImage': get_rank(r.rank),
            'maxRankImage': get_rank(r.max_rank),
            'currentRank': r.rank,
            'maxRank': r.max_rank,
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
            'casualPlaytime': pc.time_played,
            'rankedPlaytime': pr.time_played,

            'hs': round((p.headshots / p.kills) * 100, 2),
        }

        xd["all_data"][p.id] = all_data
        xd["main_data"][p.id] = main_data
        print(f"Done!      [{p.id}]")
        count += 1

    if mmr_watch_message:
        mmr_watch_message = f"**Rainbow Six Siege** MMR adjustment announcement \n\n{mmr_watch_message}"
        mmr_watch_message += f"\n\nThis happened since the last check <t:{int(last_db_update)}:R>"

    await auth.close()
    return xd, mmr_watch_message


def get_rank(rank) -> str:
    rank_dict = {
        "unranked": "RpPdtbU",
        "copper 5": "SNSfudP",
        "copper 4": "7PiisA2",
        "copper 3": "aNCvwAI",
        "copper 2": "fUzUApd",
        "copper 1": "eGuxE0k",
        "bronze 5": "bbjMf4V",
        "bronze 4": "75IEQkD",
        "bronze 3": "GIt29R0",
        "bronze 2": "sTIXKlh",
        "bronze 1": "zKRDUdK",
        "silver 5": "CbAbvOa",
        "silver 4": "2Y8Yr11",
        "silver 3": "zNUuJSn",
        "silver 2": "utTa5mq",
        "silver 1": "27ISr4q",
        "gold 4": "YIWWNzf",
        "gold 3": "JJvq35l",
        "gold 2": "Fco8pIl",
        "gold 1": "m8FFWGi",
        "platinum 3": "GpEpkDs",
        "platinum 2": "P8IO0Sn",
        "platinum 1": "52Y4EVg",
        "diamond 3": "XEqbdS5",
        "diamond 2": "A9hsLtc",
        "diamond 1": "n0izxYa",
        "champion": "QHZFdUj"
    }
    return f"https://i.imgur.com/{rank_dict.get(rank.lower())}.png"
