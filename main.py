import random
from itertools import product
from dataclasses import dataclass
from time import time

from poker import Range # type: ignore
from compare import is_first_hand_better

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

    def __str__(self) -> str:
        return str(self.card1) + str(self.card2)

    def __hash__(self):
        return hash({self.card1, self.card2})

def percent(numerator, denominator, round_precision) -> float:
    return round(numerator / denominator * 100, round_precision)

def odds_str(hand: Hand, wdr: list[int], num_games: int) -> str:
    hand_type = str(hand)[0] + str(hand)[2]
    if str(hand)[0] != str(hand)[2]:
        hand_type += 's' if str(hand)[1] == str(hand)[3] else 'o'
    return f"{hand_type} wins {percent(wdr[0], num_games, 3)}%, ties {percent(wdr[1], num_games, 3)}%"

def run_sim(hand: Hand) -> str:
    all_cards = {Card(x[0], x[1]) for x in product('23456789TJQKA', 'shdc')} - {hand.card1, hand.card2}
    wdr: list[int] = [0,0,0]
    num_trials = 100000
    for i in range(num_trials):
        if i % 50000 == 0 and i > 0:
            print(odds_str(hand, wdr, i))
        opp_hand = Hand(*random.sample(list(all_cards), 2))
        comm_cards = random.sample(list(all_cards - {opp_hand.card1, opp_hand.card2}), 5)
        cards_str = f"{str(hand)} {str(opp_hand)} {''.join(str(card) for card in comm_cards)}"
        first_hand_btr = is_first_hand_better(cards_str)
        if first_hand_btr is None:
            wdr[1] += 1
        elif first_hand_btr:
            wdr[0] += 1
        else:
            wdr[2] += 1
    return odds_str(hand, wdr, num_trials)

def get_wins_ties(wdr: str) -> tuple[float, float]:
    return tuple(float(s.split()[-1]) for s in wdr.split('%')[:2])

def wdr_fitness(wdr: str) -> float:
    return get_wins_ties(wdr)[0] + get_wins_ties(wdr)[1] * 0.5

def write_list_to_file(filename: str, lines: list[str], trailing_msg: str = '') -> None:
    """Any existing contents in the file will be overwritten; `trailing_msg` will be added
       at the end of each line."""
    with open(filename, 'w') as f:
        for line in lines:
            f.write(f"{line}{trailing_msg}\n")

def main():
    preflop_types = Range('XX').to_ascii().split() # all types of suited/offsuit preflop hands
    results: list[str] = []
    filename = f"preflop hands - {round(time())}.txt"
    for i, hand_type in enumerate(preflop_types):
        print(f'Ran simulations for {i} out of 169 starting hand types')
        suit1, suit2 = 'd', ('d' if hand_type.endswith('s') else 'h')
        val1, val2 = hand_type[:2]
        hand = Hand(Card(val1, suit1), Card(val2, suit2))
        results.append(run_sim(hand))
        results.sort(key=wdr_fitness, reverse=True)
        write_list_to_file(filename, results, " in heads up")

if __name__ == '__main__':
    main()