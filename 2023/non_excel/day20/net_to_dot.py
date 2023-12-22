#!/bin/env python3

import sys
import re
import copy

from part2 import Module, FlipFlop, Conjunction, Broadcast, Input

class Output(Module):
    def __init__(self):
        super().__init__([])

nodestyle = {
    FlipFlop: {
        'shape': 'diamond',
        'style': 'filled',
        'color': 'grey56',
        'fillcolor': 'grey76'
    },
    Conjunction: {
        'shape': 'cds',
        'style': 'filled',
        'color': 'burlywood4',
        'fillcolor': 'burlywood'
    },
    Broadcast: {
        'style': 'filled',
        'color': 'blue3',
        'fillcolor': 'deepskyblue2'
    },
    Output: {
        'style': 'filled',
        'color': 'red',
        'fillcolor': 'indianred1'
    }
}

def styletag(args):
    return "[" + " ".join(f'{k}="{v}"' for k,v in args.items()) + "]"

class ToDot:
    def __init__(self, input):
        self.network = copy.deepcopy(input.network)
        self.network.add_module('rx', Output())
        self.network.connect()

    def todot(self):
        print("digraph {")
        print("  rankdir=LR;")
        for name, module in self.network.modules.items():
            output_str = "{" + " ".join(outp for outp in module.outputs if outp in self.network.modules) + "}"
            print(f"  {name} -> {output_str};")
            if type(module) in nodestyle:
                print(f"  {name} {styletag(nodestyle[type(module)])}")
        print("}")

if __name__ == "__main__":
    import doctest
    doctest.testmod()

    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <input file>")
        sys.exit(1)

    input = Input(sys.argv[1])
    
    dot = ToDot(input)
    dot.todot()
