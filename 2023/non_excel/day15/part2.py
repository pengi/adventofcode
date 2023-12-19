#!/bin/env python3

import sys
import re

def hash(s):
    """
    Hash function

    >>> hash('HASH')
    52
    """
    val = 0
    for c in s.strip():
        val += ord(c)
        val *= 17
        val %= 256
    return val

class Box:
    def __init__(self):
        # Front is index 0, back is high index
        self.slots = []
    
    def __str__(self):
        return ",".join(f"{lbl}={f}" for lbl,f in self.slots)
    
    def rem(self, label): # Operation -
        self.slots = [(lbl, focal) for lbl, focal in self.slots if lbl != label]

    def add(self, label, focal): # Operation =
        if any(lbl == label for lbl,f in self.slots):
            self.slots = [(lbl, focal if lbl == label else f) for lbl, f in self.slots]
        else:
            self.slots.append((label, focal))

    def power(self, box_nr):
        power = 0
        for slot_nr, (label, focal) in enumerate(self.slots):
            power += (box_nr + 1) * (slot_nr + 1) * focal
        return power

class Input:
    def __init__(self, f):
        """
        Parse the input file
        
        f can be either a filename or a file-like object
        """
        if type(f) == str:
            f = open(f,"r")
        
        self.steps = f.read().strip().split(',')
        

class Part1:
    def __init__(self, input):
        self.steps = input.steps

    def run(self):
        return sum(hash(step) for step in self.steps)

class Part2:
    def __init__(self, input):
        self.steps = input.steps

    def run(self):
        boxes = [Box() for i in range(256)]
        re_add = re.compile(r"(.*)=([0-9])")
        re_rem = re.compile(r"(.*)-")

        for step in self.steps:
            m = re.fullmatch(r"(.*)=([0-9])", step)
            if m:
                lbl, focal = m.groups()
                boxes[hash(lbl)].add(lbl, int(focal))

            m = re.fullmatch(r"(.*)-", step)
            if m:
                lbl, = m.groups()
                boxes[hash(lbl)].rem(lbl)
        
        #for i, box in enumerate(boxes):
        #    if len(box.slots) > 0:
        #        print(f"{i:3} {box}")

        return sum(box.power(i) for i, box in enumerate(boxes))
            

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
