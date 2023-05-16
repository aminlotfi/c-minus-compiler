import json


def get_rules():
    with open('rules.json') as f:
        rules = json.load(f)
    return rules


class DFA:
    def __init__(self, n_states, has_epsilon, follow):
        self.n_states = n_states
        self.next_state = []
        self.arrow_type = []
        for i in range(n_states - 1):
            self.next_state.append({})
            self.arrow_type.append({})

        if has_epsilon:
            for x in follow:
                self.next_state[0][x] = self.n_states - 1
                self.arrow_type[0][x] = 'EPSILON'

    def add_arrow(self, state1, state2, label, t, first_follow=None):
        if t == 'terminal':
            self.next_state[state1][label] = state2
            self.arrow_type[state1][label] = t
            return
        first, follow = first_follow
        if 'EPSILON' in first:
            for x in follow:
                self.next_state[state1][x] = state2
                self.arrow_type[state1][x] = label
        for x in first:
            if x == 'EPSILON':
                continue
            self.next_state[state1][x] = state2
            self.arrow_type[state1][x] = label


def make_DFAs(data):
    all_rules = get_rules()
    DFAs = {}
    for non_terminal, rules in all_rules.items():
        n_states = 2
        has_epsilon = False
        for rule in rules:
            if rule[0] == 'EPSILON':
                has_epsilon = True
            n_states += len(rule) - 1
        dfa = DFA(n_states, has_epsilon, data['follow'][non_terminal])
        DFAs[non_terminal] = dfa
        curr_state = 1
        for rule in rules:
            for i in range(len(rule)):
                label = rule[i]
                if i == 0:
                    state1 = 0
                else:
                    state1 = curr_state - 1

                if i == len(rule) - 1:
                    state2 = n_states - 1
                else:
                    state2 = curr_state

                if label in data['non-terminal']:
                    t = 'non-terminal'
                    dfa.add_arrow(state1, state2, label, t, (data['first'][label], data['follow'][label]))
                else:
                    t = 'terminal'
                    dfa.add_arrow(state1, state2, label, t)

                if state2 == curr_state:
                    curr_state += 1

    return DFAs
