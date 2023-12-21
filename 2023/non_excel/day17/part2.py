#!/bin/env python3

import sys
import re

from heapq import heappush, heappop


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


# For debug output, highlight background
_bg_set = "\x1b[44m"
_bg_clr = "\x1b[0m"

class Ant:
    def __init__(self, field, x, y, min_d, max_d, dir, tot_cost = 0, path = []):
        self.field = field
        self.x = x
        self.y = y
        self.min_d = min_d
        self.max_d = max_d
        self.dir = dir
        self.tot_cost = tot_cost
        self.path = path
    
    def __str__(self):
        return f"<Ant @{self.tot_cost} {self.x},{self.y} {_dir_name[self.dir]}>"
    
    def __lt__(self, other):
        return self.tot_cost < other.tot_cost
    
    def _new_ant(self, x, y, dir, cost, path):
        return Ant(self.field, x, y, self.min_d, self.max_d, dir, cost, path)

    def step(self):
        x = self.x
        y = self.y
        dx, dy = self.dir
        ants = []
        cost = self.tot_cost
        path = self.path
        for dist in range(1, self.max_d+1):
            nx = x + dx * dist
            ny = y + dy * dist

            # If going outside of field, then abort
            if not self.field.within(nx, ny):
                break
            cost += self.field.cost(nx, ny)
            path = path + [(nx,ny)] # make sure to make a copy

            if dist >= self.min_d:
                ants.append(self._new_ant(nx, ny, (dy, -dx), cost, path))
                ants.append(self._new_ant(nx, ny, (-dy, dx), cost, path))
        return ants

class Field:
    def __init__(self, cells):
        # Make sure it's a proper 2D array
        self.cells = [[int(x) for x in xs] for xs in cells]
        self.visited = [[0 for x in xs] for xs in cells]

    def within(self, x, y):
        if y < 0 or y >= len(self.visited):
            return False
        if x < 0 or x >= len(self.visited[y]):
            return False
        return True

    def visit(self, x, y, dir):
        # Never possible to visit outside of the field:
        if not self.within(x, y):
            return False

        # Accept if any direction is beter
        if self.visited[y][x] & _dir_bitmask[dir] != 0:
            return False
        
        self.visited[y][x] |= _dir_bitmask[dir]
        return True
    
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
                if (x,y) in path:
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
        self.min_d = 1
        self.max_d = 3

    def run(self):
        field = self.field.copy()
        ants = [
            Ant(field,0,0,self.min_d,self.max_d,(1,0)),
            Ant(field,0,0,self.min_d,self.max_d,(0,1))
            ]
        
        goal_x = field.width()-1
        goal_y = field.height()-1

        best_cost = None

        while len(ants) > 0:
            ant = heappop(ants)
            if not field.visit(ant.x, ant.y, ant.dir):
                continue
            
            if ant.x == goal_x and ant.y == goal_y:
                if best_cost == None:
                    best_cost = ant.tot_cost
                #if best_cost == ant.tot_cost:
                #    print("---")
                #    field.print(ant.path)

            for newant in ant.step():
                heappush(ants, newant)

        #field.print()
        return best_cost

class Part2(Part1):
    def __init__(self, input):
        self.field = input.field
        self.min_d = 4
        self.max_d = 10

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
