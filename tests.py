from copy import deepcopy
import pytest

import compare
from compare import GameType

_mapping = str.maketrans("TJQKA", ":;<=>")
_rankings: dict = {0: "high card", 1: "one pair", 2: "two pair", 3: "trips", 4: "straight",
                   5: "flush", 6: "boat", 7: "quads", 8: "straight flush"}
_rankings.update(dict(tuple(reversed(i)) for i in _rankings.items()))

random_hands: list[tuple[str, ...]] = [
     ("6dJc8c5c 7c6sAs9d Kc5sJsKdQh", "two pair", "one pair"),
     ("Th6dAh5d 2h9d5h3h 8hKh5cKcTc", "two pair", "two pair"),
     ("TdJd3h7h 9hAc6h2c Tc8s9c2hJh", "straight", "two pair"),
     ("7dTdAd8s 3c9sAc8c 6s4cKhQs2s", "high card", "high card"),
     ("9c9h7h2s 4s2hTh8h 4c6s5dAd6c", "two pair", "two pair"),
     ("6d8cTc7h 2d5c9h4d TdAsKh6c7c", "two pair", "high card"),
     ("AcAh4hJd ThQd8h2s 3cAs5dQh5c", "boat", "two pair"),
     ("QcKdTsQs Kc9s4h9d Qd4dAsAh5s", "boat", "two pair"),
     ("Ac4dJhJd 5c7d5dTh 6cJc3sQs2c", "trips", "one pair"),
     ("5dTd7d4s Ts6c9h8s AhJsQh3s2c", "straight", "high card", "high card", "high card")
]
"""2nd and 3rd elements are for the hand rank in omaha. If 4th and 5th elements exist, they are for
   games with 2 hole cards (e.g., holdem and shortdeck). For Omaha hands, it's expected that
   the better 4-card hand should come before the worse 4-card hand, in the cards string."""

def get_integer_groups(cards: str):
    groups = tuple(tuple(ord(card) for card in section.translate(_mapping)) for section in cards.split())
    return (
        (groups[0][::2], groups[0][1::2]),
        (groups[1][::2], groups[1][1::2]),
        (groups[2][::2], groups[2][1::2])
    )

def omaha_hands() -> list[tuple[str, ...]]:
    return [hand[:3] for hand in deepcopy(random_hands)]

def non_omaha_hands() -> list[tuple[str, ...]]:
    new_hands = []
    for hand in deepcopy(random_hands):
        if len(hand) < 5:
            continue
        cards = hand[0].split()
        all_new_cards = (f"{cards[0][:4]} {cards[1][:4]} {cards[2]}")
        new_hand = (all_new_cards, ) + hand[1:]
        new_hands.append(tuple(e for i,e in enumerate(new_hand) if i not in (1,2)))
    return new_hands

def assert_rankings(cards: tuple[str, ...]):
    assert len(cards) == 3
    int_groups = get_integer_groups(cards[0])
    for i in range(2):
        player_cards, player_suits = int_groups[i]
        comm_cards, comm_suits = int_groups[-1]
        rank_list = compare.getBestComb(
            player_cards, player_suits, comm_cards, comm_suits
        )
        assert _rankings[rank_list[5]] == cards[i+1]

# todo - make test for getting best 5 card hand from 7 or 9 cards.

@pytest.mark.parametrize("cards", omaha_hands())
def test_omaha_matchups(cards: tuple[str, ...]):
    compare.set_gametype(GameType.OMAHA)
    assert compare.is_first_hand_better(cards[0]) is True
    assert_rankings(cards)

@pytest.mark.parametrize("cards", non_omaha_hands())
def test_holdem_matchups(cards: tuple[str, ...]):
    compare.set_gametype(GameType.TEXAS)
    if cards[1] != cards[2]:
        # doesn't test comparing hands that have the same rank (e.g., boat vs boat)
        assert compare.is_first_hand_better(cards[0]) is (_rankings[cards[1]] > _rankings[cards[2]])
    assert_rankings(cards)