from data import Integer, Array, Function


class ProgramBlock:
    def __init__(self):
        self.instructions = [None]
    
    def add_instruction(self, inst):
        self.instructions.append(inst)
    
    def insert_instruction(self, inst, index):
        print(inst)
        print(index)

        if self.instructions[index]:
            print("BUG!")
        self.instructions[index] = inst
    
    def get_i(self):
        return len(self.instructions)
    
    def skip_instruction(self):
        self.instructions.append(None)
    def get_block(self):
        return '\n'.join([f'{i}\t{self.instructions[i]}' for i in range(len(self.instructions))])

class DataBlock:
    def __init__(self):
        self.datas = []
    
    def add_int(self, lexeme):
        integer = Integer(lexeme, self.get_address())
        self.datas.append(integer)
        return integer
    
    def add_arr(self, lexeme, length):
        array = Array(lexeme, self.get_address(), length)
        
        for i in range(length):
            self.add_int(lexeme)
        return array
    
    def add_func(self, lexeme, typ):

        function = Function(lexeme, self.get_address(), typ)
        
        if typ == 'int':
            self.add_int(lexeme)
        else:
            self.add_int(lexeme)
        
        return function
    def get_address(self):
        return 4 * len(self.datas) + 100


class MemoryBlock:
    def __init__(self):
        self.PB = ProgramBlock()
        self.DB = DataBlock()
        self.current_temp = 500
    
    def get_temp(self):
        self.current_temp += 4
        return self.current_temp - 4