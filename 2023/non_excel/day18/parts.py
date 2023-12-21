#!/bin/env python3

import sys
import re

_dirs = {
    'R': (1, 0),
    'D': (0, 1),
    'L': (-1, 0),
    'U': (0, -1)
}

class Ant:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.area = 0
        self.steps = 0

    def __str__(self):
        return f"<Ant ({self.x},{self.y})>"

    def walk(self, direction, dist):
        dx, dy = _dirs[direction]
        dx *= dist
        dy *= dist

        # This area works since all steps are veritcal or horizontal, so either
        # dx or dy
        #
        # For explaination of how the area is calculated, see day 10. However,
        # this extends the area outside path, instead of cutting away
        self.area += dy * self.x

        self.x += dx
        self.y += dy

        self.steps += dist
    
    def get_area(self):
        if self.x != 0 or self.y != 0:
            # Area only works if back to origin
            return False
        
        return self.area + self.steps//2 +  1

class Input:
    def __init__(self, f):
        """
        Parse the input file

        f can be either a filename or a file-like object
        """
        if type(f) == str:
            f = open(f,"r")

        self.steps = []
        for line in f:
            m = re.fullmatch(r"([RULD]) ([0-9]+) \(#([0-9a-fA-F]+)\)", line.strip())
            if m:
                direction, distance, color = m.groups()
                self.steps.append((direction, int(distance), color))
        

class Part1:
    def __init__(self, input):
        self.steps = input.steps

    def run(self):
        a = Ant()
        for s in self.steps:
            direction, dist, color = s
            a.walk(direction, dist)
        return a.get_area()

class Part2:
    def __init__(self, input):
        self.steps = input.steps

    def run(self):
        a = Ant()
        dir_num = ['R','D','L','U']
        for s in self.steps:
            direction, dist, color = s
            dist = int(color[0:5], 16)
            direction = dir_num[int(color[5])]
            a.walk(direction, dist)
        return a.get_area()
        


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <input file>")
        sys.exit(1)

    input = Input(sys.argv[1])

    part1 = Part1(input)
    print(f"Part1: {part1.run()}")

    part2 = Part2(input)
    print(f"Part2: {part2.run()}")
