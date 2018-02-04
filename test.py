#!/bin/end python3

import logging
import os

from lark import Lark
from interpreter import LanceInterpreter


def run_files_in(dir):
    tree = [entry for entry in os.walk(dir)]
    files = []
    for entry in tree:
        path = entry[0]
        for fname in entry[2]:
            files.append(os.path.join(path, fname))

    for f in files:
        run_script(f)


def run_script(filename):
    print("Running {}".format(filename))
    with open(filename) as scriptfile:
        script = scriptfile.read()

    try:
        tree = parser.parse(script)
    except Exception as e:
        print("Exception while parsing {}: {}".format(filename, e))
        return

    # Uncomment to print AST
    # print(tree.pretty())
    evaluator = LanceInterpreter(log_level=logging.DEBUG, mock_input=True)
    try:
        evaluator.evaluate(tree)
    except Exception as e:
        print("Exception while executing {}: {}".format(filename, e))
        return


with open("grammar.lark") as grammar:
    parser = Lark(grammar, start='program', debug=True, parser='lalr')


if __name__ == "__main__":
    run_files_in("tests")
