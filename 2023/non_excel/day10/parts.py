#!/bin/env python3

import sys
import re

# Directions are determined as bitmasks
DIR_N = 0b0001
DIR_E = 0b0010
DIR_S = 0b0100
DIR_W = 0b1000

_dirs = [DIR_N, DIR_E, DIR_S, DIR_W]

# Reverse a direction
_dir_rev = {
    DIR_N: DIR_S,
    DIR_E: DIR_W,
    DIR_S: DIR_N,
    DIR_W: DIR_E,
}

# Maps direction index to typle of delta x and delta y for a step
_dir_step = {
    DIR_N: (0, -1),
    DIR_E: (1, 0),
    DIR_S: (0, 1),
    DIR_W: (-1, 0),
}

# Maps a pipe letter to a bitmask, such as bits 1<<d is enabled if the pipe has
# an exit to that direction
_pipes = {
    '|': 0b0101,
    '-': 0b1010,
    'L': 0b0011,
    'F': 0b0110,
    '7': 0b1100,
    'J': 0b1001,
    '.': 0b0000
}
_pipes_rev = {v:k for k,v in _pipes.items()}

class Ant:
    def __init__(self, map, x, y, dir=None):
        self.map = map
        self.x = x
        self.y = y
        self.steps = 0
        if dir is None:
            self.find_dir()
        else:
            self.dir=dir

    def __str__(self):
        return f"<Ant ({self.x},{self.y})x{self.dir} @{self.steps}>"

    def find_dir(self):
        """
        Find a valid direction on a map
        """
        for d in _dirs:
            temp = Ant(self.map, self.x, self.y, d)
            if temp.walk():
                self.dir = d
                return True
        return False

    def walk(self):
        dx, dy = _dir_step[self.dir]
        nx = self.x + dx
        ny = self.y + dy
        if not self.map.is_valid(nx, ny):
            return False

        next_pipe = self.map.get(nx, ny)

        # Pipe doesn't have an input hole
        if next_pipe & _dir_rev[self.dir] == 0:
            return False

        self.x = nx
        self.y = ny
        self.dir = next_pipe & ~_dir_rev[self.dir] # save remaining direction
        self.steps += 1
        return True

class Map:
    def __init__(self, lines):
        self.lines = lines
        self.tags_tag = {}
        self.tags_coord = {}
        self.update_tag('S')

    def update_tag(self, tag):
        """
        Locate and log a tag, and update with proper pipe orientation
        """
        x,y = self.find(tag)
        exits = 0
        for d in _dirs:
            temp = Ant(self, x, y, d)
            if temp.walk():
                exits |= d
        self.tags_tag[tag] = (x,y)
        self.tags_coord[(x,y)] = tag
        self.lines[y][x] = _pipes_rev[exits]


    def find(self, c):
        for y, row in enumerate(self.lines):
            for x, pipe in enumerate(row):
                if pipe == c:
                    return x,y
        return None

    def is_valid(self,x,y):
        """
        Check if location is valid
        """
        if y<0 or y>=len(self.lines):
            return False
        if x<0 or x>=len(self.lines[y]):
            return False
        return True

    def get(self,x,y):
        return _pipes[self.lines[y][x]]

    def get_tag(self,c):
        if c in self.tags_tag:
            return self.tags_tag[c]
        return None

    def at_tag(self,x,y):
        if (x,y) in self.tags_coord:
            return self.tags_coord[(x,y)]
        return None

class Input:
    def __init__(self, f):
        """
        Parse the input file

        f can be either a filename or a file-like object
        """
        if type(f) == str:
            f = open(f,"r")

        lines = [list(l.strip()) for l in f.readlines() if l.strip() != ""]
        self.map = Map(lines)

class Part1:
    def __init__(self, input):
        self.map = input.map

    def run(self):
        ant = Ant(self.map, *self.map.get_tag('S'))
        while True:
            ant.walk()
            #print(ant)
            if self.map.at_tag(ant.x, ant.y) == 'S':
                break
        return ant.steps // 2

class Part2:
    def __init__(self, input):
        self.map = input.map

    def run(self):
        # To count the area within the pipe as puzzle describes, it's easier to
        # split in some sub problems:
        #
        # 1. count the area within the pipe, as if the pipe turns in the middle
        #    of the letter. Thus a map:
        #
        #    F7
        #    LJ
        #
        #    doesn't contain any area according to puzzle, but still 1/4 in each
        #    segment, thus 1 area in total.
        #
        #    This can be done by vertical pipes adding the area from the pipe to
        #    the leftmost border of the map when moving upwards, and subtracting
        #    that area when moving downwards. The area within the pipe will then
        #    be the only part left. (sideways is technically counted too, but
        #    since no vertical movmement, the area added/subtracted will be 0)
        #
        #    Note that depending on direction of travel, this area can result
        #    in either positive or negative. Therefore use absolute value of the
        #    area if direction doesn't matter (which it doesn't)
        #
        # 2. Count the number of steps taken.
        #    Done as part 1
        #
        # 3. Compensate for extra area on pipe segments.
        #
        #    Since the loop does not cross itself, there are always 4 outermost
        #    corners, which will only add one extra 1/4 each to the area.
        #
        #    All other pipe segments will either contribute with 1/2 to the area
        #    each, or come in pairs of two that one adds 1/4 and the other 3/4.
        #    Thus all add on average 1/2 each in total.
        #
        #    Therefore, area extra can be calculated as ((steps-4)//2 + 4//4)
        ant = Ant(self.map, *self.map.get_tag('S'))
        area = 0
        while True:
            if ant.dir == DIR_N:
                area += ant.x
            if ant.dir == DIR_S:
                area -= ant.x
            ant.walk()
            if self.map.at_tag(ant.x, ant.y) == 'S':
                break
        return abs(area) - ((ant.steps-4) // 2) - (4 // 4)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <input file>")
        sys.exit(1)

    input = Input(sys.argv[1])

    part1 = Part1(input)
    print(f"Part1: {part1.run()}")

    part2 = Part2(input)
    print(f"Part2: {part2.run()}")
