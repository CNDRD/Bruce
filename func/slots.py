from numpy.random import choice
from numpy import arange

r = arange(1, 10)


def get_slots() -> (int, int, int):
    return choice(r, p=probs), choice(r, p=probs), choice(r, p=probs)


def int_to_slots(i: int) -> str:
    return slots.get(i).get("e", "Wrong Number Passed")


def calc_winnings(slotters: (int, int, int), bet: int) -> int:
    for slot in slots:
        cnt = slotters.count(slot)
        if cnt == 3:
            return int(slots[slot].get(3) * bet)
        if cnt == 2:
            return int(slots[slot].get(2) * bet)
    return 0


slots = {
    1: {
        "e": "😀", "p": 0.05,
        3: 700, 2: 25
    },
    2: {
        "e": "💎", "p": 0.06,
        3: 25, 2: 10
    },
    3: {
        "e": "🤡", "p": 0.07,
        3: 10, 2: 5
    },
    4: {
        "e": "🔔", "p": 0.08,
        3: 5, 2: 3
    },
    5: {
        "e": "🍒", "p": 0.09,
        3: 3, 2: 2
    },
    6: {
        "e": "🍋", "p": 0.1,
        3: 2, 2: 1.5
    },
    7: {
        "e": "❤️", "p": 0.15,
        3: 1.5, 2: 1
    },
    8: {
        "e": "🦶", "p": 0.17,
        3: 1, 2: 0.75
    },
    9: {
        "e": "💩", "p": 0.23,
        3: 0.75, 2: 0.5
    }
}

probs = [slots[s].get("p") for s in slots]
