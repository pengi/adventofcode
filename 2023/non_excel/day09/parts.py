#!/bin/env python3

import sys
import re

def nums_to_borders(nums):
    """
    Convert a number sequence, as stated in the puzzle, to a list of the last
    column
    """
    # Need to index the list later
    nums = list(nums)
    while sum(1 for n in nums if n != 0) != 0:
        yield nums[0], nums[-1]
        nums = [a-b for a,b in zip(nums[1:],nums)]


class Sequence:
    def __init__(self, nums):
        self.neg_nums = []
        self.pos_nums = nums
        first_last = list(nums_to_borders(nums))
        self.first = [a for a,b in first_last]
        self.last = [b for a,b in first_last]
    
    def __getitem__(self, i):
        if i < 0:
            i = -1-i # Flip to negative list
            while i >= len(self.neg_nums):
                # We need to fill with more numbers
                for k in range(len(self.first)-2,-1,-1):
                    self.first[k] -= self.first[k+1]
                self.neg_nums.append(self.first[0])
            return self.neg_nums[i]
        else:
            while i >= len(self.pos_nums):
                # We need to fill with more numbers
                for k in range(len(self.last)-2,-1,-1):
                    self.last[k] += self.last[k+1]
                self.pos_nums.append(self.last[0])
            return self.pos_nums[i]
    
    def __len__(self):
        return len(self.pos_nums)

class Input:
    def __init__(self, f):
        """
        Parse the input file
        
        f can be either a filename or a file-like object
        """
        if type(f) == str:
            f = open(f,"r")
        
        self.seqs = []
        for line in f:
            nums = [int(num) for num in line.split(" ")]
            self.seqs.append(Sequence(nums))

class Part1:
    def __init__(self, input):
        self.seqs = input.seqs

    def run(self):
        last_sum = 0
        for seq in self.seqs:
            last_sum += seq[len(seq)]
        return last_sum

class Part2:
    def __init__(self, input):
        self.seqs = input.seqs

    def run(self):
        last_sum = 0
        for seq in self.seqs:
            last_sum += seq[-1]
        return last_sum


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <input file>")
        sys.exit(1)

    input = Input(sys.argv[1])
    
    part1 = Part1(input)
    print(f"Part1: {part1.run()}")

    part2 = Part2(input)
    print(f"Part2: {part2.run()}")
