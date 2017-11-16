#!/usr/bin/env python3

import random, os, sys
from subprocess import check_output

# first argument is the correct program
correct_program = "solution"
in_file = "test_gen.in"

for index in range(1,20):
    in_str = ""
    n = random.randint(1,100000)
    in_str +=  str(n) + "\n"


    correct_out = ""

    with open(in_file, "w") as infile:
        infile.write(in_str)
    with open(in_file, "rb") as infile:
        correct_out = check_output([os.path.abspath(correct_program)], stdin=infile).decode("utf-8")

    os.remove(in_file)

    with open("testdata/secret" + str(index) + ".in", "w") as infile:
        infile.write(in_str)

    with open("testdata/secret" + str(index) + ".out", "w") as outfile:
        outfile.write(correct_out)
