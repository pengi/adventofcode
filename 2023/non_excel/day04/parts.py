#!/bin/env python3

import sys
import re

class Card:
    def __init__(self, id, win, own):
        self.id = id
        self.win = win
        self.own = own
    
    def get_matches(self):
        return len(set(self.own).intersection(set(self.win)))
    
    def get_value(self):
        return (1<<self.get_matches())>>1

class Input:
    def __init__(self, f):
        """
        Parse the input file
        
        f can be either a filename or a file-like object
        """
        if type(f) == str:
            f = open(f,"r")
        
        self.cards = []
        for line in f:
            id_str, win_str, own_str = re.match(r"^Card *([0-9]+): ([0-9 ]*) \| ([0-9 ]*)$", line).groups()
            id = int(id_str)
            win = [int(c) for c in win_str.split(" ") if c != ""]
            own = [int(c) for c in own_str.split(" ") if c != ""]
            self.cards.append(Card(id, win, own))

class Part1:
    def __init__(self, cards):
        self.cards = cards

    def run(self):
        return sum(c.get_value() for c in self.cards)

class Part2:
    def __init__(self, cards):
        self.cards = cards

    def run(self):
        extra = []
        total_count = 0
        for c in self.cards:
            count = 1
            if len(extra) > 0:
                count += extra.pop(0)
            wins = c.get_matches()
            extra_add = [count] * wins
            total_count += count

            if len(extra_add) < len(extra):
                extra_add += [0] * (len(extra) - len(extra_add))
            if len(extra_add) > len(extra):
                extra += [0] * (len(extra_add) - len(extra))
            
            extra = [a+b for a,b in zip(extra,extra_add)]

        return total_count

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <input file>")
        sys.exit(1)

    input = Input(sys.argv[1])
    
    part1 = Part1(input.cards)
    print(f"Part1: {part1.run()}")

    part2 = Part2(input.cards)
    print(f"Part2: {part2.run()}")
