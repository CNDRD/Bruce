def ordinal(n) -> str:
    return "%d%s" % (n, "tsnrhtdd"[(n / 10 % 10 != 1) * (n % 10 < 4) * n % 10::4])
# https://stackoverflow.com/a/20007730


def add_spaces(numero: int, char: str = " ") -> str:
    return f"{numero:,}".replace(",", char)


def user_has_role(ctx, role_check) -> bool:
    roles = ctx.author.roles
    for a in roles:
        if a.id == role_check:
            return True
    return False


def hex_to_hsv(h):
    rgb_tuple = tuple(int(h.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
    return rgb_to_hsv(*rgb_tuple)


def rgb_to_hsv(r, g, b):
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    mx = max(r, g, b)
    mn = min(r, g, b)
    df = mx - mn
    if mx == mn:
        h = 0
    elif mx == r:
        h = (60 * ((g - b) / df) + 360) % 360
    elif mx == g:
        h = (60 * ((b - r) / df) + 120) % 360
    elif mx == b:
        h = (60 * ((r - g) / df) + 240) % 360
    if mx == 0:
        s = 0
    else:
        s = (df / mx) * 100
    v = mx * 100
    return int(h), int(s), int(v)
