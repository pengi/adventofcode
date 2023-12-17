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

            self.lines = [l.strip() for l in f.readlines()]

class Part1:
    letters = {
        "0": 0,
        "1": 1,
        "2": 2,
        "3": 3,
        "4": 4,
        "5": 5,
        "6": 6,
        "7": 7,
        "8": 8,
        "9": 9
    }

    def __init__(self, lines):
        self.lines = lines
    
    def first(self, line):
        ret_idx = -1
        ret_num = None
        for word, num in self.letters.items():
            idx = line.find(word)
            if (idx >= 0 and idx < ret_idx) or ret_idx < 0:
                ret_idx = idx
                ret_num = num
        return ret_num
    
    def last(self, line):
        ret_idx = -1
        ret_num = None
        for word, num in self.letters.items():
            idx = line.rfind(word)
            if idx > ret_idx:
                ret_idx = idx
                ret_num = num
        return ret_num
    
    def lineval(self, line):
        first = self.first(line)
        last = self.last(line)
        return first * 10 + last

    def run(self):
        return sum(self.lineval(line) for line in self.lines)

class Part2(Part1):
    letters = {
        "0": 0,
        "1": 1,
        "2": 2,
        "3": 3,
        "4": 4,
        "5": 5,
        "6": 6,
        "7": 7,
        "8": 8,
        "9": 9,
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <input file>")
        sys.exit(1)

    lines = Input(sys.argv[1]).lines

    part1 = Part1(lines)
    print(f"Part1: {part1.run()}")

    part2 = Part2(lines)
    print(f"Part2: {part2.run()}")
