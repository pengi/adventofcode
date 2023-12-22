#!/bin/env python3

import sys
import re
import copy
import math

from collections import deque

_sig_inv = {
    'low': 'high',
    'high': 'low'
}

class Module:
    # Node style when rendering as .dot
    DOT_STYLE = {}

    def __init__(self, outputs):
        self.outputs = [out for out in outputs]
        self.inputs = {}
    
    def apply_reconnect(self, orig, new):
        new_outputs = []
        for output in self.outputs:
            new_outputs.append(output)
            if output == orig:
                new_outputs.append(new)
        self.outputs = new_outputs
    
    def filter_outputs(self, names):
        self.outputs = [outp for outp in self.outputs if outp in names]

    def register_input(self, name):
        self.inputs[name] = 'low'
    
    def _send(self, value):
        for output in self.outputs:
            yield (output, value)
    
    def _nop(self):
        return
        yield

    def signal(self, source, value):
        return
        yield # make sure it's a generator
    
    def state_str(self):
        """
        Print out state, as a hashable object

        Used for tracking periodicity in runtimes
        """
        return ""

    def optimize(self, name, network):
        return self.copy(), None, []

class LogModule(Module):
    """
    Not intended to be part of network, but just
    temporarily when running subsets for optimization
    """
    def __init__(self):
        super().__init__([])
        self.log = []

    def signal(self, source, value):
        self.log.append((source, value))
        return self._nop()

class FlipFlop(Module):
    DOT_STYLE = {
        'shape': 'diamond',
        'style': 'filled',
        'color': 'grey56',
        'fillcolor': 'grey76'
    }

    def __init__(self, outputs):
        super().__init__(outputs)
        self.state = 'low'
    
    def copy(self):
        return FlipFlop(self.outputs)
    
    def signal(self, source, value):
        if value == 'low':
            self.state = _sig_inv[self.state]
            return self._send(self.state)
        else:
            return self._nop()
        
    def state_str(self):
        return self.state

class Conjunction(Module):
    DOT_STYLE = {
        'shape': 'cds',
        'style': 'filled',
        'color': 'burlywood4',
        'fillcolor': 'burlywood'
    }
    
    def copy(self):
        return Conjunction(self.outputs)

    def signal(self, source, value):
        self.inputs[source] = value
        if any(inp == 'low' for inp in self.inputs.values()):
            return self._send('high')
        else:
            return self._send('low')

    def optimize(self, name, network):
        # If outputs are all flipflops, or a subtree of only conjunction nodes
        # downstream (until output), then this can be replaced with a filtered
        # conjunction
        upstream = network.isolate(name)
        can_be_filtered_conjunction = True
        for up_name, up_mod in upstream.modules.items():
            if type(up_mod) == FlipFlop:
                pass
            elif type(up_mod) == Broadcast:
                pass
            elif up_name == name:
                pass
            else:
                can_be_filtered_conjunction = False
        
        if can_be_filtered_conjunction:
            # if any conjunction outputs has flipflops as downstream, we can't
            # optimize, since they may then invert the high signal to a low
            # which could trigger a flipflop
            for outp in self.outputs:
                mod = network.modules[outp]
                if type(mod) == Conjunction:
                    downstream = network.downstream(outp)
                    for dsmod in downstream.values():
                        if type(dsmod) != Conjunction and type(dsmod) != Output:
                            can_be_filtered_conjunction = False
                elif type(mod) != FlipFlop:
                    can_be_filtered_conjunction = False

        if can_be_filtered_conjunction:
            new_node = FilteredConjunction(self.outputs)
            return None, new_node, [name]
        
        
        # A conjunction module having only inputs from a single chain:
        # broadcaster -> periodic -> conjunction, then they can be combined all
        # to a periodic source themselves
        periodics = []
        inp_nodes = (network.modules[inp] for inp in self.inputs.keys())
        for conj_mod in inp_nodes:
            if type(conj_mod) != Conjunction:
                periodics = None
                break
            if len(conj_mod.inputs.keys()) != 1:
                periodics = None
                break
            period_name = list(conj_mod.inputs.keys())[0]
            period_mod = network.modules[period_name]
            if type(period_mod) != Periodic:
                periodics = None
                break
            if len(period_mod.inputs.keys()) != 1:
                periodics = None
                break
            broadcast_mod = network.modules[list(period_mod.inputs.keys())[0]]
            if type(broadcast_mod) != Broadcast:
                periodics = None
                break
            periodics.append((period_name, period_mod))
        
        if periodics is not None:
            # can be converted
            interval = math.lcm(*[per.interval for nm, per in periodics])
            offset = interval-1 # Fixme: this isn't correct generally, but for now

            nm, per = periodics[0]
            # Replace inputs for first n
            return None, Periodic(self.outputs, interval, interval-1), [nm]
        
        return self.copy(), None, []

class FilteredConjunction(Module):
    DOT_STYLE = {
        'shape': 'cds',
        'style': 'filled',
        'color': 'gold3',
        'fillcolor': 'gold1'
    }
    def __init__(self, outputs):
        super().__init__(outputs)
        self.last_out = 'low'

    def copy(self):
        return FilteredConjunction(self.outputs)

    def signal(self, source, value):
        self.inputs[source] = value
        if any(inp == 'low' for inp in self.inputs.values()):
            if self.last_out != 'high':
                self.last_out = 'high'
                return self._send('high')
            else:
                return self._nop()
        else:
            self.last_out = 'low'
            return self._send('low')
        
    def optimize(self, name, network):
        # A filtered conjunction dependent only on flipflops and input may be
        # converted to a periodic node

        upstream = network.isolate(name)
        can_be_periodic = True
        for up_name, up_mod in upstream.modules.items():
            if type(up_mod) == FlipFlop:
                pass
            elif type(up_mod) == Broadcast:
                pass
            elif up_name == name:
                pass
            else:
                can_be_periodic = False
        
        if can_be_periodic:
            mod_names = upstream.modules.keys()
            states = {}
            i = 0
            log = LogModule()
            upstream.add_module('log', log)
            upstream.modules[name].outputs.append('log')
            offset = None
            while True:
                log.log = []
                upstream.send()
                if log.log != []:
                    src, value = log.log[0]
                    if value == 'low':
                        offset = i
                #    print(f"t[{i}] = {log.log}")

                statearg = "|".join(upstream.modules[name].state_str() for name in mod_names)
                if i > 0 and statearg in states:
                    #print(f"Repeat {states[statearg]} -> {i} offset {offset}")
                    interval = states[statearg] - i
                    break
                states[statearg] = i
                i += 1
            
            if offset != None:
                # This is not really correct, but works for my input.
                # Find the output node for the broadcast module, since it's only
                # one. It could in theory be multiple
                broadcast = [mod for mod_name, mod in upstream.modules.items() if type(mod)==Broadcast][0]
                if len(broadcast.outputs) == 1:
                    input_node = broadcast.outputs[0]
                    outputs = [outp for outp in self.outputs if outp != input_node]
                    new_node = Periodic(outputs, interval, offset)
                    return None, new_node, [input_node]
            
        return self.copy(), None, []

class Periodic(Module):
    DOT_STYLE = {
        'shape': 'cylinder',
        'style': 'filled',
        'color': 'gold3',
        'fillcolor': 'gold1'
    }

    def __init__(self, outputs, interval, offset):
        super().__init__(outputs)
        self.interval = interval
        self.offset = offset
        self.cur_t = 0

    def copy(self):
        return Periodic(self.outputs, self.interval, self.offset)
    
    def signal(self, source, value):
        if value == 'low':
            if self.cur_t == 0:
                for output in self.outputs:
                    yield (output, 'high')
                    
            
            if self.cur_t % self.interval == self.offset:
                for output in self.outputs:
                    yield (output, 'low')
                for output in self.outputs:
                    yield (output, 'high')
            
            self.cur_t += 1

            return
            yield
        else:
            return self._nop()

class Broadcast(Module):
    DOT_STYLE = {
        'style': 'filled',
        'color': 'blue3',
        'fillcolor': 'deepskyblue2'
    }
    
    def copy(self):
        return Broadcast(self.outputs)

    def signal(self, source, value):
        return self._send(value)
    
class OutputTrigger:
    """
    Trigger flag for output node
    
    It is kept in its own class to be able to have the same instance through
    the optimization process
    """
    def __init__(self):
        self.triggered = False
    
    def trigger(self):
        self.triggered = True
    
    def reset(self):
        self.triggered = False
    
    def has_triggered(self):
        return self.triggered

class Output(Module):
    """
    The output triggers when a low signal is recieved

    It has no outputs itself
    """
    DOT_STYLE = {
        'style': 'filled',
        'color': 'red',
        'fillcolor': 'indianred1'
    }

    def __init__(self):
        super().__init__([])
        self.trigger = OutputTrigger()
    
    def copy(self):
        new_out = Output()
        # Important that the same trigger instance remains through optimization
        new_out.trigger = self.trigger
        return new_out

    def signal(self, source, value):
        if value == 'low':
            self.trigger.trigger()
        return self._nop()

    def reset(self):
        return self.trigger.reset()

    def has_triggered(self):
        return self.trigger.has_triggered()

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
    
    def _update_name(self, old_name):
        delim = old_name.find('.')
        if delim < 0:
            id = 0
        else:
            id = int(old_name[delim+1:])
            old_name = old_name[:delim]
        
        while f"{old_name}.{id}" in self.modules:
            id += 1
        return f"{old_name}.{id}"

    def isolate(self, out_node):
        # Only save referenced node, so do simple garbage collection
        new_network = Network()
        queue = deque()
        queue.append(out_node)
        while len(queue) > 0:
            to_add = queue.popleft()
            if to_add not in new_network.modules:
                new_network.add_module(to_add, self.modules[to_add].copy())
                queue.extend(self.modules[to_add].inputs.keys())
        
        # Filter outputs to only available nodes
        available = new_network.modules.keys()
        for name, module in new_network.modules.items():
            module.filter_outputs(available)
        new_network.connect()
        return new_network

    def downstream(self, in_node):
        # This is not to isolate a running network, but just list nodes that
        # are downstream, for optimization purposes
        outp = {}
        queue = deque()
        queue.extend(self.modules[in_node].outputs)
        while len(queue) > 0:
            to_add = queue.popleft()
            if to_add not in outp:
                outp[to_add] = self.modules[to_add]
                queue.extend(self.modules[to_add].outputs)
        return outp

    def optimize(self, out_node='rx'):
        new_network = Network()
        reconnects = []
        for name, module in self.modules.items():
            old_module, new_module, new_reconnects = module.optimize(name, self)
            if old_module is not None:
                new_network.add_module(name, old_module)
            if new_module is not None:
                new_name = self._update_name(name)
                reconnects += [(orig, new_name) for orig in new_reconnects]
                new_network.add_module(new_name, new_module)

        for orig, new in reconnects:
            for name, module in new_network.modules.items():
                module.apply_reconnect(orig, new)

        new_network.connect()

        return new_network.isolate(out_node), reconnects != []

    
    def todot(self, file=sys.stdout):
        print("digraph {", file=file)
        print("  rankdir=LR;", file=file)
        for name, module in self.modules.items():
            output_str = "{" + " ".join(f"\"{outp}\"" for outp in module.outputs if outp in self.modules) + "}"
            styletag = " ".join(f'{k}="{v}"' for k,v in module.DOT_STYLE.items())
            print(f"  \"{name}\" -> {output_str};", file=file)
            print(f"  \"{name}\" [{styletag}]", file=file)
        print("}", file=file)


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

class Part2:
    def __init__(self, input):
        self.network = copy.deepcopy(input.network)
        self.output = Output()
        self.network.add_module('rx', self.output)
        self.network.connect()

    def run(self):
        network = self.network
        need_optimize = True
        while need_optimize:
            network, need_optimize = network.optimize()
        
        #network.todot(file=open('input1.dot','w'))

        # We have succeeded if only broadcaster -> periodic -> rx is left
        mod_names = [name for name in network.modules.keys() if name not in ['broadcaster', 'rx']]
        if len(mod_names) == 1:
            per_name = mod_names[0]
            if type(network.modules[per_name] == Periodic):
                return network.modules[per_name].interval
        return None
        

if __name__ == "__main__":
    import doctest
    doctest.testmod()

    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <input file>")
        sys.exit(1)

    input = Input(sys.argv[1])
    
    part2 = Part2(input)
    print(f"Part2: {part2.run()}")
