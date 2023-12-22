#!/bin/env python3

import sys
import re
import copy

from collections import deque

_sig_inv = {
    'low': 'high',
    'high': 'low'
}

class Module:
    def __init__(self, outputs):
        self.outputs = outputs
    
    def register_input(self, name):
        pass
    
    def _send(self, value):
        for output in self.outputs:
            yield (output, value)
    
    def _nop(self):
        return
        yield

    def signal(self, source, value):
        return
        yield # make sure it's a generator

class FlipFlop(Module):
    def __init__(self, outputs):
        super().__init__(outputs)
        self.state = 'low'
    
    def signal(self, source, value):
        if value == 'low':
            self.state = _sig_inv[self.state]
            return self._send(self.state)
        else:
            return self._nop()


class Conjunction(Module):
    def __init__(self, outputs):
        super().__init__(outputs)
        self.inputs = {}
    
    def register_input(self, name):
        self.inputs[name] = 'low'

    def signal(self, source, value):
        self.inputs[source] = value
        if any(inp == 'low' for inp in self.inputs.values()):
            return self._send('high')
        else:
            return self._send('low')

class Broadcast(Module):
    def __init__(self, outputs):
        super().__init__(outputs)
    
    def signal(self, source, value):
        return self._send(value)

class Network:
    def __init__(self):
        self.modules = {}

    def add_module(self, name, module):
        self.modules[name] = module
    
    def connect(self):
        for source, module in self.modules.items():
            for output in module.outputs:
                if output in self.modules:
                    self.modules[output].register_input(source)
    
    def send(self, source = 'button', value = 'low', dest = 'broadcaster'):
        signals = deque([(source, dest, value)])
        sigcount = {'low': 0, 'high': 0}
        while len(signals) > 0:
            source, dest, value = signals.popleft()
            #print(f"{source} -{value}-> {dest}")
            sigcount[value] += 1
            if dest in self.modules:
                for new_dest, new_value in self.modules[dest].signal(source, value):
                    signals.append((dest, new_dest, new_value))
        return sigcount

class Input:
    def __init__(self, f):
        """
        Parse the input file
        
        f can be either a filename or a file-like object
        """
        if type(f) == str:
            f = open(f,"r")
        
        self.network = Network()
        for l in f:
            m = re.fullmatch(r"([&%]*)([a-z]*) -> (.*)", l.strip())
            if m:
                mod_type, mod_name, outputs_str = m.groups()
                outputs = [outp.strip() for outp in outputs_str.split(',')]
                if mod_type == '':
                    module = Broadcast(outputs)
                elif mod_type == '%':
                    module = FlipFlop(outputs)
                elif mod_type == '&':
                    module = Conjunction(outputs)
                self.network.add_module(mod_name, module)

class Part1:
    def __init__(self, input):
        self.network = copy.deepcopy(input.network)
        self.network.connect()

    def run(self):
        count_low = 0
        count_high = 0
        for i in range(1000):
            runcount = self.network.send('button', 'low')
            count_low += runcount['low']
            count_high += runcount['high']
        return count_low * count_high

if __name__ == "__main__":
    import doctest
    doctest.testmod()

    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <input file>")
        sys.exit(1)

    input = Input(sys.argv[1])
    
    part1 = Part1(input)
    print(f"Part1: {part1.run()}")
