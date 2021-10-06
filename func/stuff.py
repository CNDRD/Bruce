def ordinal(n) -> str:
    return "%d%s" % (n, "tsnrhtdd"[(n / 10 % 10 != 1) * (n % 10 < 4) * n % 10::4])
# https://stackoverflow.com/a/20007730


def add_spaces(numero) -> str:
    numero = ''.join(reversed(str(numero)))
    a = [numero[i:i + 3] for i in range(0, len(numero), 3)]
    a = ' '.join([numero[i:i + 3] for i in range(0, len(numero), 3)])
    a = ''.join(reversed(str(a)))
    return a
# https://stackoverflow.com/a/15254225/13186339


def user_has_role(ctx, role_check) -> bool:
    roles = ctx.author.roles
    for a in roles:
        if a.id == role_check:
            return True
    return False
