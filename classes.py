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

    def execute(self, command):
        if command[0] == ":":
            self.pc += 1
            return
        elif not self.running:
            return

        math_operation = False
        parsed = command.split(" ")
        opcode = parsed[0]

        # starting the refactoring
        """handlers = {
            "halt": self.halt,
            "load": self.load,
            "write": self.write,
            "jump": self.jump,
            "jumpz": self.jumpz
                    }"""

        if opcode == "halt":
            self.running = False
            return

        elif opcode == "load":
            value = self.parse_arg(parsed[1])
            self.accumulator = value

        elif opcode == "write":
            #store value in location
            value = self.parse_arg(parsed[1])
            dest = int(self.parse_arg(parsed[2]))
            self.data[int(dest)] = value

        elif opcode == "jump":
            dest = int(self.parse_arg(parsed[1]))
            self.pc = dest - 1

        elif opcode == "jumpz":
            dest = int(self.parse_arg(parsed[1]))
            if self.flags["zero"]:
                self.pc = dest - 1

        elif opcode == "jumpnz":
            dest = int(self.parse_arg(parsed[1]))
            if not self.flags["zero"]:
                self.pc = dest - 1

        elif opcode == "jumpn":
            print("JUMP IF NEGATIVE")
            dest = int(self.parse_arg(parsed[1]))
            if self.flags["negative"]:
                self.pc = dest - 1

        elif opcode == "jumpnn":
            dest = int(self.parse_arg(parsed[1]))
            if not self.flags["negative"]:
                self.pc = dest - 1

        elif opcode == "add":
            math_operation = True
            term1 = self.parse_arg(parsed[1])
            term2 = self.parse_arg(parsed[2])
            self.accumulator = term1 + term2

        elif opcode in ["sub", "subtract"]:
            math_operation = True
            minuend = self.parse_arg(parsed[1])
            subtrahend = self.parse_arg(parsed[2])
            self.accumulator = minuend - subtrahend

        elif opcode in ["mul", "multiply"]:
            math_operation = True
            term1 = self.parse_arg(parsed[1])
            term2 = self.parse_arg(parsed[2])
            self.accumulator = term1 * term2

        elif opcode in ["div", "divide"]:
            math_operation = True
            dividend = self.parse_arg(parsed[1])
            divisor = self.parse_arg(parsed[2])
            self.accumulator = dividend / divisor

        elif opcode == "push":
            value = self.parse_arg(parsed[1])
            self.stack.append(value)

        elif opcode == "pop":
            #value = self.parse_arg(parsed[1])
            dest = parsed[1]
            #print(dest)
            #input()
            if dest == "a":
                self.accumulator = self.stack.pop()
            else:
                self.data[int(self.parse_arg(dest))] = self.stack.pop()

        elif opcode == "call":
            addr = self.parse_arg(parsed[1])
            self.stack.append(self.pc)
            self.pc = addr

        elif opcode == "return":
            try:
                self.pc = self.stack.pop()
            except IndexError:
                pass

        elif opcode in ["cmp", "compare"]:
            minuend = self.parse_arg(parsed[1])
            subtrahend = self.parse_arg(parsed[2])
            difference = minuend - subtrahend
            if difference == 0:
                self.flags["zero"] = True
            else:
                self.flags["zero"] = False
            if difference < 0:
                self.flags["negative"] = True
            else:
                self.flags["negative"] = False

        elif opcode == "logchar":
            char = int(self.parse_arg(parsed[1]))
            print("LOGGING:", chr(char))
            if chr(char) == "\n":
                self.log.append("")
            else:
                if len(self.log) > 0:
                    self.log[-1] += (chr(char))
                else:
                    self.log.append(chr(char))



        if math_operation:
            if self.accumulator == 0:
                self.flags["zero"] = True
            else:
                self.flags["zero"] = False

            if self.accumulator < 0:
                self.flags["negative"] = True
            else:
                self.flags["negative"] = False

        self.pc += 1

    def execute_next(self):
        if self.pc  >= len(self.code):
            self.running = False
            return
        self.execute(self.code[self.pc])