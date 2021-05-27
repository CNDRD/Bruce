import json, requests, yaml, os
from bs4 import BeautifulSoup

from dotenv import load_dotenv
load_dotenv()

TRN_API_KEY = os.getenv('TRN_API_KEY')

def csgostats(sid, discordUsername):
    name = getSteamUsernameFromID64(sid)
    raw_api_data = fetchTrnCsgoAPIdata(name)
    try:
        data = raw_api_data['data']['segments'][0]['stats']
        stats = {}
        stats['pfpLink'] = raw_api_data['data']['platformInfo']['avatarUrl']
        stats['steamID64'] = str(sid)
        stats['discordUsername'] = discordUsername
        stats['steamUsername'] = name
        for x in data:
            stats[x] = data[x]['value']
        return stats
    except:
        return {'private':True, 'discordUsername':discordUsername, 'steamUsername':name, 'steamID64': str(sid)}


def getSteamUsernameFromID64(SID):
    response = requests.get(f'http://steamcommunity.com/profiles/{SID}')
    soup = BeautifulSoup(response.content,'html.parser')
    return soup.find("span", {"class","actual_persona_name"}).get_text()


def fetchTrnCsgoAPIdata(steamID):
    headers = {"TRN-Api-Key":TRN_API_KEY}
    generalEnd = f"https://public-api.tracker.gg/v2/csgo/standard/profile/steam/{steamID}"
    sus = requests.get(generalEnd, headers=headers)
    return sus.json()
