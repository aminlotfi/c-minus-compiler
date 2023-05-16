import re
import sys
import os
import fileinput

from scanner import first_setup
from parser_1 import Parser
from anytree import RenderTree

if __name__ == '__main__':
    with open('input.txt', 'r') as f:
        lines = f.read().split('\n')
        lines_count = len(lines)
    first_setup()
    with open("input.txt", "r") as f:
        parser = Parser(f, lines_count)

    with open('parse_tree.txt', 'w+', encoding="utf-8") as f:
        for pre, _, node in RenderTree(parser.tree):
            f.write("%s%s\n" % (pre, node.name))
        f.truncate(f.tell() - 1)
    with open('syntax_errors.txt', 'w+') as f:
        if len(parser.syn_errors) == 0:
            f.write('There is no syntax error.')
        else:
            for line in parser.syn_errors:
                f.write(line + '\n')

    if os.path.getsize("lexical_errors.txt") == 0:
        with open("lexical_errors.txt", 'w') as f:
            f.write("There is no lexical error.")
    for line in fileinput.input("tokens.txt", inplace=True):
        if not (re.match("\\d+.\t\n", line) or line == '\n'):
            sys.stdout.write(line)
