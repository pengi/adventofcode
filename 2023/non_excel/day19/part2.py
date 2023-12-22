#!/bin/env python3

import sys
import re

_comp = {
    '<': lambda a, b: a < b,
    '<=': lambda a, b: a <= b,
    '>': lambda a, b: a > b,
    '>=': lambda a, b: a >= b,
}

class Subset:
    def __init__(self, ranges):
        self.ranges = ranges
        # Keeping as 1 rating for subsets means interval will be treated as
        # options when multiplying count to rating
        self.rating = 1

    @classmethod
    def init_single(cls, values):
        """
        Generate the subset of a single value
        
        >>> Subset.init_single({'a': 12, 'b': 13}).count()
        1
        """
        subset = cls({k: (v,v+1) for k,v in values.items()})
        # In this case, we can calculate the rating for part1
        subset.rating = sum(values.values())
        return subset

    def copy(self):
        subset = Subset({k: v for k,v in self.ranges.items()})
        subset.rating = self.rating
        return subset

    def _copy_update(self, name, lo, hi):
        result = self.copy()
        if hi <= lo:
            # no matches
            result.ranges = {k: (0,0) for k,v in self.ranges.items()}
        else:
            result.ranges[name] = lo, hi
        return result
    
    def copy_clear(self):
        # update to match no elements should clear
        return self._copy_update('x', 0, 0)

    def filter_ge(self, name, value):
        lo, hi = self.ranges[name]
        if lo < value:
            lo = value
        return self._copy_update(name, lo, hi)

    def filter_lt(self, name, value):
        lo, hi = self.ranges[name]
        if hi > value:
            hi = value
        return self._copy_update(name, lo, hi)
    
    def count(self):
        count = 1
        for lo, hi in self.ranges.values():
            count *= hi-lo
        return count
    

class Workflow:
    def __init__(self, name):
        self.name = name
        self.rules = []

    def add_compare(self, name, op, value, dest):
        # Easier to use to complementary operations, such as < and >=, since
        # interval is then always upper-lower.
        if op == '>':
            value += 1
            op = '>='
        self.rules.append((name, op, value, dest))

    def add_fallback(self, dest):
        self.rules.append((None, None, None, dest))

    def process(self, subset):
        for name, op, value, dest in self.rules:
            if name is None:
                yield dest, subset
                subset = subset.copy_clear() # nothing left
            elif op == '<':
                yield dest, subset.filter_lt(name, value)
                subset = subset.filter_ge(name, value)
            elif op == '>=':
                yield dest, subset.filter_ge(name, value)
                subset = subset.filter_lt(name, value)
            else:
                print(f"Shouldn't happen: {name} {op} {value} => {dest}")

    def __str__(self):
        rules_str = ', '.join(f"{var}{op}{value}:{dest}" if var is not None else f"{dest}" for var,op,value,dest in self.rules)
        return f"{self.name} {rules_str}"

class WorkflowSet:
    def __init__(self):
        self.wfs = {}
    
    def add(self, wf):
        self.wfs[wf.name] = wf
    
    def process(self, subset, wfname = 'in'):
        sum_accepted = 0
        for next_wf, next_subset in self.wfs[wfname].process(subset):
            # don't branch if nothing to branch on
            if next_subset.count() == 0:
                continue

            if next_wf == 'A':
                sum_accepted += next_subset.rating * next_subset.count()
            elif next_wf == 'R':
                # rejected
                pass
            else:
                # need to continue
                sum_accepted += self.process(next_subset, next_wf)
        return sum_accepted

class Input:
    def __init__(self, f):
        """
        Parse the input file
        
        f can be either a filename or a file-like object
        """
        if type(f) == str:
            f = open(f,"r")

        self.wfs = WorkflowSet()
        self.ratings = []

        for l in f:
            l = l.strip()

            m = re.fullmatch(r"([a-z]+){(.*)}",l)
            if m:
                # workflow line
                wfname, rules = m.groups()

                wf = Workflow(wfname)

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
                
                self.wfs.add(wf)

            m = re.fullmatch(r"{(.*)}",l)
            if m:
                # rating line
                rating = Subset.init_single({k: int(v) for k,v in (kv.split('=',2) for kv in m.group(1).split(","))})
                self.ratings.append(rating)
        

class Part1:
    def __init__(self, input):
        self.wfs = input.wfs
        self.ratings = input.ratings

    def run(self):
        sum_accepted = 0
        for rating in self.ratings:
            sum_accepted += self.wfs.process(rating)
        return sum_accepted
        

class Part2:
    def __init__(self, input):
        self.wfs = input.wfs

    def run(self):
        subset = Subset({
            'x': (1,4001),
            'm': (1,4001),
            'a': (1,4001),
            's': (1,4001)
        })
        return self.wfs.process(subset)

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
