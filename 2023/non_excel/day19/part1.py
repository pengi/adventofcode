#!/bin/env python3

import sys
import re

_comp = {
    '<': lambda a, b: a < b,
    '>': lambda a, b: a > b,
}

class Workflow:
    def __init__(self, name):
        self.name = name
        self.rules = []

    def add_compare(self, name, op, value, dest):
        self.rules.append((name, op, value, dest))

    def add_fallback(self, dest):
        self.rules.append((None, None, None, dest))

    def process(self, rating):
        for name, op, value, dest in self.rules:
            if name is None:
                return dest
            if _comp[op](rating[name], value):
                return dest
        print(f"Unknown goal {self} - {rating}")
        return None

    def __str__(self):
        rules_str = ', '.join(f"{var}{op}{value}:{dest}" if var is not None else f"{dest}" for var,op,value,dest in self.rules)
        return f"{self.name} {rules_str}"

class Input:
    def __init__(self, f):
        """
        Parse the input file
        
        f can be either a filename or a file-like object
        """
        if type(f) == str:
            f = open(f,"r")

        self.wfs = {}
        self.ratings = []

        for l in f:
            l = l.strip()

            m = re.fullmatch(r"([a-z]+){(.*)}",l)
            if m:
                # workflow line
                wfname, rules = m.groups()

                wf = Workflow(wfname)
                self.wfs[wfname] = wf

                for rule in rules.split(','):
                    m = re.fullmatch(r"([xmas])([<>])([0-9]+):([a-zA-Z]+)", rule)
                    if m:
                        name, op, value, dest = m.groups()
                        wf.add_compare(name, op, int(value), dest)
                        continue
                    
                    m = re.fullmatch(r"([a-zA-Z]+)", rule)
                    if m:
                        dest, = m.groups()
                        wf.add_fallback(dest)
                        continue

                    print(f"Unknown rule {l}")

            m = re.fullmatch(r"{(.*)}",l)
            if m:
                # rating line
                rating = {k: int(v) for k,v in (kv.split('=',2) for kv in m.group(1).split(","))}
                self.ratings.append(rating)
        

class Part1:
    def __init__(self, input):
        self.wfs = input.wfs
        self.ratings = input.ratings

    def run(self):
        sum_accepted = 0
        for rating in self.ratings:
            wfname = 'in'
            path = [wfname]
            while wfname != 'A' and wfname != 'R':
                wfname = self.wfs[wfname].process(rating)
                path.append(wfname)
            if wfname == 'A':
                sum_accepted += sum(rating.values())
        return sum_accepted

if __name__ == "__main__":
    import doctest
    doctest.testmod()

    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <input file>")
        sys.exit(1)

    input = Input(sys.argv[1])
    
    part1 = Part1(input)
    print(f"Part1: {part1.run()}")
