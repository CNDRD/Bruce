from func.firebase_init import db

import requests
import os

from dotenv import load_dotenv
load_dotenv()

PUBG_API_KEY = os.getenv("PUBG_API_KEY")


def pubg_stats() -> None:
    print("Running PUBG Stats")
    big_pp_data = {}

    users = db.child("GameStats").child("IDs").get().val()
    uids = [user.get("PUBG") for user in users.values() if user.get("PUBG") is not None]

    for user_id in uids:
        url = f"https://api.pubg.com/shards/steam/players/{user_id}/seasons/lifetime?filter[gamepad]=false"
        headers = {"Accept": "application/vnd.api+json", "Authorization": f"Bearer {PUBG_API_KEY}"}
        resp = requests.get(url, headers=headers)

        if resp.status_code != 200:
            print(f"err: {resp.status_code}\n{resp}")
            continue

        resp = resp.json()
        stats = resp["data"]["attributes"]["gameModeStats"]
        stats = remove_unplayed_gamemodes(stats)

        big_pp_data[user_id.replace(".", "_")] = stats
        big_pp_data[user_id.replace(".", "_")]["discordUsername"] = get_discord_username_from_id(users, user_id)

    db.child("GameStats").child("PUBG").set(big_pp_data)
    print("PUBG Stats Done")


def remove_unplayed_gamemodes(data) -> dict[str: dict | str]:
    new_data = data.copy()
    gamemodes = ["solo", "solo-fpp", "duo", "duo-fpp", "squad", "squad-fpp"]

    for gamemode in gamemodes:
        if new_data[gamemode]["timeSurvived"] == 0:
            new_data[gamemode] = "None"

    return new_data


def get_discord_username_from_id(users_, uid) -> str:
    for user in users_:
        if users_[user].get("PUBG") == uid:
            return users_[user]["discordUsername"].split("#")[0]
    return "Username Not Found"
