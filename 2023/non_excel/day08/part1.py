#!/bin/env python3

import sys
import re

class Path:
    def __init__(self, path):
        self.path = path
    
    def get(self, index):
        return self.path[index % len(self.path)]

class Map:
    def __init__(self, directions):
        self.directions = directions
    
    def get(self, location, direction):
        left, right = self.directions[location]
        if direction == 'L':
            return left
        elif direction == 'R':
            return right
        else:
            raise Exception(f"unknown direction {direction}")
    
    def locations(self):
        return self.directions.keys()

class Input:
    def __init__(self, f):
        """
        Parse the input file
        
        f can be either a filename or a file-like object
        """
        if type(f) == str:
            f = open(f,"r")
        
        # First line is path
        self.path = Path(f.readline().strip())
        
        # Rest is map
        directions = {}
        for line in f:
            m = re.fullmatch(r"(...) = \((...), (...)\)", line.strip())
            if m:
                src, left, right = m.groups()
                directions[src] = (left, right)
        
        self.map = Map(directions)
        

class Part1:
    def __init__(self, input):
        self.map = input.map
        self.path = input.path

    def run(self):
        step = 0
        location = 'AAA'
        while location != 'ZZZ':
            location = self.map.get(location, self.path.get(step))
            step += 1
        
        return step

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <input file>")
        sys.exit(1)

    input = Input(sys.argv[1])
    
    part1 = Part1(input)
    print(f"Part1: {part1.run()}")
