from typing import Any
from memory_block import MemoryBlock
from data import Integer
import scanner


class CodeGenerator:
    def __init__(self):
        self.memory = MemoryBlock()
        self.PB = self.memory.PB
        self.DB = self.memory.DB
        self.SS = []
        self.variables = {}
        self.symbol_table = []
        self.scope_stack = []
        self.errors = []
        self.actions = {
            'assign': self.assign,
            'assign_chain': self.assign_chain,
            'begin_func': self.begin_func,
            'begin_repeat': self.begin_repeat,
            'break_loop': self.break_loop,
            'declare_arr': self.declare_arr,
            'declare_int': self.declare_int,
            'do_op': self.do_op,
            'end_args': self.end_args,
            'end_repeat': self.end_repeat,
            'get_func': self.get_func,
            'invoke_func': self.invoke_func,
            'jp': self.jp,
            'jpfsave': self.jpfsave,
            'parray': self.parray,
            'push': self.push,
            'push_num': self.push_num,
            'save_addop': self.save_addop,
            'save_multop': self.save_multop,
            'save_relop': self.save_relop,
            'save_skip': self.save_skip,
            'set_return_addr': self.set_return_addr,
            'end_func': self.end_func,
            'pid': self.pid,
            'end_expression': self.end_expression,
            'arr_arg': self.arr_arg,
            'narr_arg': self.narr_arg
        }

    def pid(self):
        if self.token == 'output':
            self.SS.append('out')
            return
        if self.token not in self.symbol_table:
            self.errors.append(self.error_pref() + f'\'{self.token}\' is not defined.')
            self.SS.append('1000')
            return
        data = self.variables[self.token]

        self.SS.append(data.address if data.__class__.__name__ != 'Array' else str(data.address))
        return

    def save_skip(self):
        print(self.SS)
        self.SS.append(self.PB.get_i())
        print(self.SS)
        self.PB.skip_instruction()
        return

    def jpfsave(self):
        address = self.SS.pop()
        bool = self.SS.pop()
        i = self.PB.get_i()
        self.PB.skip_instruction()
        self.PB.insert_instruction(f'(JPF, {bool}, {self.PB.get_i()},  )', address)
        self.SS.append(bool)
        self.SS.append(i)
        return

    def jp(self):
        address = self.SS.pop()
        bool = self.SS.pop()
        self.PB.insert_instruction(f'(JP, {self.PB.get_i()},  ,  )', address)
        return

    def push(self):
        self.SS.append(self.token)
        return

    def push_num(self):
        self.SS.append(f'#{self.token}')
        return

    def save_addop(self):
        self.SS.append('ADD' if self.token == '+' else 'SUB')
        return

    def save_multop(self):
        self.SS.append('MULT')
        return

    def save_relop(self):
        self.SS.append('LT' if self.token[0] == '<' else 'EQ')
        return

    def do_op(self):
        operand1, op, operand2 = self.SS[-3:]
        print(self.SS)

        self.SS = self.SS[:-3]
        type1 = 'int' if (type(operand1) == int or operand1[0] in ['#', '@']) else 'array'
        type2 = 'int' if (type(operand2) == int or operand2[0] in ['#', '@']) else 'array'
        if type1 != type2 and operand1 != '1000' and operand2 != '1000':
            self.errors.append(self.error_pref() + f'Type mismatch in operands, Got array instead of int.')

        temp_addr = self.memory.get_temp()
        self.PB.add_instruction(f'({op}, {operand1}, {operand2}, {temp_addr} )')
        self.SS.append(temp_addr)
        return

    def declare_int(self):
        t, lexeme = self.SS[-2:]
        self.SS = self.SS[:-2]
        if t == 'void':
            self.errors.append(self.error_pref() + f'Illegal type of void for \'{lexeme}\'.')
            return  # TODO doublecheck

        integer = self.DB.add_int(lexeme)
        self.variables[lexeme] = integer
        self.symbol_table.append(lexeme)
        return

    def declare_arr(self):
        t, lexeme, s = self.SS[-3:]
        self.SS = self.SS[:-3]
        if t == 'void':
            self.errors.append(self.error_pref() + f'Illegal type of void for {lexeme}.')
            return

        s = int(s[1:])
        arr = self.DB.add_arr(lexeme, s)
        self.variables[lexeme] = arr
        self.symbol_table.append(lexeme)
        return

    def begin_func(self):
        typ, lexeme = self.SS[-2:]
        self.SS = self.SS[:-2]
        func = self.DB.add_func(lexeme, typ)
        self.symbol_table.append(lexeme)
        self.variables[lexeme] = func
        self.scope_stack.append(len(self.symbol_table))
        self.SS.append(lexeme)
        return

    def narr_arg(self):
        func_name, typ, lexeme = self.SS[-3:]
        self.SS = self.SS[:-2]
        integer = self.DB.add_int(lexeme)
        self.symbol_table.append(lexeme)
        self.variables[lexeme] = integer
        self.variables[func_name].add_arg('int')
        return

    def arr_arg(self):
        func_name, typ, lexeme = self.SS[-3:]
        self.SS = self.SS[:-2]
        arr = self.DB.add_arr(lexeme, 10)
        self.symbol_table.append(lexeme)
        self.variables[lexeme] = arr
        self.variables[func_name].add_arg('array')

    def end_args(self):
        print(self.SS)
        if self.SS[-1] == 'void':
            self.SS.pop()
        lexeme = self.SS[-1]
        self.SS = self.SS[:-1]
        if lexeme == 'main':
            print(self.PB.get_block())
            self.PB.insert_instruction(f'(JP, {self.PB.get_i()},  ,   )', 0)
        return

    def assign_chain(self):
        self.SS.append('chained')
        return

    def begin_repeat(self):
        self.SS.append('repeat')
        self.PB.add_instruction(f'(JP, {self.PB.get_i() + 2},  ,   )')
        self.PB.skip_instruction()
        self.SS.append(self.PB.get_i())
        return

    def assign(self):
        addr, chain, value = self.SS[-3:]
        self.SS = self.SS[:-3]
        self.PB.add_instruction(f'(ASSIGN, {value}, {addr},  )')
        if self.SS and self.SS[-1] == chain:
            self.SS.append(value)
        return

    def end_repeat(self):
        name, address, bool = self.SS[-3:]
        self.SS = self.SS[:-3]

        self.PB.add_instruction(f'(JPF, {bool}, {address},   )')
        self.PB.insert_instruction(f'(JP, {self.PB.get_i()},  ,   )', address - 1)
        return

    def parray(self):
        address, offset = self.SS[-2:]
        address = int(address)
        self.SS = self.SS[:-2]
        if type(offset) == str:
            self.SS.append(address + int(offset[1:]) * 4)
            return
        temp1 = self.memory.get_temp()
        temp2 = self.memory.get_temp()
        self.PB.add_instruction(f'(MULT, {offset}, #4, {temp1})')
        self.PB.add_instruction(f'(ADD #{address}, {temp1}, {temp2})')
        self.SS.append(f'@{temp2}')
        return

    def break_loop(self):
        if 'repeat' not in self.SS:
            self.errors.append(self.error_pref() + f'No \'repeat ... until\' found for \'break\'.')
            return
        repeat_index = self.SS.index('repeat')
        jump_address = self.SS[repeat_index + 1]
        self.PB.add_instruction(f'(JP, {jump_address - 1},  ,   )')
        return

    def set_return_addr(self):
        self.SS.pop()
        pass

    def invoke_func(self):
        args = []
        index = None
        for i in range(len(self.SS)):
            if self.SS[i] == 'args':
                index = i
        args = self.SS[index + 1:]
        func_addr = self.SS[index - 1]
        self.SS = self.SS[:index - 1]
        if type(func_addr) == str and func_addr == 'out':
            self.PB.add_instruction(f'(PRINT, {args[0]},  ,   )')
            return
        func_name = None
        for var, data in self.variables.items():
            if data.address == func_addr:
                func_name = var
        func = self.variables[func_name]
        print(func_name)
        print()
        if len(args) != len(func.args):
            self.errors.append(self.error_pref() + f'Mismatch in numbers of arguments of \'{func.lexeme}\'.')
        else:
            for i in range(len(args)):
                arg = args[i]
                type_arg = 'int' if (type(arg) == int or arg[0] in ['#', '@']) else 'array'
                if type_arg != func.args[i]:
                    self.errors.append(
                        self.error_pref() + f'Mismatch in type of argument {i + 1} of \'{func.lexeme}\'. Expected \'{func.args[i]}\' but got \'{type_arg}\' instead.')

        if func.type == 'int':
            self.SS.append(func.address)

    def get_func(self):
        self.SS.append('args')
        # TODO
        return

    def end_func(self):
        l = self.scope_stack.pop()
        self.symbol_table = self.symbol_table[:l]
        pass

    def end_expression(self):
        pass

    def __call__(self, name, token) -> Any:
        self.token = token
        self.actions[name]()

    def error_pref(self):
        return f'#{scanner.line_no}: Semantic Error! '

    def get_errors(self):
        return '\n'.join(self.errors)
