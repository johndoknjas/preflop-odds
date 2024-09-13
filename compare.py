# Written by Tyler Fisher, 20 Feb 2017, and modifications made by myself. For his original, see here:
# https://github.com/tylerjustinfisher/poker-hand-comparator/blob/f17df6dc9466e890eea51053c648578c923b8b37/heads%20up/handComparator_code-golf.py

from __future__ import annotations

from enum import Enum, auto
from typing import Optional
import itertools

class GameType(Enum):
    TEXAS = auto()
    SHORTDECK = auto()
    SHORTDECK_TRIPS = auto()

_ranks = {}
_num_card_vals: Optional[int] = None

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
        return h1[5] > h2[5]  # different ranks
    if h1[5] == 8 or h1[5] == rank('straight'):
        # SF or straight: check middle card
        return h1[2] > h2[2] if h1[2] != h2[2] else None
    if h1[5] == rank('flush') or h1[5] == 0:  # flush or high card: check all five cards
        for wooper in range(4, -1, -1):
            if h1[wooper] != h2[wooper]:
                return h1[wooper] > h2[wooper]
        return None  # chop
    # The hands must be either quads, trips, full house, two pair, or one pair.
    for scromp in range(6, 10):
        if h1[scromp] != h2[scromp]:
            return h1[scromp] > h2[scromp]  # one is higher, so that one wins
        if scromp + 1 == len(h1):
            return None  # all were the same, so it's a chop
    assert False

def getBestFrom7(sevenCards: list[int], sevenSuits: list[int]) -> list[int]:
    """Given 7 cards, call the 5-card comparator on each of the 21 possible combos."""
    bestHandRank = None
    for comb_5 in itertools.combinations(zip(sevenCards, sevenSuits), 5):
        newHandCards, newHandSuits = zip(*comb_5)
        newHandRank = getHandRankFromFiveCards(sorted(newHandCards), newHandSuits)
        if bestHandRank is None or first7HandIsBetter(newHandRank, bestHandRank):
            bestHandRank = newHandRank
    assert bestHandRank
    return bestHandRank

def getHandRankFromFiveCards(fC: list[int], fS: list[int] | tuple[int, int, int, int, int]):
    """`fC` contains the five values (should already be sorted) and `fS` contains the five suits."""
    # given 5 cards, determine what the rank of the hand is and add kicker info to it
    if fS.count(fS[0]) == len(fS):
        # flush, see if it's a regular flush or a straight flush
        fC.append(8 if (    (fC[0] == fC[1] - 1 == fC[2] - 2 == fC[3] - 3)
                        and (fC[4] - 1 == fC[3] or fC[4] - (num_card_vals()-1) == fC[0]))
                    else rank('flush'))
    elif ((fC[0] == fC[1] - 1 == fC[2] - 2 == fC[3] - 3) and
          (fC[4] - 1 == fC[3] or fC[4] - (num_card_vals()-1) == fC[0])):
        fC.append(rank('straight'))  # straight
    elif fC[1] == fC[2] == fC[3] and (fC[0] == fC[1] or fC[3] == fC[4]):
        fC.extend((7, fC[0], fC[4]) if fC[0] == fC[1] else (7, fC[4], fC[0])) # quads
    elif fC[0] == fC[1] == fC[2] and fC[3] == fC[4]:
        fC.extend((rank('boat'), fC[0], fC[4]))  # boat, high set full of low pair
    elif fC[0] == fC[1] and fC[2] == fC[3] == fC[4]:
        fC.extend((rank('boat'), fC[4], fC[0]))  # boat, low set full of high pair
    elif fC[0] == fC[1] == fC[2]:
        fC.extend((rank('trips'), fC[0], fC[4], fC[3]))
        # trips, both kickers higher; other kicker-types of trips in next line
    elif fC[2] == fC[3] and (fC[1] == fC[2] or fC[3] == fC[4]):
            fC.extend((rank('trips'), fC[1], fC[4], fC[0]) if fC[1] == fC[2] else
                      (rank('trips'), fC[2], fC[1], fC[0]))
    elif ((fC[0] == fC[1] and (fC[2] == fC[3] or fC[3] == fC[4])) or
          (fC[1] == fC[2] and fC[3] == fC[4])):  # two pair
        if fC[0] == fC[1] and fC[2] == fC[3]:
            fC.extend((2, fC[3], fC[1], fC[4]))  # kicker higher than both pairs
        else:
            fC.extend((2, fC[4], fC[1], fC[2 if fC[0] == fC[1] and fC[3] == fC[4] else 0]))
    elif fC[0] == fC[1] or fC[1] == fC[2]:
            fC.extend((1, fC[0], fC[4], fC[3], fC[2]) if fC[0] == fC[1] else
                      (1, fC[1], fC[4], fC[3], fC[0]))
    elif fC[2] == fC[3] or fC[3] == fC[4]:
        fC.extend((1, fC[2], fC[4], fC[1], fC[0]) if fC[2] == fC[3] else (1, fC[3], fC[2], fC[1], fC[0]))
    # If we haven't appended anything, note that it's a highcard hand by appending a zero:
    return fC if len(fC) > 5 else fC + [0]

def is_first_hand_better(cards: str):
    """`cards` should be in a format like this: `KhQh AsJs 5c6dTh4dJd`"""
    cards = (cards.replace("T", ":").replace("J", ";").replace("Q", "<")
                  .replace("K", "=").replace("A", ">"))
    listOfCards = (",".join(str(ord(card)) for card in cards)).split(",")
    c = [int(item) for item in listOfCards]
    h1 = getBestFrom7(
        [c[0], c[2], c[10], c[12], c[14], c[16], c[18]],
        [c[1], c[3], c[11], c[13], c[15], c[17], c[19]],
    )
    h2 = getBestFrom7(
        [c[5], c[7], c[10], c[12], c[14], c[16], c[18]],
        [c[6], c[8], c[11], c[13], c[15], c[17], c[19]]
    )
    return first7HandIsBetter(h1, h2)
