import re
import sys
import os
import fileinput

from scanner import first_setup
from parser_1 import Parser
from anytree import RenderTree

with open('input.txt', 'r') as f:
    lines = f.read().split('\n')
    lines_count = len(lines)
first_setup()
with open("input.txt", "r") as f:
    parser = Parser(f, lines_count)

if parser.code_gen.errors:
    with open('output.txt', 'w') as f:
        f.write('The output code has not been generated.')
    with open('semantic_errors.txt', 'w') as f:
        f.write(parser.code_gen.get_errors())

else:
    with open('output.txt', 'w') as f:
        f.write(parser.code_gen.PB.get_block())
    with open('semantic_errors.txt', 'w') as f:
        f.write('The input program is semantically correct.\n')