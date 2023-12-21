#!/bin/env python3

import sys
import re

from heapq import heappush, heappop

# For debug output, highlight background
_bg_set = "\x1b[44m"
_bg_clr = "\x1b[0m"

class Ant:
    def __init__(self, field, x, y, dir_dist = [3,3,3,3], tot_cost = 0, path = []):
        self.field = field
        self.x = x
        self.y = y
        self.dir_dist = dir_dist
        self.tot_cost = tot_cost
        self.path = path
    
    def __str__(self):
        return f"<Ant @{self.tot_cost} {self.x},{self.y} {self.dir_dist}>"
    
    def __lt__(self, other):
        return self.tot_cost < other.tot_cost
    
    def _visit_and_store(self, x, y, dir_dist):
        # Don't accept if we ran out of distance
        if any(d<0 for d in dir_dist):
            return []

        # Get if location is good enough
        if self.field.visit(x, y, dir_dist):
            # Calculate cost, it's the same for all outgoing ants
            cost = self.tot_cost + self.field.cost(x,y)
            return [Ant(self.field, x, y, dir_dist, cost, self.path + [(x,y)])]
        
        # otherwise skip
        return []

    def step(self):
        x = self.x
        y = self.y
        de, ds, dw, dn = self.dir_dist
        ants = []
        ants += self._visit_and_store(x+1, y, [de-1, 3, 0, 3])
        ants += self._visit_and_store(x, y+1, [3, ds-1, 3, 0])
        ants += self._visit_and_store(x-1, y, [0, 3, dw-1, 3])
        ants += self._visit_and_store(x, y-1, [3, 0, 3, dn-1])
        return ants

class Field:
    def __init__(self, cells):
        # Make sure it's a proper 2D array
        self.cells = [[int(x) for x in xs] for xs in cells]
        self.best = [[[0] * 4 for x in xs] for xs in cells]

    def visit(self, x, y, dir_dist):
        # Never possible to visit outside of the field:
        if y < 0 or y >= len(self.cells):
            return False
        if x < 0 or x >= len(self.cells[y]):
            return False

        # Accept if any direction is beter
        if any(old < new for old, new in zip(self.best[y][x], dir_dist)):
            self.best[y][x] = [max(old,new) for old,new in zip(self.best[y][x], dir_dist)]
            return True
        return False
    
    def width(self):
        return len(self.cells[0])
    
    def height(self):
        return len(self.cells)

    def cost(self, x, y):
        return self.cells[y][x]

    def copy(self):
        return Field(self.cells)
    
    def print(self, path):
        for y, crow in enumerate(self.cells):
            line = ""
            for x, c in enumerate(crow):
                if (y,x) in path:
                    line += _bg_set + str(c) + _bg_clr
                else:
                    line += str(c)
            print(line)

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
        ants = [Ant(field,0,0)]
        
        goal_x = field.width()-1
        goal_y = field.height()-1

        best_cost = None

        while len(ants) > 0:
            ant = heappop(ants)
            
            if ant.x == goal_x and ant.y == goal_y:
                if best_cost == None:
                    best_cost = ant.tot_cost
                if best_cost == ant.tot_cost:
                    print("---")
                    field.print(ant.path)

            for newant in ant.step():
                heappush(ants, newant)

        #field.print()
        return best_cost

class Part2:
    def __init__(self, input):
        self.field = input.field

    def run(self):
        return None

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
