import json


def get_rules():
    with open('rules.json') as f:
        rules = json.load(f)
    return rules


class DFA:
    def __init__(self, rules):
        self.rules = rules

def make_DFAs(data):
    all_rules = get_rules()
    DFAs = {}
    for non_terminal, rules_list in all_rules.items():
        rules = {}
        for rule in rules_list:
            first_token = None
            for x in rule:
                if x[0] != '#' and x != 'EPSILON':
                    first_token = x
                    break
            
            if not first_token:
                for terminal in data['follow'][non_terminal]:
                    rules[terminal] = rule if 'EPSILON' not in rule else []
            elif first_token in data['terminals']:
                rules[first_token] = rule
            else:
                for terminal in data['first'][first_token]:
                    if terminal == 'EPSILON':
                        for terminal1 in data['follow'][first_token]:
                            rules[terminal1] = rule
                        continue
                    rules[terminal] = rule
        DFAs[non_terminal] = DFA(rules)
    return DFAs