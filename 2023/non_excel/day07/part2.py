#!/bin/env python3

import sys
import re

cardvalue = {
    '2': 2,
    '3': 3,
    '4': 4,
    '5': 5,
    '6': 6,
    '7': 7,
    '8': 8,
    '9': 9,
    'T': 10,
    'J': 11, 
    'Q': 12,
    'K': 13,
    'A': 14
}
valuecard = {v:k for k,v in cardvalue.items()}

class Hand:
    def __init__(self, cards, bid):
        self.cards = cards
        self.bid = bid
    
    def __str__(self):
        cards_str = "".join(valuecard[c] for c in self.cards)
        return f"<{cards_str} @ {self.bid:3}>"
    
    def __lt__(self, other):
        return self.strength() < other.strength()

    def cardcount(self, jokers=False):
        """
        Count the number of cards of each type, and return as a string of digits
        in falling order

        This will make it possible to process the type depending on the start of
        the string
        """

        # A stack is a set: (count, card)
        stacks = []
        # Make a working copy
        cards = self.cards.copy()

        # Pick first card each iteration, count and remove all of similar type
        while len(cards) > 0:
            card = cards[0]
            count = sum(1 for c in cards if c == card)
            cards = [c for c in cards if c != card]
            stacks.append([count,card])

        stacks.sort(
            key=lambda c: c[0],
            reverse=True
        )

        if jokers:
            joker_val = cardvalue['J']
            # The joker stack is always best to just add to the highest stack count
            # If there are no jokers, keep an extra stack of 0 jokers at the end
            jokers = ([count for count, card in stacks if card == joker_val] + [0])[0]

            # Remove jokers from stacks, but still keep a 0-sized stack of jokers
            # if there are only jokers in the stack, so it's possible to assign the
            # jokers to the highest stack
            stacks = [c for c in stacks if c[1] != joker_val] + [[0,joker_val]]

            # add jokers to first stack
            stacks[0][0] += jokers
        
        return "".join(str(count) for count,card in stacks), [card for count,card in stacks]

    def strength(self, jokers=False):
        """
        Get a numeric strengh of hte hand, so that a better hand always have a
        higher strength value.
        
        The type of the most significant part, but then add the values of the
        cards to the strength in decreasing significance
        """
        counts, cards = self.cardcount(jokers)
        
        if counts.startswith('5'): # Five of a kind
            st = 7
        elif counts.startswith('4'): # Four of a kind
            st = 6
        elif counts.startswith('32'): # Full house
            st = 5
        elif counts.startswith('31'): # Three of a kind
            st = 4
        elif counts.startswith('22'): # Two pair
            st = 3
        elif counts.startswith('21'): # One pair
            st = 2
        elif counts.startswith('1'): # High card
            st = 1
        else: # Shouldn't happen...
            st = 0

        # Add the cards
        joker_val = cardvalue['J']
        for c in self.cards:
            st *= 100

            # If having jokers, don't count if it's a joker
            if not (jokers and c == joker_val):
                st += c
        
        return st
            

class Input:
    def __init__(self, f):
        """
        Parse the input file
        
        f can be either a filename or a file-like object
        """
        if type(f) == str:
            f = open(f,"r")
        
        self.hands = []
        for line in f:
            cards, bid = line.strip().split(" ",2)
            cards = [cardvalue[c] for c in list(cards)]
            bid = int(bid)
            self.hands.append(Hand(cards, bid))

class Part1:
    def __init__(self, hands):
        self.hands = hands

    def run(self):
        ranked_hands = self.hands.copy()
        ranked_hands.sort()
        #for hand in ranked_hands:
        #    print(f"{hand} {hand.strength()}")
        return sum(c.bid * (i+1) for i,c in enumerate(ranked_hands))

class Part2:
    def __init__(self, hands):
        self.hands = hands

    def run(self):
        ranked_hands = self.hands.copy()
        ranked_hands.sort(key=lambda c: c.strength(True))
        #for hand in ranked_hands:
        #    print(f"{hand} {hand.strength()}")
        return sum(c.bid * (i+1) for i,c in enumerate(ranked_hands))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <input file>")
        sys.exit(1)

    input = Input(sys.argv[1])
    
    part1 = Part1(input.hands)
    print(f"Part1: {part1.run()}")
    
    part2 = Part2(input.hands)
    print(f"Part2: {part2.run()}")
