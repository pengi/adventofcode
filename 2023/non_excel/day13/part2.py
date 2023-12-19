#!/bin/env python3

import sys
import re

def str_compare(a,b):
    return sum(1 for ca,cb in zip(a,b) if ca!=cb)

class Image:
    def __init__(self, pxls):
        self.rows = pxls.split("\n")
    
    def flip(self):
        """
        Return a flipped copy of the image, where x and y is reversed
        """
        pxls = ["".join(row[i] for row in self.rows) for i in range(len(self.rows[0]))]
        return Image("\n".join(pxls))
    
    def _is_mirror_y(self, y, smudges = 0):
        smudges_found = 0
        for ya, yb in zip(range(y,-1,-1),range(y+1,len(self.rows))):
            smudges_found += str_compare(self.rows[ya], self.rows[yb])
            # Fail early if needed
            if smudges_found > smudges:
                return False
        return smudges_found == smudges

    def get_mirror_y(self, smudges = 0):
        return [
            y
            for (y,(a,b))
            in enumerate(zip(self.rows,self.rows[1:]))
            if str_compare(a, b) <= smudges and self._is_mirror_y(y, smudges)
        ]

    def __str__(self):
        return "\n".join(self.rows)

class Input:
    def __init__(self, f):
        """
        Parse the input file

        f can be either a filename or a file-like object
        """
        if type(f) == str:
            f = open(f,"r")

        content = f.read()
        self.imgs = []
        for image in content.split("\n\n"):
            self.imgs.append(Image(image.strip()))

class Part1:
    def __init__(self, input):
        self.imgs = input.imgs

    def run(self):
        mirrorsum = 0
        for img in self.imgs:
            mirrorsum += 100 * sum(n+1 for n in img.get_mirror_y(0))
            mirrorsum += sum(n+1 for n in img.flip().get_mirror_y(0))
        return mirrorsum

class Part2:
    def __init__(self, input):
        self.imgs = input.imgs

    def run(self):
        mirrorsum = 0
        for img in self.imgs:
            mirrorsum += 100 * sum(n+1 for n in img.get_mirror_y(1))
            mirrorsum += sum(n+1 for n in img.flip().get_mirror_y(1))
        return mirrorsum

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <input file>")
        sys.exit(1)

    input = Input(sys.argv[1])

    part1 = Part1(input)
    print(f"Part2: {part1.run()}")

    part2 = Part2(input)
    print(f"Part2: {part2.run()}")
