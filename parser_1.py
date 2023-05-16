from reader import read_json
from maker import make_DFAs
from anytree import Node, RenderTree
from scanner import get_next_token
import scanner


class Parser:
    def __init__(self, f, lines_count):
        self.lines_count = lines_count
        self.f = f
        self.data = read_json()
        self.DFAs = make_DFAs(self.data)
        self.syn_errors = []
        self.token = get_next_token(f)
        self.tree = Node('Program')
        self.pass_dfa(non_terminal='Program', par=self.tree)

    def pass_dfa(self, non_terminal, par):
        dfa = self.DFAs[non_terminal]
        current_state = 0
        while current_state != dfa.n_states - 1:
            if self.token == '$':
                label = '$'
            elif self.token[0] == 'ID':
                label = 'ID'
            elif self.token[0] == 'NUM':
                label = 'NUM'
            else:
                label = self.token[1]
            error = False
            if label in dfa.next_state[current_state]:
                move_type = dfa.arrow_type[current_state][label]
                current_state = dfa.next_state[current_state][label]
            else:
                for tmp in dfa.arrow_type[current_state]:
                    move_type = dfa.arrow_type[current_state][tmp]
                    break
                for tmp in dfa.next_state[current_state]:
                    next_state = dfa.next_state[current_state][tmp]
                    break
                if move_type != 'terminal':
                    if label in self.data['follow'][move_type]:
                        current_state = next_state
                        move_type = 'missing ' + str(move_type)
                        error = True
                    else:
                        move_type = 'illegal ' + str(label)
                        error = True
                else:
                    for tmp in dfa.next_state[current_state]:
                        expected_label = tmp
                        break
                    current_state = next_state
                    move_type = 'missing ' + str(expected_label)
                    error = True

            if error:
                if move_type == 'illegal $':
                    self.syn_errors.append('#' + str(self.lines_count) + ' : syntax error, Unexpected EOF')
                    return False
                self.syn_errors.append('#' + str(scanner.line_no) + ' : syntax error, ' + str(move_type))
                if len(move_type) >= 7 and move_type[0:7] == 'illegal':
                    self.token = get_next_token(self.f)


            elif move_type == 'EPSILON':
                Node(name='epsilon', parent=par)
                return True

            elif move_type == 'terminal':
                if self.token == '$':
                    Node(name='$', parent=par)
                    break
                Node(name='(' + str(self.token[0]) + ', ' + str(self.token[1]) + ')', parent=par)
                self.token = get_next_token(self.f)

            else:
                down_node = Node(move_type, parent=par)
                done = self.pass_dfa(move_type, down_node)
                if not done:
                    return False
        return True
