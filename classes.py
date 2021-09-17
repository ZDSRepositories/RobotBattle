class Computer():
    def __init__(self, code, memory_size, pc):
        self.code = code
        self.memory_size = memory_size
        self.data = [float(0) for i in range(memory_size)]
        self.log = []

        self.pc = 0 #program counter: current line number
        self.accumulator = 0.0
        self.stack = []
        self.running = True
        self.flags = {"zero": False, "negative":False}

    def restart(self):
        self.accumulator = 0
        self.pc = 0
        self.data = [0 for i in range(self.memory_size)]

    def parse_arg(self, arg):
        value = arg
        if arg[0] == "@":
            if arg[1] == "a":
                value = self.accumulator
            else:
                value = self.data[int(value[1:])]
        elif arg[0] == ":":
            value = self.code.index(arg)
        else:
            value = float(value)

        return value


    def execute_assembly(self, command):
        binary_opcodes = ["write", "add", "sub", "subtract", "mul", "multiply",
                      "div", "divide", "cmp", "compare"]
        noarg_opcodes = ["halt", "return"]
        if command[0] == ":":
            self.pc += 1
            return
        elif not self.running:
            return

        math_operation = False
        parsed = command.split(" ")
        opcode = parsed[0]
        args = [float(self.parse_arg(arg)) for arg in parsed[1:]]
        """
        arg1 = float(self.parse_arg(parsed[1]))
        arg2 = None
        if opcode in binary_opcodes:
            arg2 = float(self.parse_arg(parsed[2]))"""

        # starting the refactoring
        handlers = {
            "halt": self.handle_halt,
            "load": self.handle_load,
            "write": self.handle_write,
            "jump": self.handle_jump,
            "jumpz": self.handle_jumpz,
            "jumpnz": self.handle_jumpnz,
            "jumpn": self.handle_jumpn,
            "jumpnn": self.handle_jumpnn,
            "add": self.handle_add,
            "sub": self.handle_subtract,
            "subtract": self.handle_subtract,
            "mul": self.handle_multiply,
            "multiply": self.handle_multiply,
            "div": self.handle_divide,
            "divide": self.handle_divide,
            "push": self.handle_push,
            "pop": self.handle_pop,
            "call": self.handle_call,
            "return": self.handle_return,
            "cmp": self.handle_compare,
            "compare": self.handle_compare,
            "log": self.handle_log
        }

        #print(binary_opcodes)
        #print(opcode)
        if opcode in binary_opcodes:
            #print(handlers[opcode])
            handlers[opcode](args[0], args[1])
        elif opcode in noarg_opcodes:
            handlers[opcode]()
        else:
            handlers[opcode](args[0])
        self.pc += 1

        return


    def update_flags(self):
        if self.accumulator == 0:
            self.flags["zero"] = True
        else:
            self.flags["zero"] = False

        if self.accumulator < 0:
            self.flags["negative"] = True
        else:
            self.flags["negative"] = False


    def handle_halt(self):
        self.running = False
        return

    def handle_load(self, value):
        self.accumulator = value

    def handle_write(self, value, dest):
        # store value at location
        self.data[int(dest)] = value

    def handle_jump(self, dest):
        self.pc = int(dest - 1)

    def handle_jumpz(self, dest):
        if self.flags["zero"]:
            self.pc = int(dest - 1)

    def handle_jumpnz(self, dest):
        if not self.flags["zero"]:
            self.pc = int(dest - 1)

    def handle_jumpn(self, dest):
        print("JUMP IF NEGATIVE")
        if self.flags["negative"]:
            self.pc = int(dest - 1)

    def handle_jumpnn(self, dest):
        if not self.flags["negative"]:
            self.pc = int(dest - 1)

    def handle_add(self, term1, term2):
        math_operation = True
        self.accumulator = term1 + term2
        self.update_flags()

    def handle_subtract(self, minuend, subtrahend):
        math_operation = True
        self.accumulator = minuend - subtrahend
        self.update_flags()

    def handle_multiply(self, term1, term2):
        math_operation = True
        self.accumulator = term1 * term2
        self.update_flags()

    def handle_divide(self, dividend, divisor):
        math_operation = True
        self.accumulator = dividend / divisor
        self.update_flags()

    def handle_push(self, value):
        self.stack.append(value)

    def handle_pop(self, dest):
        if dest == "a":
            self.accumulator = self.stack.pop()
        else:
            self.data[int(self.parse_arg(dest))] = self.stack.pop()

    def handle_call(self, addr):
        self.stack.append(self.pc)
        self.pc = addr - 1

    def handle_return(self):
        try:
            self.pc = self.stack.pop()
        except IndexError:
            pass

    def handle_compare(self, minuend, subtrahend):
        difference = minuend - subtrahend
        if difference == 0:
            self.flags["zero"] = True
        else:
            self.flags["zero"] = False
        if difference < 0:
            self.flags["negative"] = True
        else:
            self.flags["negative"] = False

    def handle_log(self, char):
        #print(type(char))
        char = chr(int(char))
        print("LOGGING CHR", ord(char), ":", char)
        if char == "\n":
            self.log.append("")
        else:
            if len(self.log) > 0:
                self.log[-1] += char
            else:
                self.log.append(char)


    def execute_next(self):
        if self.pc  >= len(self.code):
            self.running = False
            return
        if self.running:
            self.execute_assembly(self.code[self.pc])
