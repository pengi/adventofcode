#!/bin/env python3

import sys
import re
import math

class Obj:
    def __init__(self, x, y, w):
        self.x = x
        self.y = y
        self.w = w
    
    def is_adj(self, other):
        if self.y - other.y > 1 or self.y - other.y < -1:
            return False
        if other.x + other.w < self.x:
            return False
        if self.x + self.w < other.x:
            return False
        return True


class ObjNum(Obj):
    def __init__(self, x, y, w, num):
        super().__init__(x, y, w)
        self.num = num
        
    def __str__(self):
        return f"<Obj {self.num:5} {self.x:2}-{self.x+self.w-1:2},{self.y:2}>"

class ObjSym(Obj):
    def __init__(self, x, y, w, sym):
        super().__init__(x, y, w)
        self.sym = sym
        
    def __str__(self):
        return f"<Obj {self.sym:5} {self.x:2}-{self.x+self.w-1:2},{self.y:2}>"

class World:
    def __init__(self, map):
        self.map = map
        self.objs = []
    
    def __str__(self):
        return "Map:\n---\n" + "\n".join(self.map) + "\n---\n" + "\n".join(str(obj) for obj in self.objs) + "\n---\n"
    
    def get(self,x,y):
        """
        Get character for coordinate
        
        If outside of map, just assume it's infinit and blank with .
        """
        if y<0 or y>=len(self.map):
            return '.'
        if x<0 or x>=len(self.map[y]):
            return '.'
        return self.map[y][x]

    def add_obj(self, obj: Obj):
        self.objs.append(obj)
    
    def obj_is_part(self, obj):
        """
        Return if obj has an adjecent symbol (non-digit or .)
        """
        non_sym = "0123456789."

        # Test directly to the left
        if non_sym.find(self.get(obj.x-1, obj.y)) < 0:
            return True
        
        # Test directly to the right
        if non_sym.find(self.get(obj.x+obj.w, obj.y)) < 0:
            return True
        
        # Iterate the line above and below
        for x in range(obj.x-1, obj.x+obj.w+1):
            if non_sym.find(self.get(x, obj.y-1)) < 0:
                return True
            if non_sym.find(self.get(x, obj.y+1)) < 0:
                return True

        return False
        
class Input:
    def _parse_values(self, values):
        return [int(v) for v in values.split(" ") if v != ""]
    
    def __init__(self, f):
        """
        Parse the input file
        
        f can be either a filename or a file-like object
        """
        if type(f) == str:
            f = open(f,"r")

        map = [l.strip() for l in f.readlines() if l.strip() != ""]
        self.world = World(map)

        for y, line in enumerate(map):
            for m in re.finditer(r"([0-9]+)", line):
                x, x2 = m.span()
                num = int(m.group(1))
                self.world.add_obj(ObjNum(x, y, x2-x, num))
            for m in re.finditer(r"([^0-9.])", line):
                x, x2 = m.span()
                self.world.add_obj(ObjSym(x, y, x2-x, m.group(1)))

class Part1:
    def __init__(self, world):
        self.world = world

    def run(self):
        num_sum = 0
        for obj in self.world.objs:
            if isinstance(obj, ObjNum):
                if self.world.obj_is_part(obj):
                    num_sum += obj.num
        return num_sum

class Part2:
    def __init__(self, world):
        self.world = world

    def run(self):
        num_sum = 0
        for obj in self.world.objs:
            if isinstance(obj, ObjSym) and obj.sym == '*':
                nums = []
                for numobj in (o for o in self.world.objs if isinstance(o,ObjNum)):
                    if numobj.is_adj(obj):
                        nums.append(numobj)
                if len(nums) == 2:
                    ratio = nums[0].num * nums[1].num
                    num_sum += ratio
        return num_sum

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <input file>")
        sys.exit(1)

    world = Input(sys.argv[1]).world

    #print(f"{world}")

    part1 = Part1(world)
    print(f"Part1: {part1.run()}")

    part2 = Part2(world)
    print(f"Part2: {part2.run()}")
