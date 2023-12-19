#!/bin/env python3

import sys
import re

def _flatten(xss):
    return [x for xs in xss for x in xs]

class StarLine:
    def __init__(self, counts):
        # Save the counts, but also expand the empty spaces
        self.counts = counts

    def __str__(self):
        return str(self.counts)

    def process_len(self, expansion=1):
        # Each segment contains a set of lines. The amount of lines crossing
        # each segment is quite easy to calculate; it's the number of stars to
        # the left of the segment multiplied by the number of stars to the
        # right.
        #
        # Since the width/height of the starfield scales linearly, while the
        # number of connections scales as O(n^2), it will be way faster to
        # iterate over each segment instead of each connection
        tot_len = 0
        count_left = 0
        count_right = sum(self.counts)
        for cur in self.counts:
            if cur == 0:
                tot_len += count_left * count_right * expansion
            else:
                tot_len += count_left * count_right
            count_right -= cur
            count_left += cur
        return tot_len

class Input:
    def __init__(self, f):
        """
        Parse the input file

        f can be either a filename or a file-like object
        """
        if type(f) == str:
            f = open(f,"r")

        lines = [l.strip() for l in f.readlines() if l.strip() != ""]

        # Since the puzzle itself never needs the area, but just counting x and
        # y axis independently, split it up already at the parsing stage
        counts_x = [sum(1 for c in l if c == '#') for l in lines]
        counts_y = list(map(lambda *xs: sum(xs), *[[1 if c == '#' else 0 for c in l] for l in lines]))

        # It's not important what axis it is, but just treat them indepdentently

        self.stars = [
            StarLine(counts_x),
            StarLine(counts_y)
        ]


class Part1:
    def __init__(self, input):
        self.stars = input.stars

    def run(self):
        return sum(stars.process_len(2) for stars in self.stars)

class Part2:
    def __init__(self, input):
        self.stars = input.stars

    def run(self):
        return sum(stars.process_len(1000000) for stars in self.stars)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <input file>")
        sys.exit(1)

    input = Input(sys.argv[1])

    part1 = Part1(input)
    print(f"Part1: {part1.run()}")

    part2 = Part2(input)
    print(f"Part2: {part2.run()}")
