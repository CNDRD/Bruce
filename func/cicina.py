import requests
import json


def get_cicina_today(today, today_date):
    if today is None:
        return None

    xd = []
    for u in today:
        if today[u]['date'] == today_date:
            today[u].pop('date')
            xd.append(today[u])

    if not xd:
        return None
    return xd


def get_random_cicina(api_key: str) -> int:

    data = json.dumps({
        "jsonrpc": "2.0", "method": "generateIntegers", 'id': 1,
        "params": {"apiKey": api_key, "n": 1, "min": 0, "max": 50, "replacement": True}
    })
    headers = {'Content-type': 'application/json', 'Content-Length': '200', 'Accept': 'application/json'}
    response = requests.post(url='https://api.random.org/json-rpc/2/invoke', data=data, headers=headers)
    return response.json().get('result').get('random').get('data')[0]
