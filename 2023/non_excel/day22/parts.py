#!/bin/env python3

import sys
import re

import copy

def overlap1d(s1, e1, s2, e2):
    """
    Check if overlapping in one dimesion
    
    if two ends have same coordinates, they overlap still

    >>> overlap1d(3, 4, 5, 7)
    False
    >>> overlap1d(3, 5, 5, 7)
    True
    >>> overlap1d(3, 6, 5, 7)
    True
    >>> overlap1d(3, 12, 5, 7)
    True
    >>> overlap1d(3, 5, 0, 7)
    True
    >>> overlap1d(10, 12, 5, 7)
    False
    """
    return s1 <= e2 and s2 <= e1


class Cube:
    def __init__(self, xa, ya, za, xb, yb, zb):
        self.xa = xa
        self.ya = ya
        self.za = za
        self.xb = xb
        self.yb = yb
        self.zb = zb
        self.contact_up = []
        self.contact_down = []

    def __str__(self):
        return f"<{self.xa},{self.ya},{self.za} ~ {self.xb},{self.yb},{self.zb}>"

    def above(self, other):
        # check overlap
        if overlap1d(self.xa, self.xb, other.xa, other.xb) \
            and overlap1d(self.ya, self.yb, other.ya, other.yb):
            return self.za > other.zb
        else:
            return False
    
    def pack(self, below):
        top_z = max([0] + [c.zb for c in below])
        distance = self.za - top_z - 1
        self.za -= distance
        self.zb -= distance
    
    def add_contacts(self, below):
        # Assuming below actaully overlaps, since it comes from packing
        for other in below:
            if other.zb == self.za - 1:
                # Got contact
                self.contact_down.append(other)
                other.contact_up.append(self)

class Stack:
    def __init__(self):
        self.cubes = []

    def add_cube(self, cube):
        self.cubes.append(cube)
    
    def _dopack(self, cube_nr, packed_list, below_list):
        # Aleady packed
        if packed_list[cube_nr]:
            return
        
        # Pack all below first
        for below_nr in below_list[cube_nr]:
            self._dopack(below_nr, packed_list, below_list)
        
        # Pack this cube
        self.cubes[cube_nr].pack([self.cubes[i] for i in below_list[cube_nr]])
        packed_list[cube_nr] = True

    def pack(self):
        top_cubes = [True] * len(self.cubes)
        below = [[] for cube in self.cubes]

        # Find all blocks below every cube, and also find top cubes
        for ia, ca in enumerate(self.cubes):
            for ib, cb in enumerate(self.cubes):
                if ia != ib:
                    if ca.above(cb):
                        top_cubes[ib] = False
                        below[ia].append(ib)
        
        is_packed = [False] * len(self.cubes)
        for i, is_top in enumerate(top_cubes):
            if is_top:
                self._dopack(i, is_packed, below)
        
        for cube_nr, cube in enumerate(self.cubes):
            cube.add_contacts([self.cubes[i] for i in below[cube_nr]])


class Input:
    def __init__(self, f):
        """
        Parse the input file
        
        f can be either a filename or a file-like object
        """
        if type(f) == str:
            f = open(f,"r")
        
        re_cube = re.compile(r"([0-9]+),([0-9]+),([0-9]+)~([0-9]+),([0-9]+),([0-9]+)")

        self.stack = Stack()
        for l in f:
            m = re_cube.fullmatch(l.strip())
            if m:
                self.stack.add_cube(Cube(*[int(crd) for crd in m.groups()]))
        

class Part1:
    def __init__(self, input):
        self.stack = copy.deepcopy(input.stack)

    def run(self):
        self.stack.pack()

        # Nodes that can't be desintegrated is if any cube in contact_up has
        # only one contact_down
        num_disint = 0
        for i, cube in enumerate(self.stack.cubes):
            num_sup = sum(1 for c in cube.contact_up if len(c.contact_down) == 1)
            if num_sup == 0:
                num_disint += 1
        return num_disint

class Part2:
    def __init__(self, input):
        self.stack = copy.deepcopy(input.stack)

    def run(self):
        self.stack.pack()

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
