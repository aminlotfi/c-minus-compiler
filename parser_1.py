from reader import read_json
from maker import make_DFAs
from anytree import Node, RenderTree
from scanner import get_next_token
import scanner
from codegen import CodeGenerator


class Parser:
    def __init__(self, f, lines_count):
        self.lines_count = lines_count
        self.f = f
        self.data = read_json()
        self.DFAs = make_DFAs(self.data)
        self.syn_errors = []
        self.process_token()
        self.code_gen = CodeGenerator()
        self.pass_dfa(non_terminal='Program')

    def pass_dfa(self, non_terminal):
        print(non_terminal)
        dfa = self.DFAs[non_terminal]
        dfa_path = dfa.rules[self.token]
        for state in dfa_path:
            if state[0] == '#':
                self.code_gen(state[1:], self.lexeme)
                continue
            if state in self.data['terminals'] or state == '$':
                print(non_terminal, self.lexeme)
                self.process_token()
                continue
            self.pass_dfa(state)

    def process_token(self):
        token = get_next_token(self.f)
        if token == '$':
            label = '$'
        elif token[0] == 'ID':
            label = 'ID'
        elif token[0] == 'NUM':
            label = 'NUM'
        else:
            label = token[1]
        self.token = label
        self.lexeme = token[1] if token != '$' else '$'
