FORMAT_HEADER = \
    "UNIT     Clocks  Busy    Fi   Fj    Fk   Qj         Qk         Rj    Rk\
\n-------------------------------------------------------------------------------"


add = 0
mul = 1
ld = 2

class FunctionalUnit:

    def __init__(self, type, clocks, num=0):
        self.time = clocks
        self.default_clocks = clocks
        self.type = type                      # type of functional unit
        self.busy = False                     # busy status
        self.dest = self.src1 = self.src2 = None    # instruction registers
        self.src1_rs = self.src2_rs = None              # FUs producing source registers Fj, Fk
        self.r1 = self.r2 = True              # Flags for Fj, Fk ready status
        self.lock = False                     # mutex
        self.inst_pc = -1                     # pc for the instruction using the FU
        self.start = -1
        self.executed = False
        self.id = type+str(num)

    '''
    def __str__(self) -> str:
        return "%-10s%-10d%-10s%-10s%-10s%-10s%-10s%-10s" % \
            (self.id, self.time, str(self.busy), str(self.type), str(self.src1), str(self.src2), str(self.src1_rs), self.src2_rs)
    '''
    def __str__(self):
        qj_type = self.src1_rs.type if self.src1_rs is not None else None
        qk_type = self.src2_rs.type if self.src2_rs is not None else None
        rs_name1 = self.src1_rs.id if self.src1_rs is not None else None
        rs_name2 = self.src2_rs.id if self.src2_rs is not None else None

        return "%-7s%8d%6s%6s%6s%6s  %-9s  %-9s%6s%6s" % \
            (self.type, self.time, self.busy,
                self.dest, self.src1, self.src2,
                rs_name1, rs_name2, self.r1, self.r2)

    """Resets the functional unit so it can be used by another instruction"""
    def clear(self):
        self.time = self.default_clocks
        self.busy = False
        self.dest = self.src1 = self.scr2 = None    # instruction registers
        self.src1_rs = self.src2_rs = None              # FUs producing source registers Fj, Fk
        self.r1 = self.r2 = True # Flags for Fj, Fk ready status
        self.inst_pc = -1
        self.start = -1
        self.executed = False

        """Encapsulates the functionality of issuing an instruction"""
    def issue(self, inst, reg_status):
        self.busy = True
        self.dest = inst.dest
        self.src1 = inst.src1
        self.src2 = inst.src2

        if inst.src1 in reg_status:
            self.src1_rs = reg_status[inst.src1] #set to fu producing register val
        if inst.src2 in reg_status:
            self.src2_rs = reg_status[inst.src2]

        self.r1 = not self.src1_rs
        self.r2 = not self.src2_rs


    def read_operands(self):
        self.r1 = False
        self.r2 = False
    """Update function encapsulates the clock on a functional unit"""

    def execute(self):
        if self.start == -1:
            self.start = self.time
        self.time -= 1
     


    """Encapsulates the functionality of writing back an instruction
    Requires as input all of the functional units on the scoreboard"""
    def write_back(self, f_units):
        for f in f_units:
            if f.src1_rs == self:
                f.r1 = True
                f.src1_rs = None
            if f.src2_rs == self:
                f.r2 = True
                f.src_rs = None

    """Determines if a functional unit has been issued"""
    def issued(self):
        return self.busy and self.time > 0

