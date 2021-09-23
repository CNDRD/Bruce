import disnake

def gimme_them_stats(mem):
    x = {
        "uid": mem.id,
        "username": mem.name,
        "house": _get_hypesquad_house(mem.public_flags),
        "voice": _get_voice(mem.voice),
        "premium_since": _get_premium(mem.premium_since),
        "status": _get_status(mem.raw_status),
        "is_on_mobile": mem.is_on_mobile(),
        "activities": _get_activities(mem.activities),
        "early_supporter": mem.public_flags.early_supporter
    }
    return x
def _get_hypesquad_house(flags):
    if flags.hypesquad_balance:
        return "balance"
    if flags.hypesquad_bravery:
        return "bravery"
    if flags.hypesquad_brilliance:
        return "brilliance"
    return "none"
def _get_voice(v):
    xd = {
        'deaf': False, 'mute': False,
        'self_mute': False, 'self_deaf': False,
        'self_stream': False, 'self_video': False,
    }

    if v is None:
        return "none"

    if v.deaf:
        xd['deaf'] = True
    if v.mute:
        xd['mute'] = True
    if v.self_mute:
        xd['self_mute'] = True
    if v.self_deaf:
        xd['self_deaf'] = True
    if v.self_stream:
        xd['self_stream'] = True
    if v.self_video:
        xd['self_video'] = True

    return xd
def _get_activities(activities):
    if activities == (): return "none"

    xd = {
        "spotify": "none",
        "custom": "none",
        "other": []
    }

    for activity in activities:
        if isinstance(activity, disnake.activity.Spotify):
            xd["spotify"] = {
                "artist": activity.artists[0],
                "title": activity.title,
            }

        elif isinstance(activity, disnake.activity.CustomActivity):
            if activity.emoji:
                xd["custom"] = {
                    "name": activity.name or "none",
                    "emoji_name": activity.emoji.name or "none",
                    "emoji_url": str(activity.emoji.url) or "none"
                }
            else:
                xd["custom"] = {
                    "name": activity.name or "none",
                    "emoji_name": "none",
                    "emoji_url": "none"
                }

        else:
            xd["other"].append(str(activity.name))

    return xd
def _get_premium(uhh):
    if uhh is None: return "none"
    return datetime.timestamp(uhh)
def _get_status(s):
    if not isinstance(s, str):
        return s[0]
    return s
