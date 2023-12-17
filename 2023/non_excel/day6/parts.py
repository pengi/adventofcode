#!/bin/env python3

import sys
import re
import math

class Input:
    def _parse_values(self, values):
        return [int(v) for v in values.split(" ") if v != ""]
    
    def __init__(self, f):
        """
        Parse the input file
        
        f can be either a filename or a file-like object
        """
        if type(f) == str:
            f = open(f,"r")
        
        self.lines = {}

        for line in f.readlines():
            [header, values] = line.split(": ", 2)
            header = header.strip()
            values = self._parse_values(values.strip())
            self.lines["var_" + header.lower()] = values
        
        # Get all keys
        keys = list(self.lines.keys())

        # Convert all input to tuples
        objs = zip(*(self.lines[k] for k in keys))

        # Combine all to dicts for processing
        self.races = [{k:obj[i] for i, k in enumerate(keys)} for obj in objs]

    def __str__(self):
        return repr(self.races)

# Part 2 uses other input parsing...
class InputPart2(Input):
    def _parse_values(self, values):
        return [int(values.replace(" ", ""))]

class Problem:
    def __init__(self, races):
        self.races = races

    def options_race(self, var_time, var_distance):

        # if holding the button for the time t, between 1 and var_time ms, the
        # distance travelled will therefore be: D = t * (var_time - t)
        #
        # A winning race is therefore D > var_distance
        #
        # So for every t such as t*(var_time-t) > var_distance is a winning
        # race:
        #
        # opts = 0
        # for t in range(1, var_time):
        #     if t*(var_time-t) > var_distance:
        #         opts += 1
        #
        # Howver, this can be rewritten to for every t such as:
        #
        # t*t - t*var_time + var_distance < 0
        #
        # The number of winning options is therefore the distance between the
        # points that solves the equestion t*t - t*var_time + var_distance = 0
        #
        # Which is: opts = 2*math.sqrt((var_time/2)**2 - var_distance)
        #
        # However, that works for an ideal world. But now t is discreete for
        # whole milliseconds. Therefore, calculate t for start and end and round
        # up/down
        #
        # t1 = var_time/2 - sqrt((var_time/2)**2 - var_distance)
        # t2 = var_time/2 + sqrt((var_time/2)**2 - var_distance)
        #
        # Due to rounding errors on float values, t1 and t2 are found by
        # iterating around t1 and t2 points, according to first formula to find
        # the first and last winning number

        t1 = int(var_time/2 - math.sqrt((var_time/2)**2 - var_distance)) - 1
        t2 = int(var_time/2 + math.sqrt((var_time/2)**2 - var_distance)) + 1

        while t1*(var_time-t1) <= var_distance and t1 < t2:
            t1 += 1

        while t2*(var_time-t2) <= var_distance and t1 < t2:
            t2 -= 1

        opts = t2 - t1 + 1
        print(f"time: {var_time:10} dist: {var_distance:20} options: {t1:3} {t2:3} {opts:4}")
        return opts

    def run(self):
        opts = 1
        for race in self.races:
            opts *= self.options_race(**race)
        return opts

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <input file>")
        sys.exit(1)
        
    print("\nPart1:\n")

    part1 = Problem(Input(sys.argv[1]).races)
    part1_result = part1.run()

    print(f"\nPart1: {part1_result}\n")

        
    print("\nPart2:\n")

    part2 = Problem(InputPart2(sys.argv[1]).races)
    part2_result = part2.run()

    print(f"\nPart2: {part2_result}\n")
