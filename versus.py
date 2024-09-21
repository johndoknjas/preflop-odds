from __future__ import annotations
from itertools import product, combinations
from time import time
import sys
import os
import re

import compare
from compare import GameType, gametype
from main import Card, HOLDEM_VALS, SUITS, EV, HandType4Cards

def sort_val(t: tuple[str, bool | None]) -> int:
    return sum((i+1) * HOLDEM_VALS[::-1].index(c) for i,c in enumerate(t[0][::-1]) if c in HOLDEM_VALS)

def main() -> None: # todo - mypy says line 22, not line 15, when type for main is removed
    hand_1_str, hand_2_str = sys.argv[1:3]
    compare.set_gametype(GameType.OMAHA)
    cards_in_play = [Card(s[i], s[i+1]) for s in (hand_1_str, hand_2_str) for i in range(0, len(s), 2)]
    REM_CARDS = {c for c in {Card(*x) for x in product(HOLDEM_VALS, SUITS)} if c not in cards_in_play}
    comm_combos = list(combinations(REM_CARDS, 5))
    print(len(comm_combos))
    results: list[tuple[str, bool | None]] = []
    ev_hand1 = EV(HandType4Cards(tuple(re.findall('..', hand_1_str))))
    print_interval = 10000
    for i, comm_cards in enumerate(comm_combos):
        if i % print_interval == 0 and i > 0:
            for result in results[i-print_interval:i]:
                print(result)
            print(f"{i} comm hands processed; current EV for hand 1 is {ev_hand1.ev()}")
            print('\n\n\n')
        comm_str = ''.join(str(x) for x in comm_cards)
        cards_str = f"{hand_1_str} {hand_2_str} {comm_str}"
        results.append((cards_str, compare.is_first_hand_better(cards_str)))
        ev_hand1.update(0.5 if results[-1][1] is None else int(results[-1][1])) # assumes only 1 opp
    results.sort(key=sort_val, reverse=True)
    filepath = f'tests/{round(time())}.txt'
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        for result in results:
            f.write(f"{result[0]}: first hand got a result of {result[1]}\n")

if __name__ == '__main__':
    main()