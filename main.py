from __future__ import annotations
import random
from itertools import product, combinations_with_replacement, combinations, permutations, chain
from dataclasses import dataclass
from time import time
import sys
from datetime import datetime
import os
from typing import Iterable
from functools import cmp_to_key

import compare
from compare import GameType, gametype, num_hole_cards
import Utils

SHORTDECK_VALS = '6789TJQKA'
HOLDEM_VALS = '2345' + SHORTDECK_VALS
# HOLDEM_VALS seems to be used most of the time with [::-1], so maybe reverse the order of the values
# here, and might as well for SHORTDECK_VALS as well.
SUITS = 'shdc'
# todo - use an enum for SUITS?

def card_val_key(card: str | Card) -> int:
    """The greater the card val is, the lesser the int that'll be returned.
       `card` can be a `Card` object, or a str (with or without a suit char)."""
    if isinstance(card, Card):
        card = card.val
    card = card[0] # in case `card` was passed in as a string with a suit
    return -HOLDEM_VALS.index(card)

def cmp_group(g1: str, g2: str) -> int:
    for i in range(min(len(g1), len(g2))):
        first, second = card_val_key(g1[i]), card_val_key(g2[i])
        if first < second:
            return -1
        if second < first:
            return 1
    return -1 if len(g1) > len(g2) else 1 if len(g1) < len(g2) else 0

# todo - replace HandType4 class with this one
# Will have to check whether users of the class will rely on any specific orders of cards,
# and if so whether it aligns with what the class does now.
class OmahaSuitType:
    group_key = cmp_to_key(cmp_group)
    def __init__(self, *card_groupsP: Iterable[str] | str):
        """Each argument should contain card vals that should be of the same suit as each other,
           and of a different suit to all other groups in `cards`."""
        self.card_groups = tuple(
            sorted((''.join(sorted(g, key=card_val_key)) for g in card_groupsP), key=OmahaSuitType.group_key)
        )

    def generate_concrete_hand(self) -> list[Card]:
        assert self.well_formed()
        return sorted(
            (Card(card_val, SUITS[i]) for i, suit_group in enumerate(self.card_groups)
                                      for card_val in suit_group), key=card_val_key
        )

    def well_formed(self) -> bool:
        return (sum(len(group) for group in self.card_groups) == 4 and
                all(len(group) == len(set(group)) for group in self.card_groups))

    def __eq__(self, other) -> bool:
        assert isinstance(other, OmahaSuitType) and self.well_formed() and other.well_formed()
        return self.card_groups == other.card_groups

    def __hash__(self):
        assert self.well_formed()
        return hash(self.card_groups)

    def __str__(self) -> str:
        assert self.well_formed()
        return '.'.join(self.card_groups)

    @staticmethod
    def all_hand_types() -> list[OmahaSuitType]:
        card_vals = HOLDEM_VALS[::-1]
        objects: list[OmahaSuitType] = []
        for comb in combinations_with_replacement(card_vals, 4):
            first_2, evens, beg_end, mid_2, odds, last_2 = combinations(comb, 2)
            objects.extend(chain(
                (OmahaSuitType(comb),),
                (OmahaSuitType(comb[:x], comb[x:]) for x in (1,2,3)),
                (OmahaSuitType(x, *y) for x,y in permutations((first_2, last_2))),
                (OmahaSuitType((comb[0], comb[x], comb[3]), comb[y]) for x,y in ((1,2), (2,1))),
                (OmahaSuitType(*x, *y) for x,y in chain(product((evens, [evens]), (odds, [odds])),
                                                        product(([beg_end], beg_end), ([mid_2], mid_2))))
            ))
        objects = list(set(o for o in objects if o.well_formed()))
        assert len(objects) == 16432
        return objects

@dataclass
class Card:
    val: str
    suit: str
    # todo - override dataclass' default __lt__ and/or __gt__
    # (e.g., for sorting a list of Cards or comparing two Cards for >= value).

    def __str__(self) -> str:
        return self.val + self.suit

    def __hash__(self):
        return hash((self.val, self.suit))

@dataclass
class EV:
    # todo - make it optional to set a hand_type - if None, just assert False in __str__ in case it's called.
    # also, update class so that it keeps track of #wins, #losses, and #splits. The #wins is diff
    # from `pots_won`, it'd be the number of full pots won. User may just be interested in this info.
    hand_type: HandType2Cards | HandType4Cards
    pots_won: float = 0
    hands_played: int = 0

    def update(self, amount_of_pot_won: float) -> None:
        self.pots_won += amount_of_pot_won
        self.hands_played += 1

    def ev(self) -> float:
        """Returns EV as a percentage of the pot"""
        return round(self.pots_won / self.hands_played * 100, 3)

    def __str__(self) -> str:
        return f"{self.hand_type} wins {self.ev()}% of the pot on avg"

@dataclass
class HandType2Cards:
    card1_val: str
    card2_val: str
    suited: bool
    # todo - enforce that card1_val has a higher value than card2_val?

    def generate_concrete_hand(self) -> list[Card]:
        """Returns a list of `Card`s that matches the requirements"""
        return [Card(self.card1_val, 'd'), Card(self.card2_val, ('d' if self.suited else 'h'))]

    def __post_init__(self) -> None:
        assert self.card1_val != self.card2_val or not self.suited

    def __str__(self) -> str:
        return (self.card1_val + self.card2_val +
                ('' if self.card1_val == self.card2_val else 's' if self.suited else 'o'))

    @staticmethod
    def all_hand_types() -> list[HandType2Cards]:
        card_vals = (SHORTDECK_VALS if gametype() in (
            GameType.SHORTDECK, GameType.SHORTDECK_TRIPS
        ) else HOLDEM_VALS)[::-1]
        hand_types: list[HandType2Cards] = []
        for card1_val, card2_val in combinations_with_replacement(card_vals, 2):
            hand_types.append(HandType2Cards(card1_val, card2_val, False))
            if card1_val != card2_val:
                hand_types.append(HandType2Cards(card1_val, card2_val, True))
        return hand_types

class HandType4Cards:
    def __init__(self, card_vals: tuple[str,str,str,str]):
        # todo - enforce that the card vals are in order of value?
        # also, consider adding a param that says double suited, rainbow, single suited, random, etc.
        self._card_vals = card_vals
        self._possible_cards = [[Card(card_val, s) for s in SUITS] for card_val in card_vals]

    def generate_concrete_hand(self) -> list[Card]:
        hand: list[Card] = []
        for options in self._possible_cards:
            while (pick := random.choice(options)) in hand:
                pass
            hand.append(pick)
        return hand

    def __str__(self) -> str:
        return ''.join(val for val in self._card_vals)

    def __eq__(self, other) -> bool:
        return isinstance(other, HandType4Cards) and self._card_vals == other._card_vals

    @staticmethod
    def all_hand_types() -> list[HandType4Cards]:
        card_vals = (SHORTDECK_VALS if gametype() in (
            GameType.SHORTDECK, GameType.SHORTDECK_TRIPS
        ) else HOLDEM_VALS)[::-1]
        return [HandType4Cards(comb) for comb in combinations_with_replacement(card_vals, 4)]

def cards_as_str(cards: list[Card]) -> str:
    """Used for debugging"""
    return ' '.join(str(card) for card in sorted(cards, key=card_val_key))

def run_sim(hand_type: HandType2Cards | HandType4Cards, num_opps: int, debug: bool = False) -> EV:
    # todo - update so that the sim is run for num_opps and all positive ints less than it as well.
    # Just saves a bunch of time.
    CARD_VALS = SHORTDECK_VALS if gametype() in (
        GameType.SHORTDECK, GameType.SHORTDECK_TRIPS
    ) else HOLDEM_VALS
    ALL_CARDS = {Card(*x) for x in product(CARD_VALS, SUITS)}
    ev = EV(hand_type)
    num_trials = 100000
    for i in range(num_trials):
        assert len(ALL_CARDS) == 52
        hand = hand_type.generate_concrete_hand()
        rem_cards = ALL_CARDS - {*hand}
        assert len(rem_cards) == 52 - num_hole_cards()
        if i % 50000 == 0 and i > 0:
            print(f"EV: {str(ev)}")
        opp_hands: list[list[Card]] = []
        for _ in range(num_opps):
            opp_hand = random.sample(list(rem_cards), num_hole_cards())
            rem_cards -= {*opp_hand}
            opp_hands.append(opp_hand)
        assert len(rem_cards) == 52 - num_hole_cards() * (num_opps + 1)
        comm_cards = random.sample(list(rem_cards), 5)
        best_hands = [hand]
        for opp_hand in opp_hands:
            if hand != best_hands[0]:
                break
            new_hand_btr = compare.is_first_hand_better(''.join(str(x) for x in opp_hand) + ' ' +
                ''.join(str(x) for x in best_hands[0]) + ' ' + ''.join(str(x) for x in comm_cards))
            if new_hand_btr:
                best_hands = [opp_hand]
            elif new_hand_btr is None:
                best_hands.append(opp_hand)
            if debug:
                print(f'Result: {new_hand_btr}\nhand: {cards_as_str(hand)}\nopp: {cards_as_str(opp_hand)}')
                print(f"Community:\n{cards_as_str(comm_cards)}\n")
        ev.update(1 / len(best_hands) if best_hands[0] == hand else 0)
    return ev

def write_EVs_to_file(filename: str, evs: list[EV], trailing_msg: str = '') -> None:
    """Any existing contents in the file will be overwritten; `trailing_msg` will be added
       at the end of each line."""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as f:
        for i, ev in enumerate(evs):
            f.write(f"#{i+1}: {str(ev)}{trailing_msg}\n")

def main() -> None:
    Utils.pypy_notice()
    chosen_gametype = (GameType.SHORTDECK if 'shortdeck' in sys.argv else
                       GameType.SHORTDECK_TRIPS if 'shortdeck_v' in sys.argv else
                       GameType.OMAHA if 'omaha' in sys.argv else
                       GameType.TEXAS)
    compare.set_gametype(chosen_gametype)
    preflop_types = HandType4Cards.all_hand_types() if gametype() == GameType.OMAHA else HandType2Cards.all_hand_types()
    # todo - make it so that the user can do something like x/y, where x and y are integers up to them.
    # will compute that fraction of the preflop_types
    rough_halfway_idx = len(preflop_types) // 2
    rough_quarter_idx = len(preflop_types) // 4
    rough_three_quarter_idx = rough_halfway_idx + rough_quarter_idx
    if '/' in sys.argv:
        preflop_types = preflop_types[:rough_quarter_idx]
    elif '//' in sys.argv:
        preflop_types = preflop_types[rough_quarter_idx:rough_halfway_idx]
    elif '///' in sys.argv:
        preflop_types = preflop_types[rough_halfway_idx:rough_three_quarter_idx]
    elif '////' in sys.argv:
        preflop_types = preflop_types[rough_three_quarter_idx:]

    min_opps, max_opps = int((my_split := sys.argv[1].split('-'))[0]), int(my_split[-1])
    for num_opps in range(min_opps, max_opps+1):
        results: list[EV] = []
        filename = (datetime.today().strftime('%b %d %Y').replace(' 0', ' ') +
                    f"/preflop odds vs {num_opps} opps in {gametype().value} - {round(time())}.txt")
        for i, hand_type in enumerate(preflop_types): # type: ignore
            print(f'Ran simulations for {i} out of {len(preflop_types)} starting hand types') # type: ignore
            print(f"Running simulation for {hand_type} vs {num_opps} opps")
            results.append(run_sim(hand_type, num_opps))
            results.sort(key=lambda ev: ev.ev(), reverse=True)
        write_EVs_to_file(filename, results, f" vs {num_opps} opps")

if __name__ == '__main__':
    main()