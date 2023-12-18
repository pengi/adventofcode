#!/bin/env python3

import sys
import re
import math
from part1 import *

#
# A ghost in this case is just a periodic interval when the ghost ends up at the
# same location again, and when the first appers there.
#
# If two ghosts are on the same map, then they will end up once at the same
# location (if the puzzle input is correctly created... more on that later).
# Eventually they will end up on the same location again.
#
# The interval will then be the least common multiple between the two ghosts
# intervals, and the start time can be calculated out of the two ghosts offset
# in their interval. See Ghost.combine()
#
# Thus, analyze each ghost individually, and combine them afterwards
#
# There are two cases that this case may fail on, which apparently didn't happen
# here:
#
# Two ghosts may have be out of phase. For example two ghosts both having even
# intervals, and one only ends up on odd times while the other on even times,
# and thus never end up at the same time
#
# A ghost may iterate between two different exists, and thus have two offsets.
# Only one is counted here. This may also be that it passes over an exist before
# ending up on a cycle.
#


class Ghost:
    def __init__(self, start=0, interval=1):
        """
        Represents the times a ghost is at an end location
        
        The default ghost, created as Ghost(), will always be at an end
        location
        """
        self.start = start
        self.interval = interval
    
    def __str__(self):
        return f"({self.interval}*i + {self.start})"
    
    def combine(self, other):
        # The interval will always be the least common multiple of the two
        # ghosts interval
        interval = math.lcm(self.interval, other.interval)

        # within the interval, the time they end up at the location may be at a
        # certain offset in time
        offset = (self.start * other.interval + other.start * self.interval)%interval

        # They will not end up at the given location before the first ghosts
        # end up there. Initially, it may be a longer path
        first = max(self.start, other.start)

        # Find the first occurance of i such as:
        # interval * i + offset >= first
        #
        # wich means:
        # i >= (first - offset) // interval
        #
        # then start = interval * i + offset
    
        i = (first - offset) // interval
        while interval * i + offset < first:
            i += 1
        start = interval * i + offset

        return Ghost(start, interval)

class Part2:
    def __init__(self, input):
        self.path = input.path
        self.map = input.map

    def analyze_ghost(self, start):
        """
        Return start time and cycle time in a given map

        It tries to log which Z-nodes it passes, and if it ends up on one again,
        it will return a tuple of two values:

        1. first iteration it ends up on the node
        2. how many cycles until ending up there again
        """
        step = 0
        location = start
        visits = {}
        while not location in visits:
            if location[-1] == 'Z':
                visits[location] = step
            location = self.map.get(location, self.path.get(step))
            step += 1
        return visits[location], step-visits[location]

    def run(self):
        ghosts = []
        for loc in self.map.locations():
            if loc[-1] == 'A':
                start, interval = self.analyze_ghost(loc)
                ghosts.append((loc, Ghost(start, interval)))
        
        # Combine ghosts together, one at a time. Start with the default ghost
        cur_ghost = Ghost()
        for loc, ghost in ghosts:
            cur_ghost = cur_ghost.combine(ghost)
            print(f"{loc}: {ghost} => {cur_ghost}")
        
        return cur_ghost.start

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <input file>")
        sys.exit(1)

    input = Input(sys.argv[1])
    
    # Not all part 2 examples inputs works on part 1
    try:
        part1 = Part1(input)
        print(f"Part1: {part1.run()}")
    except:
        pass

    part2 = Part2(input)
    print(f"Part2: {part2.run()}")
