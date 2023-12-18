#!/bin/env python3

import sys
import re

cardvalue = {
    '2': 2,  '3': 3,  '4': 4,  '5': 5,
    '6': 6,  '7': 7,  '8': 8,  '9': 9,
    'T': 10, 'J': 11, 'Q': 12, 'K': 13,
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

    def cardcount(self):
        """
        Generate a tuple of two lists:
        
        First list contains the count of each type of cards, from most to least
        cards. For easier processing, return that as a string of digits 5-1.

        Second list contains the types (values) of the cards, from the order
        they appear in the first list. If two cards have the same count, then
        the most valueable appears first

        This will be useful to easily profile the the hand for which type it is
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
            stacks.append((count,card))

        stacks.sort(
            key=lambda c: c[0],
            reverse=True
        )
        
        return "".join(str(count) for count,card in stacks), [card for count,card in stacks]

    def strength(self):
        """
        Get a numeric strengh of hte hand, so that a better hand always have a
        higher strength value.
        
        The type of the most significant part, but then add the values of the
        cards to the strength in decreasing significance
        """
        counts, cards = self.cardcount()
        
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
        for c in self.cards:
            st *= 100
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

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <input file>")
        sys.exit(1)

    input = Input(sys.argv[1])
    
    part1 = Part1(input.hands)
    print(f"Part1: {part1.run()}")

    part2 = Part2(input.hands)
    print(f"Part2: {part2.run()}")
