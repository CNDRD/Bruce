import numpy as np


def get_cicina_today(today: None | dict[dict[str: int | str]], today_date: str) -> None | list[dict[str: int]]:
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


def get_random_cicina() -> int:
    return np.random.randint(0, 51)
