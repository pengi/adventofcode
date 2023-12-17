#!/bin/env python3

import sys
import re

class SeedRange:
    """
    Represent a single range of seeds

    start is inclusive
    end is exclusive

    if end is missing, assume a single seed
    """
    def __init__(self, start, end=None):
        if end is None:
            end = start+1

        self.start = start
        self.end = end
    
    def len(self):
        return self.end - self.start

    def is_valid(self):
        """
        Determines if range is valid
        
        Invalid range is if start is equal or after end
        """
        return self.start <= self.end

    def __str__(self):
        if self.len() == 1:
            return f"{self.start}"
        else:
            return f"{self.start}-{self.end-1}"
    
    def merge(self, range):
        """
        Merge two ranges

        If two ranges can be merged, return a merged range
        
        If not possible, return None
        """
        if self.end >= range.start and range.end >= self.start:
            return SeedRange(
                min(self.start, range.start),
                max(self.end, range.end)
            )
    
    def remove(self, range):
        """
        Remove out a range current range

        Return a list of ranges that corresponds to remaning pieces of the
        range.

        Note that this does not return a SeedRangeSet.
        """
        result = []

        # Is there a part below input range?
        if self.start < range.start:
            result.append(SeedRange(self.start, min(self.end,range.start)))

        # Is there a part after input range?
        if self.end > range.end:
            result.append(SeedRange(max(self.start,range.end), self.end))
        
        return result

class SeedRangeSet:
    """
    Represent a set of ranges
    
    Given the set of ranges, it is possible to add set operations:

    - union - combine two sets to a new set, and optimize the use of sets
    - difference - remove one set from the other, and return an optimized set
    """
    def __init__(self):
        self.ranges = []
    
    def add_range(self, range: SeedRange):
        result = SeedRangeSet()

        for cur in self.ranges:
            merged = cur.merge(range)

            # If a range can be merged, then "consume" it to the input range,
            # otherwise keep it untouched
            if merged is None:
                result.ranges.append(cur)
            else:
                range = merged
        
        # The input range should be non-overlapping at this point, so add to
        # result
        result.ranges.append(range)

        return result
    
    def __add__(self, seeds):
        """
        Merge two SeedRangeSet or SeedRangeSet with a SeedRange

        Can be used both as:
        a = b + c

        or:
        a += c
        """
        result = self
        if type(seeds) == SeedRange:
            result = result.add_range(seeds)
        elif type(seeds) == SeedRangeSet:
            for range in seeds.ranges:
                result = result.add_range(range)
        else:
            raise TypeError(f"Invalid type {type(seeds)}")
        return result

    def __sub__(self, seeds):
        """
        Remove one SeedRangeSet from the other

        Can be used both as:
        a = b - c

        or:
        a -= c
        """
        result = self

        for range in seeds.ranges:
            new_set = SeedRangeSet()
            for cur in result.ranges:
                remains = cur.remove(range)
                new_set.ranges += remains
            result = new_set
        
        return result

    def __str__(self) -> str:
        return ", ".join(str(range) for range in self.ranges)

    def min(self) -> int:
        min_location = None
        for range in self.ranges:
            if min_location is None or min_location > range.start:
                min_location = range.start
        return min_location

class MapRange:
    """
    A translation range, where a set of numbers may be translated to another
    range
    """
    def __init__(self, dst: int, src: int, length: int):
        self.dst = dst
        self.src = src
        self.length = length
    
    def __str__(self) -> str:
        return f"{self.src} - {self.src+self.length-1} => {self.dst} - {self.dst+self.length-1}"

    def _overlap(self, seeds: SeedRange) -> SeedRange:
        """
        Return SeedRange that overlap with input range
        
        Return None if not overlapping
        """
        range = SeedRange(
            max(self.src, seeds.start),
            min(self.src + self.length, seeds.end)
        )
        if not range.is_valid():
            return None
        return range

    def translate(self, seeds: SeedRangeSet) -> (SeedRangeSet, SeedRangeSet):
        """
        Translate a number given the current range

        returns a tuple of two SeedRangeSet:s, one with translated values and
        one with source seeds used in translation
        """
        dst_seeds = SeedRangeSet()
        src_seeds = SeedRangeSet()
        for seedrange in seeds.ranges:
            overlap = self._overlap(seedrange)
            if overlap is None:
                continue
            
            dst_seeds += SeedRange(
                    overlap.start + self.dst - self.src,
                    overlap.end + self.dst - self.src
                )
            src_seeds += overlap
        return (dst_seeds, src_seeds)

class Map:
    """
    A translation from a set of numbers to another, where ranges of numbers may
    be translated
    """
    def __init__(self):
        self.ranges = []

    def add_range(self, range: MapRange) -> None:
        self.ranges.append(range)
    
    def __str__(self) -> str:
        return "".join([f"{r}\n" for r in self.ranges])
    
    def translate(self, seeds: SeedRangeSet) -> SeedRangeSet:
        """
        Translate a number given current map
        """
        result_seeds = SeedRangeSet()
        for maprange in self.ranges:
            (dst_seeds, src_seeds) = maprange.translate(seeds)

            # Remove source seeds from original set
            seeds -= src_seeds

            # Add new seeds to new set
            result_seeds += dst_seeds

        # Add remaining non-translated seeds
        result_seeds += seeds
        return result_seeds


class Almenac:
    """
    A set of maps, from how to translate from a source to a destination
    """
    def __init__(self):
        self.maps = {}

    def add_map(self, src_name: str, dst_name: str, map: Map) -> None:
        self.maps[src_name] = (dst_name, map)
    
    def __str__(self) -> str:
        return "".join(f"{src} => {dst}:\n{map}\n" for src,(dst,map) in self.maps.items())
    
    def translate(self, src_name: str, dst_name: str, seeds: SeedRangeSet) -> SeedRangeSet:
        """
        Translate a number from a source to a destination
        
        It assumes that destination is reachable by iteration from the almenac
        """
        cur_name = src_name
        while True:
            if cur_name == dst_name:
                break
            
            # Do single translation
            print(f"  - {cur_name}: {seeds}")
            cur_name, map = self.maps[cur_name]
            seeds = map.translate(seeds)
        print(f"  - {cur_name}: {seeds}")
        return seeds

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
                seednums = [int(v) for v in match_seeds.group(1).split(" ")]

                # seed line, as part1
                self.seeds1 = SeedRangeSet()
                for v in seednums:
                    self.seeds1 += SeedRange(v)
                
                self.seeds2 = SeedRangeSet()
                for i in range(0, len(seednums), 2):
                    self.seeds2 += SeedRange(
                        seednums[i],
                        seednums[i] + seednums[i+1]
                    )

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
        return \
            f"seeds part 1: {self.seeds1}\n" + \
            f"seeds part 2: {self.seeds2}\n" + \
            f"{self.almenac}"

class Problem:
    def __init__(self, almenac, seeds):
        self.seeds = seeds
        self.almenac = almenac

    def run(self):
        min_location = None
        seeds = self.seeds
        print(f"seeds={seeds}")
        print("")
        locations = self.almenac.translate('seed', 'location', seeds)
        print("")
        print(f"locations={locations}")

        return locations.min()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <input file>")
        sys.exit(1)

    input = Input(sys.argv[1])

    # Enable for debugging
    print(input)

    print("\nPart1:\n")
    part1 = Problem(input.almenac, input.seeds1)
    part1_result = part1.run()
    print(f"\nPart1: {part1_result}\n")

    print("\nPart2:\n")
    part2 = Problem(input.almenac, input.seeds2)
    part2_result = part2.run()
    print(f"\nPart2: {part2_result}\n")
