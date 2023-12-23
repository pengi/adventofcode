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

class Brick:
    def __init__(self, xa, ya, za, xb, yb, zb):
        self.num = None
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
    
    
    def _calc_dep_fall(self, has_fallen):
        # Will this fall if tag is removed?
        if any(not has_fallen[brick.num] for brick in self.contact_down):
            # If so, this will remain, and so the ones above
            return 0
        
        # Tag this brick
        has_fallen[self.num] = True

        return 1 + sum(brick._calc_dep_fall(has_fallen) for brick in self.contact_up)

    def calc_depends(self, has_fallen):
        # This will fall
        has_fallen[self.num] = True

        # Count number of depdendents
        # If two are on next level, first may not trigger level over that to
        # fall, but then level above will trigger instead
        return sum(brick._calc_dep_fall(has_fallen) for brick in self.contact_up)

class Stack:
    def __init__(self):
        self.bricks = []

    def add_brick(self, brick):
        brick.num = len(self.bricks)
        self.bricks.append(brick)
    
    def num_bricks(self):
        return len(self.bricks)
    
    def _dopack(self, brick_nr, packed_list, below_list):
        # Aleady packed
        if packed_list[brick_nr]:
            return
        
        # Pack all below first
        for below_nr in below_list[brick_nr]:
            self._dopack(below_nr, packed_list, below_list)
        
        # Pack this brick
        self.bricks[brick_nr].pack([self.bricks[i] for i in below_list[brick_nr]])
        packed_list[brick_nr] = True

    def pack(self):
        top_bricks = [True] * len(self.bricks)
        below = [[] for brick in self.bricks]

        # Find all blocks below every brick, and also find top bricks
        for ia, ca in enumerate(self.bricks):
            for ib, cb in enumerate(self.bricks):
                if ia != ib:
                    if ca.above(cb):
                        top_bricks[ib] = False
                        below[ia].append(ib)
        
        is_packed = [False] * len(self.bricks)
        for i, is_top in enumerate(top_bricks):
            if is_top:
                self._dopack(i, is_packed, below)
        
        for brick_nr, brick in enumerate(self.bricks):
            brick.add_contacts([self.bricks[i] for i in below[brick_nr]])

    def calc_depends(self, brick_nr):
        return self.bricks[brick_nr].calc_depends([False] * len(self.bricks))


class Input:
    def __init__(self, f):
        """
        Parse the input file
        
        f can be either a filename or a file-like object
        """
        if type(f) == str:
            f = open(f,"r")
        
        re_brick = re.compile(r"([0-9]+),([0-9]+),([0-9]+)~([0-9]+),([0-9]+),([0-9]+)")

        self.stack = Stack()
        for l in f:
            m = re_brick.fullmatch(l.strip())
            if m:
                self.stack.add_brick(Brick(*[int(crd) for crd in m.groups()]))
        

class Part1:
    def __init__(self, input):
        self.stack = copy.deepcopy(input.stack)

    def run(self):
        self.stack.pack()

        # Nodes that can't be desintegrated is if any brick in contact_up has
        # only one contact_down
        num_disint = 0
        for i, brick in enumerate(self.stack.bricks):
            num_sup = sum(1 for c in brick.contact_up if len(c.contact_down) == 1)
            if num_sup == 0:
                num_disint += 1
        return num_disint

class Part2:
    def __init__(self, input):
        self.stack = copy.deepcopy(input.stack)

    def run(self):
        self.stack.pack()
        return sum(self.stack.calc_depends(i) for i in range(self.stack.num_bricks()))

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
