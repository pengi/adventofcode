#!/bin/env python3

import sys
import re

class Panel:
    def __init__(self, field):
        self.field = field
        self.width = len(field[0])
        self.height = len(field)
    
    def __str__(self):
        return "\n".join("".join(slot for slot in row) for row in self.field)

    def copy(self):
        return Panel([[x for x in xs] for xs in self.field])

    def _do_move(self, x, y, dx, dy, n):
        """
        Do one row/column of rock processing

        starting at (x,y), step (dx,dy) steps for n iterations
        """
        next_slot = 0
        for i in range(n):
            cx = x + dx * i
            cy = y + dy * i
            slot = self.field[cy][cx]
            if slot == 'O':
                self.field[cy][cx] = '.'
                self.field[y  + dy*next_slot][x  + dx*next_slot] = 'O'
                next_slot += 1
            elif slot == '#':
                next_slot = i+1
    
    def flip_north(self):
        for x in range(self.width):
            self._do_move(x, 0, 0, 1, self.height)
    
    def flip_west(self):
        for y in range(self.height):
            self._do_move(0, y, 1, 0, self.width)
    
    def flip_south(self):
        for x in range(self.width):
            self._do_move(x, -1, 0, -1, self.height)
    
    def flip_east(self):
        for y in range(self.height):
            self._do_move(-1, y, -1, 0, self.width)
    
    def spin_cycle(self):
        self.flip_north()
        self.flip_west()
        self.flip_south()
        self.flip_east()
    
    def get_load(self):
        return sum(
            (self.height - i) * sum(1 for slot in row if slot == 'O')
            for i,row in enumerate(self.field)
        )

class Input:
    def __init__(self, f):
        """
        Parse the input file
        
        f can be either a filename or a file-like object
        """
        if type(f) == str:
            f = open(f,"r")
        
        self.panel = Panel([list(l.strip()) for l in f.readlines() if l.strip() != ""])


class Part1:
    def __init__(self, input):
        self.panel = input.panel

    def run(self):
        p = self.panel.copy()
        p.flip_north()
        return p.get_load()


class Part2:
    def __init__(self, input):
        self.panel = input.panel

    def run(self):
        target_t = 1000000000

        # We assume it will stabilize, so log states and check for old cycles
        states = {}
        p = self.panel.copy()
        t = 1
        while True:
            p.spin_cycle()
            strp = str(p)
            if strp in states:
                break
            states[strp] = t
            t += 1

        # Calculate interval
        interval = t - states[strp]

        # since each interval returns back to original state, just don't do the
        # intervals, but calculate how many more spin cycles are left after last
        # interval
        t_left = (target_t - t) % interval

        for i in range(t_left):
            p.spin_cycle()

        return p.get_load()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <input file>")
        sys.exit(1)

    input = Input(sys.argv[1])
    
    part1 = Part1(input)
    print(f"Part1: {part1.run()}")
    
    part2 = Part2(input)
    print(f"Part1: {part2.run()}")
