#!/bin/env python3

import sys
import re

from collections import deque

_bg_set = "\x1b[44m"
_bg_clr = "\x1b[0m"

class Ant:
    def __init__(self, x, y, dist):
        self.x = x
        self.y = y
        self.dist = dist
    
    def __lt__(self, other):
        return self.dist < other.dist

    def __str__(self):
        return f"<Ant @{self.dist} {self.x},{self.y}>"
    
    def walk(self):
        yield Ant(self.x+1, self.y, self.dist+1)
        yield Ant(self.x, self.y+1, self.dist+1)
        yield Ant(self.x-1, self.y, self.dist+1)
        yield Ant(self.x, self.y-1, self.dist+1)

class Field:
    def __init__(self, cells):
        cells = [[x for x in xs] for xs in cells]
        self.cells = [[x == '#' for x in xs] for xs in cells]
        
        self.start = None
        for y,row in enumerate(cells):
            for x,c in enumerate(row):
                if c == 'S':
                    self.start = (x,y)
        
        self.reset()
    
    def reset(self):
        self.visited = [[False for x in xs] for xs in self.cells]

    def can_visit(self, x, y):
        if y<0 or y>=len(self.visited):
            return False
        if x<0 or x>=len(self.visited[y]):
            return False
        if self.visited[y][x]:
            return False
        if self.cells[y][x]:
            return False
        return True

    def visit(self, x, y):
        if not self.can_visit(x, y):
            return False
        self.visited[y][x] = True
        return True
    
    def print(self):
        for vrow, crow in zip(self.visited, self.cells):
            line = ""
            last_v = False
            for v, c in zip(vrow, crow):
                c_str = '#' if c else '.'
                if v != last_v:
                    if v:
                        line += _bg_set
                    else:
                        line += _bg_clr
                    last_v = v
                line += c_str
            if last_v:
                line += _bg_clr
            print(line)
        
    def count_visited(self, fn = None):
        if fn is None:
            fn = lambda x, y: 1
        return sum(
            sum(fn(x,y) for x,vis in enumerate(vrow) if vis)
            for y,vrow in enumerate(self.visited)
        )

    def dimensions(self):
        return len(self.cells[0]), len(self.cells)

class Input:
    def __init__(self, f):
        """
        Parse the input file
        
        f can be either a filename or a file-like object
        """
        if type(f) == str:
            f = open(f,"r")

        self.field = Field(list(l.strip()) for l in f if l.strip() != "")
        

class Part1:
    def __init__(self, input, max_dist):
        self.field = input.field
        self.max_dist = max_dist

    def run(self):
        self.field.reset()
        start_x, start_y = self.field.start

        queue = deque()
        queue.append(Ant(start_x, start_y, 0))

        while len(queue) > 0:
            ant = queue.popleft()
            if ant.dist <= self.max_dist:
                if self.field.visit(ant.x, ant.y):
                    queue.extend(a for a in ant.walk() if self.field.can_visit(a.x, a.y))

        parity = (start_x + start_y + self.max_dist) % 2
        return self.field.count_visited()
        #return self.field.count_visited(lambda x, y: (x+y)%2 == parity)
        
class Part2:
    def __init__(self, input):
        self.field = input.field

    def _coverage(self, sx, sy, steps):
        self.field.reset()

        queue = deque()
        queue.append(Ant(sx, sy, 0))
        
        while len(queue) > 0:
            ant = queue.popleft()
            if ant.dist <= steps:
                if self.field.visit(ant.x, ant.y):
                    queue.extend(a for a in ant.walk() if self.field.can_visit(a.x, a.y))
        return sum((
            self.field.count_visited(lambda x, y: (x+y)%2 == 0),
            self.field.count_visited(lambda x, y: (x+y)%2 == 1)
        ))

    def run(self):
        self.field.reset()
        
        # Input data:
        # steps = 26501365
        steps = 15


        # There are some important properties for this to easily working
        #
        # 1. start location is centered
        #
        sx, sy = self.field.start
        dx, dy = self.field.dimensions()
        if sx*2 + 1 != dx or sy*2 + 1 != dy:
            print("Non-centered start location")
            return None
        #
        # 2. A square play field, which simplifies calculations a lot
        #
        if dx != dy:
            print("Non-square field")
            return None
        #
        # 3. border of field is empty from rocks, so it's possible to follow
        #    from corner to corner as quickly as possible, without being
        #    affected by field
        #
        if any(self.field.cells[0]):
            print("Top border is obstructed")
            return None
        if any(self.field.cells[dy-1]):
            print("Bottom border is obstructed")
            return None
        if any(crow[0] for crow in self.field.cells):
            print("Left border is obstructed")
            return None
        if any(crow[dx-1] for crow in self.field.cells):
            print("Right border is obstructed")
            return None
        #
        # 4. Cross from start location to borders are free, so it's quick to
        #    reach
        #
        if any(self.field.cells[sy]):
            print("Start horizontal line is obstructed")
            return None
        if any(crow[sx] for crow in self.field.cells):
            print("Start vertical line is obstructed")
            return None
        #
        #
        # 5. There are not enough obstructions if a cell is reachable with
        #    infinite number of steps in inner repetitions of the field, then
        #    they are reachable in all inner repetitions of the field
        #
        #    This is just assumed, and wont be tested
        #

        #
        # Lets start calculation
        #
        # There are a couple of types of repeptions. Each cell is treated as an
        # entire input field:
        #
        # ....t....
        # ...0T2...
        # ..01i32..
        # .01iii32.
        # lLiiSiiRr
        # .7iiii54.
        # ..67i54..
        # ...6B4...
        # ....b....
        #
        # In this case S just indicates the starting location, but have same
        # coverage as i/inner
        #
        # Looking at T and t, the amount of steps left into T (which might
        # overflow into t) is:
        #)
        # ovf = (steps - (sy+1)) % dy
        #
        # Which is the same amount of steps into any of T,R,B,L
        #
        # There are two distinct possible options:
        #
        # option 1: ovf < sx
        #
        # In this case, the top corner reaches into the one below, thus the
        # pattern above
        #
        # ....... ....... .......
        # ....... ....... .......
        # ....... ....... .......
        # ....... ...t... .......
        # ....... ....... .......
        # ....... ...#... .......
        # ....... ..###.. .......
        #
        # ....... .#####. .......
        # ....... ####### .......
        # ......# ####### #......
        # ...0.## ###T### ##.2...
        # ....### ####### ###....
        # ...#### ####### ####...
        # ..##### ####### #####..
        #
        # option 2: ovf >= sx
        #
        # In this case, the top corner reaches into the fields beside instead,
        # and the block below is full
        #
        # example: ovf = 6, sx = 3
        #
        # ....... ....... .......
        # ....... ...#... .......
        # ....... ..###.. .......
        # ...0... .##T##. ...2...
        # ....... ####### .......
        # ......# ####### #......
        # .....## ####### ##.....
        #
        # ....### ####### ###....
        # ...#### ####### ####...
        # ..##### ####### #####..
        # .##1### ###i### ###3##.
        # ####### ####### #######
        # ####### ####### #######
        # ####### ####### #######
        #
        # Both cases can be treated as same, given that:
        #
        # In first case, simply increase ovf with the dimension (and reduce
        # inner tiles with 1).
        #
        # tile t will have 0 cells in second case

        # dx == dy and sx == sy, so it's just a qustion of path. Therefore:
        dim = dx
        mid = sx

        ovf   = (steps - (mid+1)) % dim
        tiles = (steps - (mid+1)) // dim

        if ovf < mid:
            ovf += dim
            tiles -= 1

        #print(self.field.dimensions())
        #print(self.field.start)
#
        #print(ovf)
        #print(tiles)

        coverage = {
            'i': self._coverage(mid,   mid, mid + mid + 30), # full tile
            
            'l': self._coverage(dim-1, mid  , ovf-dim),
            'L': self._coverage(dim-1, mid  , ovf),
            '0': self._coverage(dim-1, 0    , ovf-1-mid),
            '1': self._coverage(dim-1, 0    , ovf-1-mid+dim),
            
            't': self._coverage(mid  , dim-1, ovf-dim),
            'T': self._coverage(mid  , dim-1, ovf),
            '2': self._coverage(0    , dim-1, ovf-1-mid),
            '3': self._coverage(0    , dim-1, ovf-1-mid+dim),
            
            'r': self._coverage(0    , mid  , ovf-dim),
            'R': self._coverage(0    , mid  , ovf),
            '4': self._coverage(0    , 0    , ovf-1-mid),
            '5': self._coverage(0    , 0    , ovf-1-mid+dim),
            
            'b': self._coverage(mid  , 0    , ovf-dim),
            'B': self._coverage(mid  , 0    , ovf),
            '6': self._coverage(0    , 0    , ovf-1-mid),
            '7': self._coverage(0    , 0    , ovf-1-mid+dim),
        }


        tile_count = {
            'i': tiles*(tiles+1)*2 + 1,
            
            'l': 1,
            'L': 1,
            '0': tiles+1,
            '1': tiles,
            
            't': 1,
            'T': 1,
            '2': tiles+1,
            '3': tiles,
            
            'r': 1,
            'R': 1,
            '4': tiles+1,
            '5': tiles,
            
            'b': 1,
            'B': 1,
            '6': tiles+1,
            '7': tiles,
        }

        count = 0
        for ttype in tile_count.keys():
            #print(f"{ttype} - {tile_count[ttype]} - {coverage[ttype]}")
            count += tile_count[ttype] * coverage[ttype]

        # Test data:
        #  12 steps on empty field, all cells:   313, even cells:   ???
        #  15 steps on empty field, all cells:   481, even cells:   256
        # 150 steps on empty field, all cells: 45301, even cells: 22801

        return count

if __name__ == "__main__":
    import doctest
    doctest.testmod()

    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <input file> <steps>")
        sys.exit(1)

    input = Input(sys.argv[1])
    
    max_dist = 64
    if len(sys.argv) >= 3:
        max_dist = int(sys.argv[2])

    part1 = Part1(input, max_dist)
    print(f"Part1: {part1.run()}")

    part2 = Part2(input)
    print(f"Part2: {part2.run()}")
