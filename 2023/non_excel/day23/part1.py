#!/bin/env python3

import sys
import re

def multirange(*dims):
    """
    generate a multi-dimensional range

    >>> list(multirange(2,3))
    [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2), (1, 2)]

    >>> list(multirange(1,2,1))
    [(0, 0, 0), (0, 1, 0)]

    >>> list(multirange(0, 12, 17))
    []
    """
    if len(dims) > 0:
        last = dims[-1]
        for i in range(last):
            for nodes in multirange(*dims[:-1]):
                yield nodes + (i,)
    else:
        yield ()

class PxlMap:
    def __init__(self, pxls):
        self.pxls = [[x for x in xs] for xs in pxls]
    
    def __str__(self):
        return "\n".join("".join(row) for row in self.pxls)

    def width(self):
        return len(self.pxls[0])

    def height(self):
        return len(self.pxls)
    
    def get(self, x, y):
        if x < 0 or y < 0 or x >= self.width() or y >= self.width():
            return '#'
        else:
            return self.pxls[y][x]
    
    def exits(self, x, y):
        if self.get(x,y) == '>':
            yield (x+1, y)
        elif self.get(x,y) == '^':
            yield (x, y-1)
        elif self.get(x,y) == '<':
            yield (x-1, y)
        elif self.get(x,y) == 'v':
            yield (x, y+1)
        elif self.get(x,y) == '.':
            if self.get(x+1, y) != '#':
                yield  (x+1, y)
            if self.get(x, y-1) != '#':
                yield  (x, y-1)
            if self.get(x-1, y) != '#':
                yield  (x-1, y)
            if self.get(x, y+1) != '#':
                yield  (x, y+1)
        else:
            return
            yield
    
    def get_nodes(self):
        for x, y in multirange(self.width(), self.height()):
            if self.get(x,y) != '#':
                if y == 0: # top is start
                    yield ((x, y), 'S')
                elif y == self.height() - 1: # bottom is end
                    yield ((x, y), 'E')
                elif len(list(self.exits(x, y))) > 2:
                    yield ((x, y), 'i')
    
    def _walk(self, x, y, visited):
        steps = 1
        while True:
            #print(f"walk {x},{y}")
            visited[y][x] = True

            if y == 0 or y == self.height()-1:
                return (x, y, steps)
            
            exits = list(self.exits(x, y))
            new_exits = [(ex,ey) for ex,ey in exits if not visited[ey][ex]]
            
            if len(exits) > 2:
                return (x, y, steps)
            if len(new_exits) == 0:
                return None
            x, y = new_exits[0]
            steps += 1

    def get_nbr_nodes(self, x, y):
        visited = [[False for x in xs] for xs in self.pxls]
        visited[y][x] = True
        for nx, ny in self.exits(x, y):
            #print(f"exits {nx},{ny}")
            nbr = self._walk(nx, ny, visited)
            if nbr is not None:
                yield nbr

class NodeMap:
    def __init__(self, pxlmap):
        self.pxlmap = pxlmap
        nodes = list(self.pxlmap.get_nodes())

        # conversion between coordinate and id
        self.coords = [crd for crd, variant in nodes]
        self.ids = {crd: i for i, (crd, variant) in enumerate(nodes)}

        # start end end id
        self.start = [id for id, (crd, variant) in enumerate(nodes) if variant == 'S'][0]
        self.end = [id for id, (crd, variant) in enumerate(nodes) if variant == 'E'][0]

        # links
        self.nbrs = [[(self.ids[(nbrx, nbry)], steps) for nbrx, nbry, steps in self.pxlmap.get_nbr_nodes(*crd)] for crd, variant in nodes]
    
    def _get_paths(self, cur, end, visited):
        if cur == end:
            yield (0, [cur])
            return

        visited[cur] = True
        
        for nbr, steps in self.nbrs[cur]:
            if visited[nbr] == False:
                for remain, remain_path in self._get_paths(nbr, end, visited):
                    yield steps + remain, [cur] + remain_path

        visited[cur] = False

    def longest_path(self):
        visited = [False for x in self.coords]
        paths = list(self._get_paths(self.start, self.end, visited))
        return paths

class Input:
    def __init__(self, f):
        """
        Parse the input file
        
        f can be either a filename or a file-like object
        """
        if type(f) == str:
            f = open(f,"r")
        
        self.pxlmap = PxlMap((pxl for pxl in line.strip()) for line in f.readlines() if line.strip() != "")

class Part1:
    def __init__(self, input):
        self.pxlmap = input.pxlmap

    def run(self):
        #print(str(self.pxlmap))
        
        nodemap = NodeMap(self.pxlmap)
        #print(nodemap.coords)
        #print(nodemap.nbrs)

        paths = nodemap.longest_path()
        paths.sort()
        #for path in paths:
        #    print(path)

        longest_len, longest_path = paths[-1]
        return longest_len

if __name__ == "__main__":
    import doctest
    failures, tests = doctest.testmod()
    if failures > 0:
        sys.exit(1)

    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <input file>")
        sys.exit(1)

    input = Input(sys.argv[1])
    
    part1 = Part1(input)
    print(f"Part1: {part1.run()}")

