class Platforms:
    """Platforms supported

    Attributes
    ----------
    UPLAY : str
        name of the uplay platform
    XBOX : str
        name of the xbox platform
    PLAYSTATION : str
        name of the playstation platform"""

    UPLAY = "uplay"
    XBOX = "xbl"
    PLAYSTATION = "psn"


valid_platforms = [x.lower() for x in dir(Platforms) if "_" not in x]


PlatformURLNames = {
    "uplay": "OSBOR_PC_LNCH_A",
    "psn": "OSBOR_PS4_LNCH_A",
    "xbl": "OSBOR_XBOXONE_LNCH_A"
}
