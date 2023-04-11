import re
import sys
import os
import fileinput

from scanner import get_next_token, first_setup

if __name__ == '__main__':
    first_setup()
    with open("input.txt", "r") as f:
        la = get_next_token(f)
        while la != "$":
            la = get_next_token(f)
    if os.path.getsize("lexical_errors.txt") == 0:
        with open("lexical_errors.txt", 'w') as f:
            f.write("There is no lexical error.")
    for line in fileinput.input("tokens.txt", inplace=True):
        if not (re.match("\\d+.\t\n", line) or line == '\n'):
            sys.stdout.write(line)
