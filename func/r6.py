from func.firebase_init import db

from siegeapi import Auth
import time
import os

from dotenv import load_dotenv
load_dotenv()

UBISOFT_EMAIL = os.getenv("UBISOFT_EMAIL")
UBISOFT_PASSW = os.getenv("UBISOFT_PASSW")

R6STATS_VERSION = 11


def _db_ready_trends(data) -> dict[str: dict[str: str | int | float]]:
    xd = {}
    for i, date in enumerate(data.get("stats_period")):
        xd[date] = {
            "kill_death_ratio": data["kill_death_ratio"][i],
            "win_loss_ratio": data["win_loss_ratio"][i],
            "headshot_accuracy": data["headshot_accuracy"][i],
            "minutes_played": data["minutes_played"][i],
            "matches_played": data["matches_played"][i],
            "rounds_played": data["rounds_played"][i],
            "rounds_with_ace": data["rounds_with_ace"][i],
            "revives": data["revives"][i],
            "assists": data["assists"][i],
            "team_kills": data["team_kills"][i],
            "trades": data["trades"][i],
            "rounds_with_kost": data["rounds_with_kost"][i],
        }
    return xd


def _get_db_weapons(w) -> list[dict[str: int | float | str]]:
    return [vars(weapon) for weapon in (w.primary+w.secondary)]


def get_rank_image_url(rank) -> str:
    rank_dict = {
        "unranked": "RpPdtbU", "champion": "QHZFdUj",
        "copper 5": "SNSfudP", "copper 4": "7PiisA2", "copper 3": "aNCvwAI", "copper 2": "fUzUApd", "copper 1": "eGuxE0k",
        "bronze 5": "bbjMf4V", "bronze 4": "75IEQkD", "bronze 3": "GIt29R0", "bronze 2": "sTIXKlh", "bronze 1": "zKRDUdK",
        "silver 5": "CbAbvOa", "silver 4": "2Y8Yr11", "silver 3": "zNUuJSn", "silver 2": "utTa5mq", "silver 1": "27ISr4q",
        "gold 4": "YIWWNzf", "gold 3": "JJvq35l", "gold 2": "Fco8pIl", "gold 1": "m8FFWGi",
        "platinum 3": "GpEpkDs", "platinum 2": "P8IO0Sn", "platinum 1": "52Y4EVg",
        "diamond 3": "XEqbdS5", "diamond 2": "A9hsLtc", "diamond 1": "n0izxYa",
    }
    return f"https://i.imguseasonal_ranked.com/{rank_dict.get(rank.lower())}.png"


def _get_sorted_list_of_operators(ops):
    return sorted([vars(op) for op in ops], key=lambda d: d["minutes_played"])


async def rainbow6stats():
    mmr_watch_data = db.child("GameStats").child(f"R6Sv{R6STATS_VERSION}").child("mmr_watch").get().val() or {}
    mmr_watch = {}
    mmr_watch_message = ""
    playtimes = db.child("GameStats").child(f"R6Sv{R6STATS_VERSION}").child("playtimes").get().val() or {}

    users = db.child("GameStats").child("IDs").get().val()
    uids = [user.get("ubiID") for user in users.values() if user.get("ubiID") is not None]

    auth = Auth(UBISOFT_EMAIL, UBISOFT_PASSW)
    players = await auth.get_player_batch(uids=uids)

    for p in players.values():

        # MMR Check
        await p.load_playtime()
        seasonal_ranked = await p.load_ranked()
        current_season_id = seasonal_ranked.season

        if mmr_watch_data.get(p.id, None) is None:
            mmr_watch_data[p.id] = {"mmr": seasonal_ranked.mmr, "playtime": p.total_time_played}

        message_sent = mmr_watch_data[p.id].get("message_sent", False)
        mw_mmr = mmr_watch_data[p.id]["mmr"]
        mw_plt = mmr_watch_data[p.id]["playtime"]
        mmr_watch[p.id] = {
            "mmr": seasonal_ranked.mmr,
            "playtime": p.total_time_played,
            "adjustment": False,
            "adjustment_value": 0,
            "message_sent": message_sent,
        }
        if p.total_time_played == mw_plt and seasonal_ranked.mmr != mw_mmr:
            mmr_watch[p.id] = {
                "mmr": mw_mmr,
                "playtime": mw_plt,
                "adjustment": True,
                "adjustment_value": mw_mmr - seasonal_ranked.mmr,
                "message_sent": message_sent,
            }
            print(f"MMR Adjustment detected! \n {mmr_watch[p.id]}")

            if not mmr_watch_data[p.id].get("message_sent", False):
                mmr_watch_message += f"**{p.name}** just __*{'lost' if (mw_mmr-seasonal_ranked.mmr) < 0 else 'gained'}*__ ***{int(mw_mmr-seasonal_ranked.mmr)}*** MMR\n"
                mmr_watch[p.id]["message_sent"] = True

        # Check if playtime changed, so we can skip checking stats that didn't change
        db_total_playtime = playtimes.get(p.id, 0)
        if db_total_playtime == p.total_time_played:
            continue

        # XP & Level
        await p.load_progress()

        # Operators
        await p.load_operators()
        operators_attackers = _get_sorted_list_of_operators(p.operators.all.attacker)
        operators_defenders = _get_sorted_list_of_operators(p.operators.all.defender)

        # Trends
        await p.load_trends()
        trends = _db_ready_trends((vars(p.trends.all.all)))

        # Current seasonal data
        seasonal_ranked = seasonal_ranked.get_dict()  # Already loaded for MMR Watch
        seasonal_casual = (await p.load_casual()).get_dict()
        seasonal_events = (await p.load_events()).get_dict()

        # Gamemodes data
        await p.load_gamemodes()
        gamemode_all = vars(p.gamemodes.all)
        gamemode_casual = vars(p.gamemodes.casual)
        gamemode_ranked = vars(p.gamemodes.ranked)
        gamemode_unranked = vars(p.gamemodes.unranked)
        gamemode_newcomer = vars(p.gamemodes.newcomer)

        # Weapons
        await p.load_weapons()
        weapons = _get_db_weapons(p.weapons.all)

        all_data = {
            "ubisoftID": p.id,
            "ubisoftUsername": p.name,

            "seasonal": {
                "ranked": seasonal_ranked,
                "casual": seasonal_casual,
                "events": seasonal_events,
            },
            "progress": {
                "xp": p.xp,
                "totalXp": p.total_xp,
                "xpToLevelUp": p.xp_to_level_up,
                "level": p.level,
                "alphapackProbability": p.alpha_pack
            },
            "playtimes": {
                "total": p.total_time_played,
                "pvp": p.pvp_time_played,
                "pve": p.pve_time_played
            },
            "operators": {
                "atk": operators_attackers,
                "def": operators_defenders
            },
            "gamemodes": {
                "all": gamemode_all,
                "casual": gamemode_casual,
                "ranked": gamemode_ranked,
                "unranked": gamemode_unranked,
                "newcomer": gamemode_newcomer,
            },
            "weapons": weapons,
            "trends": trends,
        }
        main_data = {
            "level": p.level,
            "ubisoftID": p.id,
            "ubisoftUsername": p.name,
            "alphapackProbability": p.alpha_pack,
            "totalPlaytime": p.total_time_played,
            "ranked": seasonal_ranked,
            "operators": {
                "atk": operators_attackers[-1],
                "def": operators_defenders[-1]
            }
        }

        db.child("GameStats").child(f"R6Sv{R6STATS_VERSION}").child("main_data").child(p.id).update(main_data)
        db.child("GameStats").child(f"R6Sv{R6STATS_VERSION}").child("all_data").child(p.id).update(all_data)
        db.child("GameStats").child(f"R6Sv{R6STATS_VERSION}").child("seasonal_data").child(p.id).update({current_season_id: seasonal_ranked})
        db.child("GameStats").child(f"R6Sv{R6STATS_VERSION}").child("playtimes").update({p.id: p.total_time_played})

    db.child("GameStats").child(f"R6Sv{R6STATS_VERSION}").child("mmr_watch").update(mmr_watch)
    db.child('GameStats').child("lastUpdate").update({f"R6Sv{R6STATS_VERSION}": int(time.time())})
    return mmr_watch_message
