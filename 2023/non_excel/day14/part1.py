#!/bin/env python3

import sys
import re

def flip(rows):
    """
    Return a flipped copy of the image, where x and y is reversed
    """
    rows = list(rows)
    cols = ["".join(row[i] for row in rows) for i in range(len(rows[0]))]
    return cols

class Input:
    def __init__(self, f):
        """
        Parse the input file
        
        f can be either a filename or a file-like object
        """
        if type(f) == str:
            f = open(f,"r")
        
        self.rows = [l.strip() for l in f.readlines() if l.strip() != ""]


class Part1:
    def __init__(self, input):
        self.rows = input.rows

    def run(self):
        cols = flip(self.rows)
        # Each column can be calculated independently
        load = 0
        for col in cols:
            # Don't need to keep track of the actual result map, but just where
            # rocks would end up
            next_slot = len(cols)
            for i,slot in enumerate(col):
                if slot == 'O':
                    load += next_slot
                    next_slot -= 1
                elif slot == '#':
                    next_slot = len(cols) - i - 1
        return load

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <input file>")
        sys.exit(1)

    input = Input(sys.argv[1])
    
    part1 = Part1(input)
    print(f"Part1: {part1.run()}")
