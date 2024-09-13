from __future__ import annotations
import random
from itertools import product
from dataclasses import dataclass
from time import time
import sys
from datetime import datetime
import os
from typing import Optional

from poker import Range # type: ignore
import compare
from compare import GameType

SHORTDECK_VALS = '6789TJQKA'
HOLDEM_VALS = '2345' + SHORTDECK_VALS

gametype: Optional[GameType] = None

@dataclass
class Card:
    val: str
    suit: str

    def __str__(self) -> str:
        return self.val + self.suit

    def __hash__(self):
        return hash((self.val, self.suit))

@dataclass
class Hand:
    card1: Card
    card2: Card

    def is_stronger(self, other: Hand, comm_cards: list[Card]) -> bool | None:
        cards_str = f"{str(self)} {str(other)} {''.join(str(card) for card in comm_cards)}"
        return compare.is_first_hand_better(cards_str)

    def hand_type(self) -> str:
        as_str = str(self)
        hand_type = as_str[0] + as_str[2]
        if as_str[0] != as_str[2]:
            hand_type += 's' if as_str[1] == as_str[3] else 'o'
        return hand_type

    def __str__(self) -> str:
        return str(self.card1) + str(self.card2)

    def __hash__(self):
        return hash({self.card1, self.card2})

@dataclass
class EV:
    hand: Hand
    pots_won: float = 0
    hands_played: int = 0

    def update(self, amount_of_pot_won: float) -> None:
        self.pots_won += amount_of_pot_won
        self.hands_played += 1

    def ev(self) -> float:
        """Returns EV as a percentage of the pot"""
        return round(self.pots_won / self.hands_played * 100, 3)

    def __str__(self) -> str:
        return f"{self.hand.hand_type()} wins {self.ev()}% of the pot on avg"

def run_sim(hand: Hand, num_opps: int) -> EV:
    assert isinstance(gametype, GameType)
    card_vals = SHORTDECK_VALS if gametype in (
        GameType.SHORTDECK, GameType.SHORTDECK_TRIPS
    ) else HOLDEM_VALS
    all_cards = {Card(*x) for x in product(card_vals, 'shdc')} - {hand.card1, hand.card2}
    ev = EV(hand)
    num_trials = 100000
    for i in range(num_trials):
        if i % 50000 == 0 and i > 0:
            print(f"EV: {str(ev)}")
        rem_cards = all_cards
        opp_hands: list[Hand] = []
        for i in range(num_opps):
            opp_hand = Hand(*random.sample(list(rem_cards), 2))
            rem_cards = rem_cards - {opp_hand.card1, opp_hand.card2}
            opp_hands.append(opp_hand)
        comm_cards = random.sample(list(rem_cards), 5)
        best_hands = [hand]
        for opp_hand in opp_hands:
            if hand != best_hands[0]:
                break
            new_hand_btr = opp_hand.is_stronger(best_hands[0], comm_cards)
            if new_hand_btr:
                best_hands = [opp_hand]
            elif new_hand_btr is None:
                best_hands.append(opp_hand)
        ev.update(1 / len(best_hands) if best_hands[0] == hand else 0)
    return ev

def write_EVs_to_file(filename: str, evs: list[EV], trailing_msg: str = '') -> None:
    """Any existing contents in the file will be overwritten; `trailing_msg` will be added
       at the end of each line."""
    with open(filename, 'w') as f:
        for i, ev in enumerate(evs):
            f.write(f"#{i+1}: {str(ev)}{trailing_msg}\n")

def main() -> None:
    global gametype
    gametype = (GameType.TEXAS if len(sys.argv) < 3 else
                GameType.SHORTDECK if sys.argv[2] == 'shortdeck' else
                GameType.SHORTDECK_TRIPS if sys.argv[2] in ('shortdeck_trips', 'shortdeck_v') else
                None)
    assert isinstance(gametype, GameType)
    compare.set_gametype(gametype)
    preflop_types = Range('XX').to_ascii().split() # all types of suited/offsuit preflop hands
    if gametype in (GameType.SHORTDECK, GameType.SHORTDECK_TRIPS):
        preflop_types = [h for h in preflop_types if all(v not in h for v in '2345')]
    min_opps, max_opps = int((my_split := sys.argv[1].split('-'))[0]), int(my_split[-1])
    for num_opps in range(min_opps, max_opps+1):
        results: list[EV] = []
        filename = (datetime.today().strftime('%b %d %Y').replace(' 0', ' ') +
                    f"/preflop odds vs {num_opps} opps in {gametype.value} - {round(time())}.txt")
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        for i, hand_type in enumerate(preflop_types):
            print(f'Ran simulations for {i} out of {len(preflop_types)} starting hand types')
            print(f"Running simulation for {hand_type} vs {num_opps} opps")
            suit1, suit2 = 'd', ('d' if hand_type.endswith('s') else 'h')
            val1, val2 = hand_type[:2]
            hand = Hand(Card(val1, suit1), Card(val2, suit2))
            results.append(run_sim(hand, num_opps))
            results.sort(key=lambda ev: ev.ev(), reverse=True)
            write_EVs_to_file(filename, results, f" vs {num_opps} opps")

if __name__ == '__main__':
    main()