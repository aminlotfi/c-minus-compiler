class Data:
    def __init__(self, lexeme, addr):
        self.lexeme = lexeme
        self.address = addr


class Integer(Data):
    def __init__(self, lexeme, addr):
        super().__init__(lexeme, addr)


class Array(Data):
    def __init__(self, lexeme, addr, length):
        super().__init__(lexeme, addr)
        self.length = length


class Function(Data):
    def __init__(self, lexeme, addr, typ):
        super().__init__(lexeme, addr)
        self.type = typ
        self.args = []

    def add_arg(self, typ):
        self.args.append(typ)
