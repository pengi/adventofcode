#!/bin/env python3

import sys
import re
import math

from part1 import *

# Part 2 uses other input parsing...
class InputPart2(Input):
    def _parse_values(self, values):
        return [int(values.replace(" ", ""))]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <input file>")
        sys.exit(1)
        
    print("\nPart1:\n")

    part1 = Problem(Input(sys.argv[1]).races)
    part1_result = part1.run()

    print(f"\nPart1: {part1_result}\n")

        
    print("\nPart2:\n")

    part2 = Problem(InputPart2(sys.argv[1]).races)
    part2_result = part2.run()

    print(f"\nPart2: {part2_result}\n")
