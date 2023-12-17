#!/bin/env python3

import sys
import re

class MapRange:
    """
    A translation range, where a set of numbers may be translated to another
    range
    """
    def __init__(self, dst: int, src: int, length: int):
        self.dst = dst
        self.src = src
        self.length = length
    
    def __str__(self):
        return f"{self.src} - {self.src+self.length-1} => {self.dst} - {self.dst+self.length-1}"

    def translate(self, number):
        """
        Translate a number given the current range

        returns None if no match
        """
        if number >= self.src and number < self.src + self.length:
            return number + self.dst - self.src
        else:
            return None

class Map:
    """
    A translation from a set of numbers to another, where ranges of numbers may
    be translated
    """
    def __init__(self):
        self.ranges = []

    def add_range(self, range: MapRange):
        self.ranges.append(range)
    
    def __str__(self):
        return "".join([f"{r}\n" for r in self.ranges])
    
    def translate(self, number):
        """
        Translate a number given current map
        """
        for range in self.ranges:
            translated = range.translate(number)

            # Only match first translation. Otherwise, if for example two ranges
            # are swtiching places in same map, the number will be translated
            # back
            if translated is not None:
                return translated
        return number


class Almenac:
    """
    A set of maps, from how to translate from a source to a destination
    """
    def __init__(self):
        self.maps = {}

    def add_map(self, src_name: str, dst_name: str, map: Map):
        self.maps[src_name] = (dst_name, map)
    
    def __str__(self):
        return "".join(f"{src} => {dst}:\n{map}\n" for src,(dst,map) in self.maps.items())
    
    def translate(self, src_name: str, dst_name: str, number):
        """
        Translate a number from a source to a destination
        
        It assumes that destination is reachable by iteration from the almenac
        """
        cur_name = src_name
        while True:
            if cur_name == dst_name:
                return number
            
            # Do single translation
            cur_name, map = self.maps[cur_name]
            number = map.translate(number)

class Input:
    def __init__(self, f):
        """
        Parse the input file
        
        f can be either a filename or a file-like object
        """
        if type(f) == str:
            f = open(f,"r")
        

        cur_map = None
        self.almenac = Almenac()
        for line in f:
            # make sure there are no whitespaces that interferes
            line = line.strip()

            match_seeds = m = re.search(r'seeds: (.*)', line)
            match_map = m = re.search(r'(.*)-to-(.*) map:', line)
            match_table = m = re.search(r'(.+)', line)

            if match_seeds:
                # seed line
                self.seeds = [int(v) for v in match_seeds.group(1).split(" ")]

            elif match_map:
                # new map
                src_name = match_map.group(1)
                dst_name = match_map.group(2)

                # keeping the Map as an object (such as an instance of a class,
                # or a list), we can assign the object here, and then keep a
                # reference and modify it later without having to re-add it to
                # the input almenac
                cur_map = Map()
                self.almenac.add_map(src_name, dst_name, cur_map)
            
            elif match_table:
                dst, src, length = [int(v) for v in match_table.group(1).split(" ")]
                cur_map.add_range(MapRange(dst, src, length))

    def __str__(self):
        return f"seeds: {self.seeds}\n\n{self.almenac}"

class Problem:
    def __init__(self, input):
        self.seeds = input.seeds
        self.almenac = input.almenac

    def run(self):
        min_location = None
        for seed in self.seeds:
            location = self.almenac.translate('seed', 'location', seed)
            print(f"seed={seed} => location={location}")
            if min_location is None or min_location > location:
                min_location = location
        return min_location

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <input file>")
        sys.exit(1)

    input = Input(sys.argv[1])

    # Enable for debugging
    #print(input)

    print("\nPart1:\n")

    part1 = Problem(input)
    part1_result = part1.run()

    print(f"\nPart1: {part1_result}\n")
