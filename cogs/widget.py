import pyrebase, yaml, random, json, os, discord
from discord.ext import commands, tasks
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

## Config Load ##
config = yaml.safe_load(open('config.yml'))
diskito_id = config.get('diskito_id')

## Firebase Database ##
firebase_config = {"apiKey": "AIzaSyDe_xKKup4lVoPasLmAQW9Csc1zUzsxB0U","authDomain": "chuckwalla-69.firebaseapp.com",
  "databaseURL": "https://chuckwalla-69.firebaseio.com","storageBucket": "chuckwalla-69.appspot.com",
  "serviceAccount": json.loads(os.getenv("serviceAccountKeyJSON"))}
db = pyrebase.initialize_app(firebase_config).database()

class Widget(commands.Cog):
    def __init__(self, client):
        """
        Custom Widget
        """
        self.client = client
        self.widget_loop.start()


    @tasks.loop(hours=69.69)
    async def widget_loop(self):
        diskito = self.client.get_guild(diskito_id)
        widgeee = {}

        for member in diskito.members:
            if not member.bot:
                xd = {
                    "uid": member.id,
                    "username": member.name,
                    "house": getHypesquadHouse(member.public_flags),
                    "voice": getVoice(member.voice),
                    "premium_since": getPremium(member.premium_since),
                    "status": getStatus(member.raw_status),
                    "is_on_mobile": member.is_on_mobile(),
                    "color": getColor(member.color.to_rgb()),
                    "activities": getActivities(member.activities),
                }
                widgeee[member.id] = xd
        db.child("widget").update(widgeee)


    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if after.guild.id != diskito_id: return
        if after.bot: return

        x = {
            "uid": after.id,
            "username": after.name,
            "house": getHypesquadHouse(after.public_flags),
            "voice": getVoice(after.voice),
            "premium_since": getPremium(after.premium_since),
            "status": getStatus(after.raw_status),
            "is_on_mobile": after.is_on_mobile(),
            "color": getColor(after.color.to_rgb()),
            "activities": getActivities(after.activities),
        }

        db.child("widget").child(x["uid"]).update(x)


def setup(client):
    client.add_cog(Widget(client))


def getHypesquadHouse(flags):
    if flags.hypesquad_balance:
        return "balance"
    if flags.hypesquad_bravery:
        return "bravery"
    if flags.hypesquad_brilliance:
        return "brilliance"
    return "none"

def getVoice(v):
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

def getActivities(activities):
    if activities == (): return "none"

    xd = {
        "spotify": "none",
        "custom": "none",
        "other": []
    }
    for activity in activities:

        if isinstance(activity, discord.activity.Spotify):
            xd["spotify"] = {
                "artist": activity.artists[0],
                "title": activity.title,
                "album_cover_url": activity.album_cover_url,
            }

        elif isinstance(activity, discord.activity.CustomActivity):
            xd["custom"] = {
                "name": activity.name or "none"
            }

            if activity.emoji:
                xd["custom"] = {
                    "emoji_name": activity.emoji.name or "none",
                    "emoji_url": str(activity.emoji.url) or "none"
                }
            else:
                xd["custom"] = {
                    "emoji_name": "none",
                    "emoji_url": "none"
                }

        else:
            xd["other"].append(str(activity.name))

    return xd

def getPremium(uhh):
    if uhh is None: return "none"
    return datetime.timestamp(uhh)

def getColor(xd):
    return {"r": xd[0], "g": xd[1], "b": xd[2]}

def getStatus(s):
    if not isinstance(s, str):
        return s[0]
    return s
