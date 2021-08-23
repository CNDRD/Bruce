import requests
import yaml
import os

from dotenv import load_dotenv
load_dotenv()

TRN_Api_Key = os.getenv('TRN_API_KEY')

def _parse_legend_data(uuh):
    x = { 'name': uuh['metadata']['name'], 'imageUrl': uuh['metadata']['imageUrl'], 'tallImageUrl': uuh['metadata']['tallImageUrl'] }
    s = uuh['stats']
    for stat in s:
        x[s[stat]['displayName']] = s[stat]['value']
    return x

def apexStats():
    lmao = {}
    USERNAMES = yaml.safe_load(open('config.yml')).get('apex_usernames')

    for name in USERNAMES:
        headers = { 'TRN-Api-Key': TRN_Api_Key, 'Accept': 'application/json', 'Accept-Encoding': 'gzip' }
        r = requests.get(f"https://public-api.tracker.gg/v2/apex/standard/profile/origin/{name}", headers=headers).json()
        segments = r['data']['segments']
        stats = segments[0]['stats']

        xd = {
            'stats': {
                'level': stats['level']['value'],
                'kills': stats['kills']['value'],
                'rank': stats['rankScore']['metadata']['rankName'],
                'rankIcon': stats['rankScore']['metadata']['iconUrl'],
                'rankArena': stats['arenaRankScore']['metadata']['rankName'],
                'rankArenaIcon': stats['arenaRankScore']['metadata']['iconUrl'],
            }, 'legends': {}
        }

        legends = []
        i = 0
        for legend in segments:
            if i == 0: i = 1
            else:
                i += 1
                legends.append(_parse_legend_data(legend))

        for legend in legends:
            xd['legends'][legend['name']] = legend
        lmao[name] = xd

    return lmao
