#!/bin/env python3

import sys
import re

class Row:
    def __init__(self, springs, groups):
        self.springs = springs
        self.groups = groups
    
    def __str__(self):
        return f"{self.springs} {','.join(str(g) for g in self.groups)}"

    def __mul__(self, count):
        """
        Repeat current spring
        """
        return Row("?".join([self.springs] * count), self.groups * count)
    
    # To make it possible to have as index
    def __hash__(self):
        return hash((self.springs, ",".join(str(g) for g in self.groups)))

    def __eq__(self, other):
        return self.springs == other.springs and self.groups == other.groups

    @staticmethod
    def _consume(string, group):
        """
        Return stuff

        >>> Row._consume('...', 1) is None
        True

        >>> Row._consume('#..', 1)
        '.'

        >>> Row._consume('##.', 1) is None
        True

        >>> Row._consume('#?.', 1)
        '.'

        >>> Row._consume('?#.', 2)
        ''

        >>> Row._consume('?#.', 4) is None
        True
        """
        if len(string) < group or string[:group].find('.') >= 0:
            return None
        else:
            string = string[group:]

            # If consumed, next needs not to be a spring
            if string == '':
                return ''
            if string[0] == '#':
                return None
            
            # Also consume the next free space
            return string[1:]

    def step(self):
        # Drop . in the beginning
        springs = self.springs.lstrip('.')

        if len(springs) == 0:
            if len(self.groups) == 0:
                # No more groups to match, that's a success
                yield None
            return
        
        # If next is unknown, it's always an option to skip
        if springs[0] == '?':
            yield Row(springs[1:].lstrip('.'), self.groups)
        
        # Try to consume a group
        if len(self.groups) > 0:
            next_springs = self._consume(springs, self.groups[0])
            if next_springs is not None:
                yield Row(next_springs.lstrip('.'), self.groups[1:])
    
    def count(self):
        """
        Count number of solutions to the given row

        >>> Row('.??..??...?##.', [1,1,3]).count()
        4
        >>> Row('?###????????', [3,2,1]).count()
        10
        """
        # Native implementation would be to have a queue staring with current
        # row as an element. Poll an element from the queue. If element is
        # finished, then count it, otherwise step and add all options to the
        # queue.
        #
        # However, that will produce a lot of branches.
        #
        # better is to use some kind of memoization
        #
        # Therefore, make a bucketed priority queue, where each bucket is the
        # length of the springs string. Since each step are guaranteed to make
        # the springs shorter, it will terminate.
        #
        # If multiple branches ends up with the same row (which it will). Then
        # combine those, and count number of options in that branch instead.
        #
        # To make that possible, use a dict for each bucket, keyed on the row,
        # and pointing to the amount

        # Create buckets
        queue = [{} for i in range(len(self.springs)+1)]

        # Start with adding self
        queue[len(self.springs)][self] = 1

        tot_count = 0
        while len(queue) > 0:
            bucket = queue[-1]
            queue = queue[:-1]

            for row, count in bucket.items():
                for nrow in row.step():
                    if nrow is None:
                        tot_count += count
                    else:
                        bucket_num = len(nrow.springs)
                        nbucket = queue[bucket_num]
                        if nrow in nbucket:
                            nbucket[nrow] += count
                        else:
                            nbucket[nrow] = count
        return tot_count

class Input:
    def __init__(self, f):
        """
        Parse the input file
        
        f can be either a filename or a file-like object
        """
        if type(f) == str:
            f = open(f,"r")
        
        self.rows = []
        for line in f:
            springs, groupsstr = line.strip().split(" ")
            self.rows.append(Row(springs, [int(g) for g in groupsstr.split(",")]))
        

class Part1:
    def __init__(self, input):
        self.rows = input.rows

    def run(self):
        #for row in self.rows:
        #    print(f"{str(row):50}  ---  {row.count()}")
        return sum(row.count() for row in self.rows)

class Part2:
    def __init__(self, input):
        self.rows = input.rows

    def run(self):
        #for row in self.rows:
        #    print(f"{str(row):50}  ---  {(row*5).count()}")
        return sum((row*5).count() for row in self.rows)

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
