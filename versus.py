from __future__ import annotations
from itertools import product, combinations
from time import time
import sys
import os
import re

import compare
from compare import GameType
from main import Card, HOLDEM_VALS, SUITS, EV, HandType4Cards
import Utils

def write_to_file(results: list[tuple[str, bool | None]] | list[str]) -> None:
    filepath = f'tests/{round(time())}.txt'
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        for result in results:
            f.write(f"{result[0]}: first hand got a result of {result[1]}\n"
                    if isinstance(result, tuple) else f"{result}\n")

def sort_key(combo: tuple[Card, Card, Card, Card, Card]) -> tuple[int, ...]:
    return tuple(HOLDEM_VALS[::-1].index(c.val) for c in combo if c.val in HOLDEM_VALS)

def generate_stats(lines: list[str]) -> None:
    ev = EV(HandType4Cards(('A', 'A', 'A', 'A'))) # don't care about the hand type
    wins, ties, losses = 0,0,0
    for line in lines:
        ev.update(0.5 if line.endswith("None") else int(line.endswith("True")))
        if line.endswith("None"):
            ties += 1
        elif line.endswith("True"):
            wins += 1
        else:
            losses += 1
    print(f"First hand has an ev of {ev.ev()}")
    print(f"First hand won {wins / len(lines) * 100}%")
    print(f"First hand tied {ties / len(lines) * 100}%")
    print(f"First hand lost {losses / len(lines) * 100}%\n")

def main() -> None: # todo - mypy says wrong line when type for main is removed
    Utils.pypy_notice()
    if sys.argv[1] == 'trim':
        filepath = sys.argv[2]
        with open(filepath, 'r') as f:
            lines = f.read().splitlines()
        print("Before trimming: ", end='')
        generate_stats(lines)
        trimmed_lines = []
        for line in lines:
            comm = line.split()[2]
            if (all(x not in comm and (x not in ('True', 'False', 'None') or not line.endswith(x))
                    for x in sys.argv[3:]) and
                ('flush' not in sys.argv[3:] or all(comm.count(suit) < 3 for suit in SUITS))):
                trimmed_lines.append(line)
        print("After trimming: ", end='')
        generate_stats(trimmed_lines)
        if 'nowrite' not in sys.argv[3:]:
            write_to_file(trimmed_lines)
        sys.exit(0)
    hand_1_str, hand_2_str = sys.argv[1:3]
    exclude_str = sys.argv[3] if len(sys.argv) > 3 else ''
    compare.set_gametype(GameType.OMAHA)
    cards_in_play = [Card(s[i], s[i+1]) for s in (hand_1_str, hand_2_str, exclude_str)
                                        for i in range(0, len(s), 2)]
    REM_CARDS = [c for c in (Card(*x) for x in product(HOLDEM_VALS[::-1], SUITS)) if c not in cards_in_play]
    assert len(REM_CARDS) == 52 - sum(len(x) / 2 for x in (hand_1_str, hand_2_str, exclude_str))
    comm_combos = sorted(combinations(REM_CARDS, 5), key=sort_key)
    print(f"Going through {len(comm_combos)} community combos...")
    results: list[tuple[str, bool | None]] = []
    ev_hand1 = EV(HandType4Cards(tuple(re.findall('..', hand_1_str))))
    print_interval = 10000
    for i, comm_cards in enumerate(comm_combos):
        if i % print_interval == 0 and i > 0:
            for result in results[i-print_interval:i]:
                print(result)
            print(f"{i} comm hands processed; current EV for hand 1 is {ev_hand1.ev()}%\n\n\n\n")
        comm_str = ''.join(str(x) for x in comm_cards)
        cards_str = f"{hand_1_str} {hand_2_str} {comm_str}"
        results.append((cards_str, compare.is_first_hand_better(cards_str)))
        ev_hand1.update(0.5 if results[-1][1] is None else int(results[-1][1])) # assumes only 1 opp
    print(f"{i} comm hands processed; current EV for hand 1 is {ev_hand1.ev()}%\n\n\n\n")
    write_to_file(results)

if __name__ == '__main__':
    main()