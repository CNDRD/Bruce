def rank_name(num: int) -> str:
    a = (num - (num % 5))
    if num == 0:
        return "[0]"
    return f"[{a}-{a+5}]"
# https://stackoverflow.com/a/13082705


def xp_from_level(level: int) -> int:
    return int(5 / 6 * level * (2 * level * level + 27 * level + 91))


def level_from_xp(xp: int) -> int:
    for i in range(0, 100):
        if xp_from_level(i) <= xp < xp_from_level(i + 1):
            return i
