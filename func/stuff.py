def ordinal(n) -> str:
    return "%d%s" % (n, "tsnrhtdd"[(n / 10 % 10 != 1) * (n % 10 < 4) * n % 10::4])
# https://stackoverflow.com/a/20007730
