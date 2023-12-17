#!/bin/env python3

import sys
import re
import math

class CubeSet:
    def __init__(self, r=0, g=0, b=0):
        self.r = r
        self.g = g
        self.b = b

    def __str__(self):
        return f"CubeSet({self.r},{self.g},{self.b})"

    def __add__(self, other):
        return CubeSet(self.r + other.r, self.g + other.g, self.b + other.b)
    
    def contains(self, other):
        return self.r >= other.r and self.g >= other.g and self.b >= other.b
    
    def power(self):
        return self.r * self.g * self.b

class Game:
    def __init__(self, id, sets):
        self.id = id
        self.sets = sets
    
    def __str__(self):
        return f"<Game {self.id} {' '.join(str(s) for s in self.sets)}>"
    
    def set_all(self):
        return sum(self.sets, CubeSet())
    
    def min_set(self):
        return CubeSet(
            max(s.r for s in self.sets),
            max(s.g for s in self.sets),
            max(s.b for s in self.sets)
        )

class Input:
    def _parse_values(self, values):
        return [int(v) for v in values.split(" ") if v != ""]
    
    @staticmethod
    def _parse_cubeset(desc):
        vars = {
            'red': 0,
            'green': 0,
            'blue': 0
        }
        for vals in desc.split(", "):
            count, color = vals.strip().split(" ")
            vars[color] += int(count)
        return CubeSet(vars['red'], vars['green'], vars['blue'])


    def __init__(self, f):
        """
        Parse the input file
        
        f can be either a filename or a file-like object
        """
        if type(f) == str:
            f = open(f,"r")

        self.games = []
        for line in f:
            id, cubedesc = re.match("^Game ([0-9]+): (.*)$", line).groups()
            game = Game(int(id), [
                self._parse_cubeset(s) for s in cubedesc.split(";")
            ])
            self.games.append(game)

    def __str__(self):
        return repr(self.races)

class Part1:
    def __init__(self, games):
        self.games = games

    def run(self):
        id_sum = 0
        all_cubes = CubeSet(12, 13, 14)
        for game in self.games:
            if all_cubes.contains(game.min_set()):
                id_sum += game.id
        return id_sum

class Part2:
    def __init__(self, games):
        self.games = games

    def run(self):
        return sum(g.min_set().power() for g in self.games)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <input file>")
        sys.exit(1)

    games = Input(sys.argv[1]).games

    part1 = Part1(games)
    print(f"Part1: {part1.run()}")

    part2 = Part2(games)
    print(f"Part2: {part2.run()}")
