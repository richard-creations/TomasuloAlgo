# scoreboard.py - runs the scoreboard based on instructions
from fu import FunctionalUnit, FORMAT_HEADER
from decode import instructions as inst_funcs

ASM_FILE = 'q2.asm'
out_file = ASM_FILE[:-4]+".out"
debug = False
errors = False
""" The ScoreboardParser class is responsible for taking in an
assembly file as input and creating its respective Scoreboard object
which can then be used to simulate the scoreboarding algorithm. The
parser has one function in its API: scoreboard_for_asm()"""
class ScoreboardParser:

  def __init__(self, asm_file):
    self.sb = Scoreboard()
    self.asm = asm_file


  """ Parses a functional unit in the assembly file"""
  def __parse_fu(self, asm_tokens):
    f_unit = asm_tokens[0][1:]
    num_units = int(asm_tokens[1])
    clocks = int(asm_tokens[2])
    for unit in range(0, num_units):
      self.sb.units.append(FunctionalUnit(f_unit, clocks,unit))


  """ Parses an instruction in the assembly file"""
  def __parse_inst(self, inst_tokens):
    key = inst_tokens[0]
    inst_func = inst_funcs[key]
    instruction = inst_func(' '.join(inst_tokens))
    self.sb.instructions.append(instruction)


  """ Parses a line of the assembly file"""
  def __parse_asm_line(self, line):
    tokens = line.split()
    if debug:
      print(tokens)

    # if the line starts with '.' it is a functional unit
    # instead of an instruction
    if tokens[0][0] == '.':
      f_units = self.__parse_fu(tokens)
    else:
      inst = self.__parse_inst(tokens)


  """ Creates a Scoreboard object based on a given asm file"""
  def scoreboard_for_asm(asm_file):
    parser = ScoreboardParser(asm_file)
    with open(parser.asm, 'r') as f:
      assembly = [line.strip() for line in f]
    for instruction in assembly:
      parser.__parse_asm_line(instruction)
    return parser.sb


""" The Scoreboard class is used to simulate the scoreboarding algorithm.
"""
class Scoreboard:

  def __init__(self):
    self.units = []           # array of FunctionalUnit
    self.instructions = []    # array of Instruction
    self.reg_status = {}      # register status table
    self.pc = 0               # program counter
    self.clock = 1            # processor clock


  def __str__(self):
    result = 'CLOCK: %d\n' % (self.clock)
    result += FORMAT_HEADER + '\n'
    for unit in self.units:
      result += str(unit) + '\n'
    return result


  """ Checks to see if the scoreboard is done executing. Returns True if so"""
  def done(self):
    done_executing = True
    out_of_insts = not self.has_remaining_insts()
    if out_of_insts:
      for fu in self.units:
        if fu.busy:
          done_executing = False
          break
    return out_of_insts and done_executing


  """ Checks to see if there are instructions left to issue to the
  scoreboard and returns True if so"""
  def has_remaining_insts(self):
    return self.pc < len(self.instructions)


  """ Determines if an instruction is able to be issued"""
  def can_issue(self, inst, fu):
    if inst is None or inst.issue>0:
      return False
    else:
      return inst.op == fu.type and not fu.busy  #(inst.dest in self.reg_status)#and not (inst.dest in self.reg_status)


  """ Determines if an instruction is able to enter the read operands phase"""
  def can_read_operands(self, fu):
    return fu.busy and fu.r1 and fu.r2


  """ Determines if an instruction is able to enter the execute phase"""
  def can_execute(self, fu):
    # check to make sure we've issued operands, the functional unit
    # is actually in use, and has clocks remaining
    #print(self.reg_status)
    #print(self.instructions[fu.inst_pc].src1, self.reg_status)
    return not fu.executed and fu.busy and fu.r1 and fu.r2 #and not (fu.dest in self.reg_status)#and fu.issued()#self.instructions[fu.inst_pc].src1 and self.reg_status[self.instructions[fu.inst_pc].src2]) #self.can_read_operands(fu)# and (not fu.r1 and not fu.r2) and fu.issued()


  """ Determines if an instruction is able to enter the writeback phase"""
  def can_write_back(self, fu):
    can_write_back = False
    return fu.executed




    '''
    for f in self.units:
      can_write_back = (f.src1 != fu.dest or not f.r1) and (f.src2 != fu.dest or not f.r2)
      if not can_write_back:
        break

    
        for f in self.units:
        if f.src1_rs == fu:
            r1 = True
        if f.src2_rs == fu:
            r2 = True



    for f in self.units:
      can_write_back = (f.src1 != fu.dest or not f.r1) and (f.src2 != fu.dest or not f.r2)
      if not can_write_back:
        break
    '''
    return can_write_back


  """ Issues an instruction to the scoreboard"""
  def issue(self, inst, fu):
    fu.issue(inst, self.reg_status)
    self.reg_status[inst.dest] = fu
    self.instructions[self.pc].issue = self.clock
    fu.inst_pc = self.pc


  """ Read operands stage of the scoreboard"""
  def read_operands(self, fu):
    fu.read_operands()
    self.instructions[fu.inst_pc].read_ops = self.clock


  """ Execute stage of the scoreboard"""
  def execute(self, fu):
    fu.execute()
    if self.instructions[fu.inst_pc].start == -1:
        self.instructions[fu.inst_pc].read_ops = self.clock
        self.instructions[fu.inst_pc].start  = self.clock
        if debug:
          print("Clock: ",self.clock,"\t")
          print("executed\t", self.instructions[fu.inst_pc])
        
    if fu.time == 0:
        self.instructions[fu.inst_pc].ex_cmplt = self.clock
        fu.executed = True
        if debug:
          print("Clock: ",self.clock,"\t")
          print("finished exe\t", self.instructions[fu.inst_pc])


  """ Writeback stage of the scoreboard"""
  def write_back(self, fu):
    fu.write_back(self.units)
    self.instructions[fu.inst_pc].write_res = self.clock
    if debug:
      print("Clock: ",self.clock,"\t")
      print("writing\t\t", self.instructions[fu.inst_pc])
    # clear out the result register status
    try:
      del self.reg_status[fu.dest]

    except:
      if errors:
        print("Error during writeback: ", self.instructions[fu.inst_pc])
        print("->",fu.dest, "not in reg_status")
        print(self.reg_status)
    fu.clear()
    



  """ Tick: simulates a clock cycle in the scoreboard"""
  def tick(self):
    # unlock all functional units
    #print("Clock: ",self.clock)
    if debug:
        print(str(self))
        print(self.reg_status.keys())
    for fu in self.units:
      fu.lock = False

    # Get the next instruction based on the PC
    next_instruction = self.instructions[self.pc] if self.has_remaining_insts() else None

    for fu in self.units:
      if self.can_issue(next_instruction, fu):
        self.issue(next_instruction, fu)
        self.pc += 1
        if debug:
          print("Clock: ",self.clock,"\t")
          print("issued\t\t", next_instruction)
        fu.lock = True
      elif self.can_execute(fu):
        #print("exe ", next_instruction)
        #print("Clock: ",self.clock, fu)
        self.execute(fu)
        fu.lock = True
      elif fu.issued():
        # the functional unit is in use but can't do anything
        fu.lock = True

    for fu in self.units:
      if not fu.lock and self.can_write_back(fu):
        self.write_back(fu)

    self.clock += 1


if __name__ == '__main__':
  sb = ScoreboardParser.scoreboard_for_asm(ASM_FILE)

  while not sb.done():
    sb.tick()

  # display the final results
  print('                                          Write    ')
  print('                        Issue   Execute   Result   ')
  print('                    -------------------------------')
  for instruction in sb.instructions:
    print(str(instruction))



  # save the final results
  outstring = ''
  outstring+='                                          Write    \n'
  outstring+='                        Issue   Execute   Result   \n'
  outstring+='                    -------------------------------\n'
  for instruction in sb.instructions:
    outstring+=str(instruction)
    outstring+='\n'

  outstring+='\n'
  outstring+=str(sb)

  file = open(out_file, 'w')
  file.write(outstring)
  file.close()

