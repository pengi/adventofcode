import sys

#
# Advent of code - day16 part2 by Max "pengi" Sikström, u/pngipngi
#
# Solution done in O(log(N)) time, given offset from input buffer end
#

class PhasesState:
    """
    Contains one digit from the end for all phases in the process, including
    which offset from end, and the (reversed) input buffer.

    Can be incremented (from the end... Everything is in reverse...) one
    digit at a time.
    """
    def __init__(self, inp, offset, phases):
        self.inp = inp
        self.offset = offset
        self.phases = phases
    
    def stepone(self):
        val = self.inp[self.offset % len(self.inp)]
        self.offset+=1
        for i in range(len(self.phases)):
            self.phases[i] = (self.phases[i] + val)%10
            val = self.phases[i]
        return self.phases[-1]

    def get_result(self, count):
        result = []
        for i in range(count):
            result.append(self.stepone())
        result.reverse()
        return result
    
    def get_phases(self):
        return self.phases

class PhasesTransition:
    """
    Models the the influence of an interval of the input buffer to the output
    state of PhasesState, and the input state to the output state.

    The interval must be a even factor of the input buffer size.

    The transistion exploits the linear behaviour of the process by using
    superposition.

    According to superposition, two different parts can be calculated
    independently, and therfore update independently too:

    1. The input buffer affecting the output state, given 0 input state
    2. The input state affecting the output state, given 0 input buffer

    Also, since input state contains 100 bits, they should be calculated
    indepdendently. But since the input state is 0 when calculating 2., the
    result can simply be shifted.

    It is therefore also possible to "duplicate" the transition interval by
    transitioning a "null" input state twice.
    """
    def __init__(self, n_phases):
        self.increment = 0
        self.n_phases = n_phases
        self.phase_affect = []
        self.base_affect = []

    def apply_input(self, inp):
        if self.increment != 0:
            raise Exception("Can't apply input on non-empty object")

        self.increment = len(inp)
        self.inp = inp

        state = PhasesState(inp, 0, [0]*self.n_phases)
        for j in range(len(inp)):
            state.stepone()
        self.base_affect = state.phases

        first_phase_digit = [0]*self.n_phases
        first_phase_digit[0] = 1
        plain_input = [0] * len(inp)

        state = PhasesState(plain_input, 0, first_phase_digit)
        for j in range(len(plain_input)):
            state.stepone()
        self.phase_affect = state.get_phases()
    
    def duplicate_length(self):
        if self.increment == 0:
            raise Exception("Can't duplicate length on empty object")

        # Base affect - self.apply doesn't depend on state.inp
        state = PhasesState([], 0, [0]*self.n_phases)
        self.apply(state)
        self.apply(state)
        base_affect = state.phases

        first_phase_digit = [0]*self.n_phases
        first_phase_digit[0] = 1

        state = PhasesState([], 0, first_phase_digit)
        self.apply(state, True)
        self.apply(state, True)
        phase_affect = state.get_phases()

        new_transition = PhasesTransition(self.n_phases)
        new_transition.base_affect = base_affect
        new_transition.phase_affect = phase_affect
        new_transition.increment = self.increment*2
        new_transition.inp = self.inp
        return new_transition

    
    def apply(self, state, zero_input=False):
        # If zero inp buffer is expected, zero out base affect. Used for duplication of input length, to calculate phase affect
        if zero_input:
            new_phases = [0] * self.n_phases
        else:
            new_phases = self.base_affect[:]

        for i in range(self.n_phases):
            for j, val in enumerate([0]*i + self.phase_affect[:self.n_phases-i]):
                new_phases[j] = (new_phases[j] + state.phases[i]*val) % 10
        state.phases = new_phases
        state.offset += self.increment
        


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: "+sys.argv[0]+"<use optimization yes/no> <input file>")
        sys.exit(1)

    inp = [int(c, 10) for c in open(sys.argv[2], "r").readline(1024).strip()]

    offset = sum(10**(6-i) * v for i,v in enumerate(inp[:7]))
    count = 10000*len(inp) - offset

    inp.reverse()

    state = PhasesState(inp, 0, [0]*100)

    # Enable/Disable optimization
    if sys.argv[1] == "yes":
        transition = PhasesTransition(100)
        transition.apply_input(inp)


        # Using the Phase Transition, it is possible to duplicate/apply one
        # bit at a time from the offset, in blocks of input length to get up to
        # the start of the input buffer, as a shortcut
        left = (count-8)//len(inp)
        bit = 1
        while left > 0:
            if (left & bit) != 0:
                transition.apply(state)
                left -= bit
            bit*=2
            transition = transition.duplicate_length()
        print(state.phases)

    while state.offset < count - 8:
        state.stepone()
    print("".join(str(v) for v in state.get_result(8)))
