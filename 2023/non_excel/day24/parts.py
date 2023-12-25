#!/bin/env python3

import sys
import re

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

class Hail:
    def __init__(self, x, y, z, dx, dy, dz):
        self.crd = (x, y, z)
        self.speed = (dx, dy, dz)
    
    def __str__(self):
        return f"{','.join(str(c) for c in self.crd)} @ {','.join(str(d) for d in self.speed)}"

    def get_t(self, t):
        return tuple(c + t*d for c, d in zip(self.crd, self.speed))
    
    def intersect_xy(self, other):
        ax, ay, az = self.crd
        bx, by, bz = other.crd
        adx, ady, adz = self.speed
        bdx, bdy, bdz = other.speed

         # paralell
        if adx * bdy - ady * bdx == 0:
            return None
        
        at = (bdx*(ay - by) - bdy*(ax-bx)) / (adx*bdy - ady*bdx)
        bt = (adx*(by - ay) - ady*(bx-ax)) / (bdx*ady - bdy*adx)

        if at < 0 or bt < 0:
            return None

        return (ax + at*adx, ay + at*ady)
        

class Input:
    def __init__(self, f):
        """
        Parse the input file
        
        f can be either a filename or a file-like object
        """
        if type(f) == str:
            f = open(f,"r")
        
        self.hails = []
        for l in f:
            l = l.strip()
            m = re.fullmatch(r" *([-0-9]+), *([-0-9]+), *([-0-9]+) *@ *([-0-9]+), *([-0-9]+), *([-0-9]+) *", l)
            if m:
                crds = m.groups()
                self.hails.append(Hail(*(int(c) for c in crds)))

class Part1:
    def __init__(self, input):
        self.hails = input.hails

    def run(self):
        low = 200000000000000
        high = 400000000000000

        within = 0
        for i, hi in enumerate(self.hails):
            for j, hj in enumerate(self.hails):
                if j > i:
                    inter = hi.intersect_xy(hj)
                    if inter is not None:
                        cx, cy = inter
                        if low <= cx and cx <= high and low <= cy and cy <= high:
                            within += 1

        return within

class Part2:
    def __init__(self, input):
        pass

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
