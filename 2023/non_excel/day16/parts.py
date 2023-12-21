#!/bin/env python3

import sys
import re

from collections import deque

# Directions are determined as bitmasks
DIR_N = (0, -1)
DIR_E = (1, 0)
DIR_S = (0, 1)
DIR_W = (-1, 0)

_dir_bitmask = {
    DIR_N: 0b0001,
    DIR_E: 0b0010,
    DIR_S: 0b0100,
    DIR_W: 0b1000
}

_dir_name = {
    DIR_N: "N",
    DIR_E: "E",
    DIR_S: "S",
    DIR_W: "W"
}

# Mirror behaviour
_mirrors_output = {
    ('.', DIR_N): [DIR_N],
    ('.', DIR_E): [DIR_E],
    ('.', DIR_S): [DIR_S],
    ('.', DIR_W): [DIR_W],
    ('|', DIR_N): [DIR_N],
    ('|', DIR_E): [DIR_N, DIR_S],
    ('|', DIR_S): [DIR_S],
    ('|', DIR_W): [DIR_N, DIR_S],
    ('-', DIR_N): [DIR_E, DIR_W],
    ('-', DIR_E): [DIR_E],
    ('-', DIR_S): [DIR_E, DIR_W],
    ('-', DIR_W): [DIR_W],
    ('/', DIR_N): [DIR_E],
    ('/', DIR_E): [DIR_N],
    ('/', DIR_S): [DIR_W],
    ('/', DIR_W): [DIR_S],
    ('\\', DIR_N): [DIR_W],
    ('\\', DIR_E): [DIR_S],
    ('\\', DIR_S): [DIR_E],
    ('\\', DIR_W): [DIR_N],
}

# For debug output, highlight background
_bg_set = "\x1b[44m"
_bg_clr = "\x1b[0m"

class Ant:
    def __init__(self, field, crd, dir):
        self.field = field
        self.crd = crd
        self.dir = dir
    
    def __str__(self):
        return f"<Ant {_dir_name[self.dir]} {self.crd}>"
    
    def step(self):
        x, y = self.crd
        dx, dy = self.dir
        
        # If exit already visited in reverse, then bail out
        if not self.field.visit((x, y), (-dx, -dy)):
            return []
        
        # Get outputs
        cell = self.field.get((x, y))
        ants = []
        for odx, ody in _mirrors_output[(cell, (dx, dy))]:
            # If output is visited, don't exit it again
            if self.field.visit((x, y), (odx, ody)):
                ants.append(Ant(self.field, (x + odx, y + ody), (odx, ody)))
        return ants

class Field:
    def __init__(self, cells):
        # Make sure it's a proper 2D array
        self.cells = [[x for x in xs] for xs in cells]
        self.state = [[0 for x in xs] for xs in cells]

    def visit(self, crd, dir):
        x,y = crd

        # Never possible to visit outside of the field:
        if y < 0 or y >= len(self.state):
            return False
        if x < 0 or x >= len(self.state[y]):
            return False

        bitmask = _dir_bitmask[dir]
        if self.state[y][x] & bitmask != 0:
            return False
        self.state[y][x] |= bitmask
        return True
    
    def width(self):
        return len(self.cells[0])
    
    def height(self):
        return len(self.cells)

    def get(self, crd):
        x,y = crd
        return self.cells[y][x]

    def copy(self):
        return Field(self.cells)
    
    def print(self):
        for crow, srow in zip(self.cells, self.state):
            line = ""
            for c, s in zip(crow, srow):
                if s != 0:
                    line += _bg_set + c + _bg_clr
                else:
                    line += c
            print(line)

    def count_energized(self):
        return sum(sum(1 for x in xs if x != 0) for xs in self.state)

class Input:
    def __init__(self, f):
        """
        Parse the input file
        
        f can be either a filename or a file-like object
        """
        if type(f) == str:
            f = open(f,"r")
        
        self.field = Field(list(l.strip()) for l in f if l.strip() != "")

class Part1:
    def __init__(self, input):
        self.field = input.field

    def run(self):
        field = self.field.copy()
        ants = deque([Ant(field, (0,0), DIR_E)])
        
        while len(ants) > 0:
            ant = ants.popleft()
            ants.extend(ant.step())

        #field.print()
        return field.count_energized()

class Part2:
    def __init__(self, input):
        self.field = input.field

    def run_one(self, ant):
        field = ant.field
        ants = deque([ant])
        
        while len(ants) > 0:
            ant = ants.popleft()
            ants.extend(ant.step())

        return field.count_energized()

    def run(self):
        counts = []
        for x in range(self.field.width()):
            counts += [self.run_one(Ant(self.field.copy(), (x,0), DIR_S))]
            counts += [self.run_one(Ant(self.field.copy(), (x,self.field.height()-1), DIR_N))]
        for y in range(self.field.width()):
            counts += [self.run_one(Ant(self.field.copy(), (0,y), DIR_E))]
            counts += [self.run_one(Ant(self.field.copy(), (self.field.width()-1,y), DIR_W))]
        return max(counts)
        

if __name__ == "__main__":
    import doctest
    doctest.testmod()

    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <input file>")
        sys.exit(1)

    input = Input(sys.argv[1])
    
    part1 = Part1(input)
    print(f"Part1: {part1.run()}")

    part2 = Part2(input)
    print(f"Part2: {part2.run()}")
