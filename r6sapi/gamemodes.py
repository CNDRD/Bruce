GamemodeNames = {
    "securearea": "Secure Area",
    "rescuehostage": "Hostage Rescue",
    "plantbomb": "Bomb"
}

class Gamemode:
    """Contains information about a gamemode

    Attributes
    ----------
    type : str
        the gamemode id
    name : str
        the human-readable name for this gamemode
    won : int
        the number of wins the player has on this gamemode
    lost : int
        the number of losses the player has on this gamemode
    played : int
        the number of games this player has played on this gamemode
    best_score : int
        the best score this player has achieved on this gamemode"""
    def __init__(self, gamemodeType, stats=None):
        self.type = gamemodeType
        self.name = GamemodeNames[self.type]

        statname = gamemodeType + "pvp_"

        stats = stats or {}
        self.best_score = stats.get(statname + "bestscore", 0)
        self.lost = stats.get(statname + "matchlost", 0)
        self.won = stats.get(statname + "matchwon", 0)
        self.played = stats.get(statname + "matchplayed", 0)

        if gamemodeType == "securearea":
            self.areas_secured = stats.get("generalpvp_servershacked", 0)
            self.areas_defended = stats.get("generalpvp_serverdefender", 0)
            self.areas_contested = stats.get("generalpvp_serveraggression", 0)
        elif gamemodeType == "rescuehostage":
            self.hostages_rescued = stats.get("generalpvp_hostagerescue", 0)
            self.hostages_defended = stats.get("generalpvp_hostagedefense", 0)

    @property
    def wins(self):
        return self.won

    @property
    def losses(self):
        return self.lost
