# Written by Tyler Fisher, 20 Feb 2017, and modifications made by myself. For his original, see here:
# https://github.com/tylerjustinfisher/poker-hand-comparator/blob/f17df6dc9466e890eea51053c648578c923b8b37/heads%20up/handComparator_code-golf.py

from __future__ import annotations

from enum import Enum
from typing import Optional
import itertools

class GameType(Enum):
    TEXAS = 'texas holdem'
    SHORTDECK = 'regular shortdeck'
    SHORTDECK_TRIPS = 'shortdeck trips variant'

_ranks = {}
_num_card_vals: Optional[int] = None
_mapping = str.maketrans("TJQKA", ":;<=>")

def set_gametype(gametype: GameType):
    global _ranks, _num_card_vals
    _ranks['boat'], _ranks['flush'], _ranks['straight'], _ranks['trips'] = 6, 5, 4, 3
    _num_card_vals = 13
    if gametype in (GameType.SHORTDECK, GameType.SHORTDECK_TRIPS):
        _num_card_vals = 9
        _ranks['boat'], _ranks['flush'] = _ranks['flush'], _ranks['boat']
        if gametype == GameType.SHORTDECK_TRIPS:
            _ranks['straight'], _ranks['trips'] = _ranks['trips'], _ranks['straight']

def rank(hand_type: str) -> int:
    return _ranks[hand_type]

def num_card_vals() -> int:
    assert _num_card_vals is not None
    return _num_card_vals

def first7HandIsBetter(h1: list[int], h2: list[int]) -> bool | None:
    # given two hands, with the 5 cards + rank + relevant kicker details, say which wins
    if h1[5] != h2[5]:
        return h1[5] > h2[5] # different ranks
    if h1[5] in (rank('straight'), 8):
        # SF or straight: check middle card, and if needed check if an ace is actually the low card
        return h1[2] > h2[2] if h1[2] != h2[2] else h1[4] < h2[4] if h1[4] != h2[4] else None
    if h1[5] in (0, rank('flush')): # flush or high card: check all five cards
        return next((h1[i] > h2[i] for i in (4,3,2,1,0) if h1[i] != h2[i]), None)
    # The hands must both be one of quads, trips, boat, two pair, or one pair:
    assert 8 <= len(h1) == len(h2) <= 10
    return next((h1[i] > h2[i] for i in range(6, len(h1)) if h1[i] != h2[i]), None)

def getBestFrom7(sevenCards: tuple[int, ...], sevenSuits: tuple[int, ...]) -> list[int]:
    """Given 7 cards, call the 5-card comparator on each of the 21 possible combos."""
    bestHandRank = None
    for comb_5 in itertools.combinations(sorted(zip(sevenCards, sevenSuits), key=lambda t: t[0]), 5):
        newHandRank = getHandRankFromFiveCards(
            [t[0] for t in comb_5], all(comb_5[0][1] == t[1] for t in comb_5)
        )
        if bestHandRank is None or first7HandIsBetter(newHandRank, bestHandRank):
            bestHandRank = newHandRank
    assert bestHandRank
    return bestHandRank

def getHandRankFromFiveCards(fC: list[int], all_same_suit: bool):
    """`fC` contains the five values (should already be sorted) and `fS` contains the five suits."""
    # given 5 cards, determine what the rank of the hand is and add kicker info to it
    if all_same_suit:
        # flush, see if it's a regular flush or a straight flush
        fC.append(8 if (    all(fC[0] == fC[i] - i for i in (1,2,3))
                        and (fC[4] - 1 == fC[3] or fC[4] - (num_card_vals()-1) == fC[0]))
                    else rank('flush'))
    elif (all(fC[0] == fC[i] - i for i in (1,2,3)) and
          (fC[4] - 1 == fC[3] or fC[4] - (num_card_vals()-1) == fC[0])):
        fC.append(rank('straight'))  # straight
    elif fC[1] == fC[3] in (fC[0], fC[4]):
        fC.extend((7, fC[0], fC[4]) if fC[0] == fC[1] else (7, fC[4], fC[0])) # quads
    elif fC[0] == fC[2] and fC[3] == fC[4]:
        fC.extend((rank('boat'), fC[0], fC[4]))  # boat, high set full of low pair
    elif fC[0] == fC[1] and fC[2] == fC[4]:
        fC.extend((rank('boat'), fC[4], fC[0]))  # boat, low set full of high pair
    elif fC[0] == fC[2]:
        fC.extend((rank('trips'), fC[0], fC[4], fC[3]))
        # trips, both kickers higher; other kicker-types of trips in next line
    elif fC[2] == fC[3] in (fC[1], fC[4]):
        fC.append(rank('trips'))
        fC.extend((fC[1], fC[4], fC[0]) if fC[1] == fC[2] else (fC[2], fC[1], fC[0]))
    elif ((fC[0] == fC[1] and fC[3] in (fC[2], fC[4])) or
          (fC[1] == fC[2] and fC[3] == fC[4])):  # two pair
        if fC[0] == fC[1] and fC[2] == fC[3]:
            fC.extend((2, fC[3], fC[1], fC[4]))  # kicker higher than both pairs
        else:
            fC.extend((2, fC[4], fC[1], fC[2 if fC[0] == fC[1] and fC[3] == fC[4] else 0]))
    elif fC[1] in (fC[0], fC[2]):
        fC.extend((1, fC[0], fC[4], fC[3], fC[2]) if fC[0] == fC[1] else (1, fC[1], fC[4], fC[3], fC[0]))
    elif fC[3] in (fC[2], fC[4]):
        fC.extend((1, fC[2], fC[4], fC[1], fC[0]) if fC[2] == fC[3] else (1, fC[3], fC[2], fC[1], fC[0]))
    # If we haven't appended anything, note that it's a highcard hand by appending a zero:
    return fC if len(fC) > 5 else fC + [0]

def is_first_hand_better(cards: str):
    """`cards` should be in a format like this: `KhQh AsJs 5c6dTh4dJd`"""
    groups = tuple(tuple(ord(card) for card in section.translate(_mapping)) for section in cards.split())
    assert len(groups) == 3 and all(len(group) % 2 == 0 for group in groups)
    comm_vals, comm_suits = groups[2][::2], groups[2][1::2]
    return first7HandIsBetter(getBestFrom7(groups[0][::2] + comm_vals, groups[0][1::2] + comm_suits),
                              getBestFrom7(groups[1][::2] + comm_vals, groups[1][1::2] + comm_suits))
