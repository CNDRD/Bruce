from func.firebase_init import db

from siegeapi import Auth
import random
import time
import ast
import os

from dotenv import load_dotenv
load_dotenv()

UBISOFT_CREDENTIALS = ast.literal_eval(os.getenv("UBISOFT_CREDENTIALS"))
UBISOFT_PASSWORD = UBISOFT_CREDENTIALS.get("password")
UBISOFT_EMAILS = UBISOFT_CREDENTIALS.get("emails")
lci = random.randint(0, len(UBISOFT_EMAILS))

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


def _get_sorted_list_of_operators(ops):
    return sorted([vars(op) for op in ops], key=lambda d: d["minutes_played"])


async def rainbow6stats():
    print("Running Rainbow Six Stats")
    mmr_watch_db = db.child("GameStats").child(f"R6Sv{R6STATS_VERSION}").child("mmr_watch").get().val() or {}
    mmr_watch = {}
    mmr_watch_message = ""

    users = db.child("GameStats").child("IDs").get().val()
    uids = [user.get("ubiID") for user in users.values() if user.get("ubiID") is not None]

    global lci
    lci += 1
    if lci >= len(UBISOFT_EMAILS):
        lci = 0
    ubisoft_email = UBISOFT_EMAILS[lci]
    print(f"Logging in using credentials #{lci} | {ubisoft_email}")
    auth = Auth(ubisoft_email, UBISOFT_PASSWORD)
    players = await auth.get_player_batch(uids=uids)

    for p in players.values():

        # MMR Watch v2
        seasonal_ranked = await p.load_ranked()
        current_season_id = seasonal_ranked.season
        await p.load_progress()

        if mmr_watch_db.get(p.id) is None:
            mmr_watch[p.id] = {"mmr": seasonal_ranked.mmr, "xp": p.total_xp}

        message_sent_already = mmr_watch_db.get(p.id, {}).get("message_sent_already", False)
        db_mmr = mmr_watch_db.get(p.id, {}).get("mmr", seasonal_ranked.mmr)
        db_xp = mmr_watch_db.get(p.id, {}).get("xp", p.total_xp)
        adjustment_value = seasonal_ranked.mmr - db_mmr

        mmr_watch[p.id] = {
            "mmr": seasonal_ranked.mmr,
            "xp": p.total_xp,
            "adjustment_value": adjustment_value,
            "adjustment": False,
            "message_sent_already": message_sent_already,
        }

        if db_xp == p.total_xp and adjustment_value != 0:
            mmr_watch[p.id] = {
                "mmr": db_mmr,
                "xp": db_xp,
                "adjustment_value": adjustment_value,
                "adjustment": True,
                "message_sent_already": message_sent_already,
            }
            print(f"MMR Adjustment detected! | {mmr_watch[p.id]}")

            if not message_sent_already:
                mmr_watch_message += f"**{p.name}** just __*{'lost' if adjustment_value < 0 else 'gained'}*__ ***{int(adjustment_value)}*** MMR\n"
                mmr_watch[p.id]["message_sent_already"] = True

        # Check if total XP changed, so we can skip checking stats that didn't change
        if db_xp == p.total_xp:
            continue

        # Playtimes
        await p.load_playtime()

        # Operators
        await p.load_operators(op_about=True)
        operators_attackers = _get_sorted_list_of_operators(p.operators.all.attacker)
        operators_defenders = _get_sorted_list_of_operators(p.operators.all.defender)

        # Trends
        await p.load_trends()
        trends = _db_ready_trends((vars(p.trends.all.all)))

        # Current seasonal data
        seasonal_ranked = seasonal_ranked.get_dict()  # Already loaded for MMR Watch
        seasonal_casual = (await p.load_casual()).get_dict()
        seasonal_events = (await p.load_events()).get_dict()
        seasonal_deathmatch = (await p.load_deathmatch()).get_dict()

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
                "deathmatch": seasonal_deathmatch,
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

    db.child("GameStats").child(f"R6Sv{R6STATS_VERSION}").child("mmr_watch").update(mmr_watch)
    db.child('GameStats').child("lastUpdate").update({f"R6Sv{R6STATS_VERSION}": int(time.time())})
    return mmr_watch_message
