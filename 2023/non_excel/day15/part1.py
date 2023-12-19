#!/bin/env python3

import sys
import re

def hash(s):
    """
    Hash function

    >>> hash('HASH')
    52
    """
    val = 0
    for c in s.strip():
        val += ord(c)
        val *= 17
        val %= 256
    return val

class Input:
    def __init__(self, f):
        """
        Parse the input file
        
        f can be either a filename or a file-like object
        """
        if type(f) == str:
            f = open(f,"r")
        
        self.steps = f.read().strip().split(',')
        

class Part1:
    def __init__(self, input):
        self.steps = input.steps

    def run(self):
        return sum(hash(step) for step in self.steps)

if __name__ == "__main__":
    import doctest
    doctest.testmod()

    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <input file>")
        sys.exit(1)

    input = Input(sys.argv[1])
    
    part1 = Part1(input)
    print(f"Part1: {part1.run()}")
