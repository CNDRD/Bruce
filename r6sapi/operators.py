from r6sapi.definitions.operators import *

OperatorUrlStatisticNames = ["operatorpvp_kills","operatorpvp_death","operatorpvp_roundwon",
                             "operatorpvp_roundlost","operatorpvp_meleekills","operatorpvp_totalxp",
                             "operatorpvp_headshot","operatorpvp_timeplayed","operatorpvp_dbno"]

#  DEPRECATED - this dict is no longer updated with new OPs (sorry)
#  theoretically unused
"""
OperatorProfiles = {
    "DOC": "https://ubistatic-a.akamaihd.net/0058/prod/assets/images/large-doc.0b0321eb.png",
    "TWITCH": "https://ubistatic-a.akamaihd.net/0058/prod/assets/images/large-twitch.70219f02.png",
    "ASH": "https://ubistatic-a.akamaihd.net/0058/prod/assets/images/large-ash.9d28aebe.png",
    "THERMITE": "https://ubistatic-a.akamaihd.net/0058/prod/assets/images/large-thermite.e973bb04.png",
    "BLITZ": "https://ubistatic-a.akamaihd.net/0058/prod/assets/images/large-blitz.734e347c.png",
    "BUCK": "https://ubistatic-a.akamaihd.net/0058/prod/assets/images/large-buck.78712d24.png",
    "HIBANA": "https://ubistatic-a.akamaihd.net/0058/prod/assets/images/large-hibana.2010ec35.png",
    "KAPKAN": "https://ubistatic-a.akamaihd.net/0058/prod/assets/images/large-kapkan.db3ab661.png",
    "PULSE": "https://ubistatic-a.akamaihd.net/0058/prod/assets/images/large-pulse.30ab3682.png",
    "CASTLE": "https://ubistatic-a.akamaihd.net/0058/prod/assets/images/large-castle.b95704d7.png",
    "ROOK": "https://ubistatic-a.akamaihd.net/0058/prod/assets/images/large-rook.b3d0bfa3.png",
    "BANDIT": "https://ubistatic-a.akamaihd.net/0058/prod/assets/images/large-bandit.6d7d15bc.png",
    "SMOKE": "https://ubistatic-a.akamaihd.net/0058/prod/assets/images/large-smoke.1bf90066.png",
    "FROST": "https://ubistatic-a.akamaihd.net/0058/prod/assets/images/large-frost.f4325d10.png",
    "VALKYRIE": "https://ubistatic-a.akamaihd.net/0058/prod/assets/images/large-valkyrie.c1f143fb.png",
    "TACHANKA": "https://ubistatic-a.akamaihd.net/0058/prod/assets/images/large-tachanka.41caebce.png",
    "GLAZ": "https://ubistatic-a.akamaihd.net/0058/prod/assets/images/large-glaz.8cd96a16.png",
    "FUZE": "https://ubistatic-a.akamaihd.net/0058/prod/assets/images/large-fuze.dc9f2a14.png",
    "SLEDGE": "https://ubistatic-a.akamaihd.net/0058/prod/assets/images/large-sledge.832f6c6b.png",
    "MONTAGNE": "https://ubistatic-a.akamaihd.net/0058/prod/assets/images/large-montagne.1d04d00a.png",
    "MUTE": "https://ubistatic-a.akamaihd.net/0058/prod/assets/images/large-mute.ae51429f.png",
    "ECHO": "https://ubistatic-a.akamaihd.net/0058/prod/assets/images/large-echo.662156dc.png",
    "THATCHER": "https://ubistatic-a.akamaihd.net/0058/prod/assets/images/large-thatcher.73132fcd.png",
    "CAPITAO": "https://ubistatic-a.akamaihd.net/0058/prod/assets/images/large-capitao.1d0ea713.png",
    "IQ": "https://ubistatic-a.akamaihd.net/0058/prod/assets/images/large-iq.d97d8ee2.png",
    "BLACKBEARD": "https://ubistatic-a.akamaihd.net/0058/prod/assets/images/large-blackbeard.2292a791.png",
    "JAGER": "https://ubistatic-a.akamaihd.net/0058/prod/assets/images/large-jaeger.d8a6c470.png",
    "CAVEIRA": "https://ubistatic-a.akamaihd.net/0058/prod/assets/images/large-caveira.e4d82365.png",
    "DEFAULT": "https://ubistatic-a.akamaihd.net/0058/prod/assets/styles/images/mask-large-bandit.fc038cf1.png"
}
"""
#  DEPRECATED - use Auth.get_operator_badge() instead
#  theoretically unused
"""
OperatorIcons = {
    "DEFAULT": "https://ubistatic19-a.akamaihd.net/resource/en-GB/game/rainbow6/siege/Glaz_Badge_229122.png",
    "HIBANA": "https://ubistatic19-a.akamaihd.net/resource/en-GB/game/rainbow6/siege/R6-operators-badge-hibana_275569.png",
    "SMOKE": "https://ubistatic19-a.akamaihd.net/resource/en-GB/game/rainbow6/siege/Smoke_Badge_196198.png",
    "KAPKAN": "https://ubistatic19-a.akamaihd.net/resource/en-GB/game/rainbow6/siege/Kapkan_Badge_229123.png",
    "TACHANKA": "https://ubistatic19-a.akamaihd.net/resource/en-GB/game/rainbow6/siege/Tachanka_Badge_229124.png",
    "THERMITE": "https://ubistatic19-a.akamaihd.net/resource/en-GB/game/rainbow6/siege/Thermite_Badge_196408.png",
    "THATCHER": "https://ubistatic19-a.akamaihd.net/resource/en-GB/game/rainbow6/siege/Thatcher_Badge_196196.png",
    "GLAZ": "https://ubistatic19-a.akamaihd.net/resource/en-GB/game/rainbow6/siege/Glaz_Badge_229122.png",
    "BANDIT": "https://ubistatic19-a.akamaihd.net/resource/en-GB/game/rainbow6/siege/Bandit_Badge_222163.png",
    "ROOK": "https://ubistatic19-a.akamaihd.net/resource/en-GB/game/rainbow6/siege/Rook_Badge_211296.png",
    "IQ": "https://ubistatic19-a.akamaihd.net/resource/en-GB/game/rainbow6/siege/IQ_Badge_222165.png",
    "PULSE": "https://ubistatic19-a.akamaihd.net/resource/en-GB/game/rainbow6/siege/Pulse_Badge_202497.png",
    "MUTE": "https://ubistatic19-a.akamaihd.net/resource/en-GB/game/rainbow6/siege/Mute_Badge_196195.png",
    "VALKYRIE": "https://ubistatic19-a.akamaihd.net/resource/en-GB/game/rainbow6/siege/R6-operators-badge-valkyrie_250313.png",
    "FROST": "https://ubistatic19-a.akamaihd.net/resource/en-GB/game/rainbow6/siege/R6-operators-badge-frost_237595.png",
    "DOC": "https://ubistatic19-a.akamaihd.net/resource/en-GB/game/rainbow6/siege/Doc_Badge_211294.png",
    "SLEDGE": "https://ubistatic19-a.akamaihd.net/resource/en-GB/game/rainbow6/siege/Sledge_Badge_196197.png",
    "JAGER": "https://ubistatic19-a.akamaihd.net/resource/en-GB/game/rainbow6/siege/Jager_Badge_222166.png",
    "BLACKBEARD": "https://ubistatic19-a.akamaihd.net/resource/en-GB/game/rainbow6/siege/R6-operators-badge-blackbeard_250312.png",
    "FUZE": "https://ubistatic19-a.akamaihd.net/resource/en-GB/game/rainbow6/siege/Fuze_Badge_229121.png",
    "ECHO": "https://ubistatic19-a.akamaihd.net/resource/en-GB/game/rainbow6/siege/R6-operators-badge-echo_275572.png",
    "CAVEIRA": "https://ubistatic19-a.akamaihd.net/resource/en-GB/game/rainbow6/siege/R6-operators-badge-caveira_263102.png",
    "BLITZ": "https://ubistatic19-a.akamaihd.net/resource/en-GB/game/rainbow6/siege/Blitz_Badge_222164.png",
    "MONTAGNE": "https://ubistatic19-a.akamaihd.net/resource/en-GB/game/rainbow6/siege/Montagne_Badge_211295.png",
    "ASH": "https://ubistatic19-a.akamaihd.net/resource/en-GB/game/rainbow6/siege/Ash_Badge_196406.png",
    "TWITCH": "https://ubistatic19-a.akamaihd.net/resource/en-GB/game/rainbow6/siege/Twitch_Badge_211297.png",
    "CASTLE": "https://ubistatic19-a.akamaihd.net/resource/en-GB/game/rainbow6/siege/Castle_Badge_196407.png",
    "BUCK": "https://ubistatic19-a.akamaihd.net/resource/en-GB/game/rainbow6/siege/R6-operators-badge-buck_237592.png",
    "CAPITAO": "https://ubistatic19-a.akamaihd.net/resource/en-GB/game/rainbow6/siege/R6-operators-badge-capitao_263100.png",
    "JACKAL": "https://ubistatic19-a.akamaihd.net/resource/en-GB/game/rainbow6/siege/R6-velvet-shell-badge-jackal_282825.png",
    "MIRA": "https://ubistatic19-a.akamaihd.net/resource/en-GB/game/rainbow6/siege/R6-velvet-shell-badge-mira_282826.png",
    "ELA": "https://ubistatic-a.akamaihd.net/0058/prod/assets/images/badge-ela.63ec2d26.png",
    "LESION": "https://ubistatic-a.akamaihd.net/0058/prod/assets/images/badge-lesion.07c3d352.png",
    "YING": "https://ubistatic-a.akamaihd.net/0058/prod/assets/images/badge-ying.b88be612.png",
    "DOKKAEBI": "https://ubistatic19-a.akamaihd.net/resource/en-us/game/rainbow6/siege/r6-white-noise-badge-dokkaebi_306314.png",
    "VIGIL": "https://ubistatic19-a.akamaihd.net/resource/en-us/game/rainbow6/siege/r6-white-noise-badge-vigil_306315.png",
    "ZOFIA": "https://ubistatic19-a.akamaihd.net/resource/en-gb/game/rainbow6/siege/zofia_badge_306416.png"
}
"""
#  DEPRECATED - use OperatorInfo.unique_abilities[0]
#  theoretically unused
"""
OperatorStatistics = {
    "DOC": "teammaterevive",
    "TWITCH": "gadgetdestroybyshockdrone",
    "ASH": "bonfirewallbreached",
    "THERMITE": "reinforcementbreached",
    "BLITZ": "flashedenemy",
    "BUCK": "kill",
    "HIBANA": "detonate_projectile",
    "KAPKAN": "boobytrapkill",
    "PULSE": "heartbeatspot",
    "CASTLE": "kevlarbarricadedeployed",
    "ROOK": "armortakenteammate",
    "BANDIT": "batterykill",
    "SMOKE": "poisongaskill",
    "FROST": "dbno",
    "VALKYRIE": "camdeployed",
    "TACHANKA": "turretkill",
    "GLAZ": "sniperkill",
    "FUZE": "clusterchargekill",
    "SLEDGE": "hammerhole",
    "MONTAGNE": "shieldblockdamage",
    "MUTE": "gadgetjammed",
    "ECHO": "enemy_sonicburst_affected",
    "THATCHER": "gadgetdestroywithemp",
    "CAPITAO": "lethaldartkills",
    "IQ": "gadgetspotbyef",
    "BLACKBEARD": "gunshieldblockdamage",
    "JAGER": "gadgetdestroybycatcher",
    "CAVEIRA": "interrogations",
    "JACKAL": "cazador_assist_kill",
    "MIRA": "black_mirror_gadget_deployed",
    "LESION": "caltrop_enemy_affected",
    "ELA": "concussionmine_detonate",
    "YING": "dazzler_gadget_detonate",
    "DOKKAEBI": "phoneshacked",
    "VIGIL": "diminishedrealitymode",
    "ZOFIA": "concussiongrenade_detonate"
}
"""
#  DEPRECATED - use OperatorInfo.statistic_name
#  used in /players.py => get_all_operators(), unused tho
OperatorStatisticNames = {
    "DOC": "Teammates Revived",
    "TWITCH": "Gadgets Destroyed With Shock Drone",
    "ASH": "Walls Breached",
    "THERMITE": "Reinforcements Breached",
    "BLITZ": "Enemies Flashed",
    "BUCK": "Shotgun Kills",
    "HIBANA": "Projectiles Detonated",
    "KAPKAN": "Boobytrap Kills",
    "PULSE": "Heartbeat Spots",
    "CASTLE": "Barricades Deployed",
    "ROOK": "Armor Taken",
    "BANDIT": "Battery Kills",
    "SMOKE": "Poison Gas Kills",
    "FROST": "DBNOs From Traps",
    "VALKYRIE": "Cameras Deployed",
    "TACHANKA": "Turret Kills",
    "GLAZ": "Sniper Kills",
    "FUZE": "Cluster Charge Kills",
    "SLEDGE": "Hammer Holes",
    "MONTAGNE": "Damage Blocked",
    "MUTE": "Gadgets Jammed",
    "ECHO": "Enemies Sonic Bursted",
    "THATCHER": "Gadgets Destroyed",
    "CAPITAO": "Lethal Dart Kills",
    "IQ": "Gadgets Spotted",
    "BLACKBEARD": "Damage Blocked",
    "JAGER": "Projectiles Destroyed",
    "CAVEIRA": "Interrogations",
    "JACKAL": "Footprint Scan Assists",
    "MIRA": "Black Mirrors Deployed",
    "LESION": "Enemies poisoned by Gu mines",
    "YING": "Candela devices detonated",
    "ELA": "Grzmot Mines Detonated",
    "DOKKAEBI": "Phones Hacked",
    "VIGIL": "Drones Deceived",
    "ZOFIA": "Concussion Grenades Detonated",
    "FINKA": "Nano-boosts used",
    "LION": "Enemies revealed",
    "ALIBI": "Enemies pinged by decoys",
    "MAESTRO": "Enemies spotted with turret camera",
    "MAVERICK": "D.I.Y. Blowtorch",
    "CLASH": "CCE Shield",
    "NOMAD": "No statistic available",
    "KAID": "No statistic available",
    "MOZZIE": "Drones Hacked",
    "GRIDLOCK": "Trax Deployed",
    "WARDEN": "Flashes Resisted",
    "NOKK": "Observation tools deceived",
    "AMARU": "Distance Reeled",
    "GOYO": "Volcans Detonated",
    "KALI": "Gadgets destroyed with explosive lance",
    "WAMAI": "Gadgets destroyed by magnet",
    "IANA": "Kills after using replicator",
    "ORYX": "kills after dash",
    "ACE": "S.E.L.M.A. Detonations",
    "MELUSI": "Attackers slowed by Banshee",
    "ZERO": "Gadgets Destroyed by ARGUS Camera",
    "ARUNI": "Surya Gates Deployed"
}


def get_from_operators_const(name, what):
    for op in operators_const:
        if op['name'] == name:
            return op[what]
    return "????"



class Operator:
    """Contains information about an operator

    Attributes
    ----------
    name : str
        the name of the operator
    wins : int
        the number of wins the player has on this operator
    losses : int
        the number of losses the player has on this operator
    kills : int
        the number of kills the player has on this operator
    deaths : int
        the number of deaths the player has on this operator
    headshots : int
        the number of headshots the player has on this operator
    melees : int
        the number of melee kills the player has on this operator
    dbnos : int
        the number of DBNO (down-but-not-out)'s the player has on this operator
    xp : int
        the total amount of xp the player has on this operator
    time_played : int
        the amount of time the player has played this operator for in seconds
    statistic : int
        the value for this operators unique statistic (depreciated in favour of unique_stats)
    statistic_name : str
        the human-friendly name for this operators statistic (depreciated in favour of unique_stats)
    unique_stats : dict[:class:`UniqueOperatorStat`, int]
        mapping of an operator's unique stat to number of times that stat has been achieved (e.g. kills with a gadget)
    """
    def __init__(self, name, stats=None, unique_stats=None):
        nl = name.lower()
        self.name = nl
        self.readable = get_from_operators_const(nl, 'readable')

        stats = stats or {}
        self.wins = stats.get("roundwon", 0)
        self.losses = stats.get("roundlost", 0)
        self.kills = stats.get("kills", 0)
        self.deaths = stats.get("death", 0)
        self.headshots = stats.get("headshot", 0)
        self.melees = stats.get("meleekills", 0)
        self.dbnos = stats.get("dbno", 0)
        self.xp = stats.get("totalxp", 0)
        self.time_played = stats.get("timeplayed", 0)
        self.atkdef = get_from_operators_const(nl, 'side')
        self.icon = get_from_operators_const(nl, 'icon_url')

        if unique_stats is not None:
            self.unique_stats = unique_stats
        else:
            self.unique_stats = {}


    def print_all_stats(self):
        print(f'name -> {self.name}')
        print(f'readable -> {self.readable}')
        print(f'wins -> {self.wins}')
        print(f'losses -> {self.losses}')
        print(f'kills -> {self.kills}')
        print(f'deaths -> {self.deaths}')
        print(f'headshots -> {self.headshots}')
        print(f'melees -> {self.melees}')
        print(f'dbnos -> {self.dbnos}')
        print(f'xp -> {self.xp}')
        print(f'time_played -> {self.time_played}')
        print(f'atkdef -> {self.atkdef}')
        print(f'icon -> {self.icon}')
        print(f'unique_stats -> {self.unique_stats}')


    def get_array(self):
        return {
            'name':self.name,
            'readable':self.readable,
            'wins':self.wins,
            'losses':self.losses,
            'kills':self.kills,
            'deaths':self.deaths,
            'headshots':self.headshots,
            'melees':self.melees,
            'dbnos':self.dbnos,
            'xp':self.xp,
            'time_played':self.time_played,
            'atkdef':self.atkdef,
            'icon':self.icon,
            'unique_stats':self.unique_stats,
        }


    @property
    def statistic(self):
        # get the first unique statistic `stat`, e.g. the number of kills using a gadget
        stat = _first_key(self.unique_stats)
        if stat is None:
            return 0
        else:
            return self.unique_stats[stat]

    @property
    def statistic_name(self):
        # get the first unique statistic `stat`, e.g. the number of kills using a gadget
        stat = _first_key(self.unique_stats)
        if stat is not None:
            return stat.name
        else:
            return None


def _first_key(d):
    """Gets the first inserted key of a dictionary. Returns None if empty"""
    return next(iter(d), None)
