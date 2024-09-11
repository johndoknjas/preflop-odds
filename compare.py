# Written by Tyler Fisher, 20 Feb 2017, and adapted by myself. For his original, see here:
# https://github.com/tylerjustinfisher/poker-hand-comparator/blob/f17df6dc9466e890eea51053c648578c923b8b37/heads%20up/handComparator_code-golf.py


def first7HandIsBetter(h1: list[int], h2: list[int]) -> bool | None:
    # given two hands, with the 5 cards + rank + relevant kicker details, say which wins
    if h1[5] != h2[5]:
        return h1[5] > h2[5]  # different ranks
    if h1[5] == 8 or h1[5] == 4:
        return (
            h1[2] > h2[2] if h1[2] != h2[2] else None
        )  # SF or straight: check middle card
    if h1[5] == 5 or h1[5] == 0:  # flush or high card: check all five cards
        for wooper in range(5):
            if h1[4 - wooper] != h2[4 - wooper]:
                return h1[4 - wooper] > h2[4 - wooper]
        return None  # chop
    for scromp in range(6, 10):
        if h1[scromp] != h2[scromp]:
            return h1[scromp] > h2[scromp]  # one is higher, so that one wins
        if len(h1) == scromp + 1:
            return None  # all were the same, so it's a chop
    assert False


def getBestFrom7(sevenCards: list[int], sevenSuits: list[int]):
    # todo - see if this can be sped up, why are the i-j loops iterating 42 times and not 21.
    # given 7 cards, call the 5-card comparator on each of the 21 poss. combos
    bestHand = None
    for i in range(7):
        for j in range(i + 1, 7):
            s = []
            for k in range(7):
                if k != i and k != j:
                    s.extend([sevenCards[k], sevenSuits[k]])
            newHand = getHandRankFromFiveCards(
                sorted([s[0], s[2], s[4], s[6], s[8]]), [s[1], s[3], s[5], s[7], s[9]]
            )
            if bestHand is None or first7HandIsBetter(newHand, bestHand):
                bestHand = newHand
    assert bestHand
    return bestHand

def getHandRankFromFiveCards(fC: list[int], fS: list[int]):
    """`fC` are the five values and `fS` are the five suits"""
    # given 5 cards, determine what the rank of the hand is and add kicker info to it
    if fS.count(fS[0]) == len(fS):
        # flush, see if it's a regular flush or a straight flush
        fC.append(8 if (    (fC[0] == fC[1] - 1 == fC[2] - 2 == fC[3] - 3)
                        and (fC[4] - 1 == fC[3] or fC[4] - 12 == fC[0]))
                    else 5)
    elif ((fC[0] == fC[1] - 1 == fC[2] - 2 == fC[3] - 3) and
          (fC[4] - 1 == fC[3] or fC[4] - 12 == fC[0])):
        fC.append(4)  # straight
    elif fC[1] == fC[2] == fC[3] and (fC[0] == fC[1] or fC[3] == fC[4]):
        fC.extend((7, fC[0], fC[4]) if fC[0] == fC[1] else (7, fC[4], fC[0])) # quads
    elif fC[0] == fC[1] == fC[2] and fC[3] == fC[4]:
        fC.extend((6, fC[0], fC[4]))  # boat, high set full of low pair
    elif fC[0] == fC[1] and fC[2] == fC[3] == fC[4]:
        fC.extend((6, fC[4], fC[0]))  # boat, low set full of high pair
    elif fC[0] == fC[1] == fC[2]:
        fC.extend((3, fC[0], fC[4], fC[3]))
        # trips, both kickers higher; other kicker-types of trips in next line
    elif fC[2] == fC[3] and (fC[1] == fC[2] or fC[3] == fC[4]):
            fC.extend((3, fC[1], fC[4], fC[0]) if fC[1] == fC[2] else (3, fC[2], fC[1], fC[0]))
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
    return fC if len(fC) > 5 else fC + [0]
    # return hand, but first if we haven't appended anything else note that it's just a high card hand

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
        [c[6], c[8], c[11], c[13], c[15], c[17], c[19]],
    )
    return first7HandIsBetter(h1, h2)
