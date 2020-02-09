#!/usr/bin/python3

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re
import nltk
import sys
import getopt
import time

from NgramLM import NgramLM

# global variable

def build_LM(in_file):
    """
    build language models for each label
    each line in in_file contains a label and a string separated by a space
    """
    print('building language models...')
    # This is an empty method
    # Pls implement your code below in

    LMs = {}
    with open(in_file, 'r') as file:
        for line in file:
            (label, text) = line.strip("\r\n").split(" ", 1)
            if label not in LMs:
                LMs[label] = NgramLM()
            LMs[label].train(text)

    return LMs

def test_LM(in_file, out_file, LM):
    """
    test the language models on new strings
    each line of in_file contains a string
    you should print the most probable label for each string into out_file
    """
    print("testing language models...")
    # This is an empty method
    # Pls implement your code in below

    with open(in_file, 'r') as in_file, \
        open(out_file, 'w') as out_file:
        lineno = 0
        for line in in_file:
            max_label = "other"
            max_prob = -sys.float_info.max
            line = line.strip("\r\n")
            for label in LM:
                probability, ignore_rate = LM[label].predict(line)
                if probability > max_prob and ignore_rate < 0.6:
                    max_label = label
                    max_prob = probability

            print(max_label, line, file=out_file)
            lineno += 1


def usage():
    print("usage: " + sys.argv[0] + " -b input-file-for-building-LM -t input-file-for-testing-LM -o output-file")

input_file_b = input_file_t = output_file = None
try:
    opts, args = getopt.getopt(sys.argv[1:], 'b:t:o:csa')
except getopt.GetoptError:
    usage()
    sys.exit(2)
for o, a in opts:
    if o == '-b':
        input_file_b = a
    elif o == '-t':
        input_file_t = a
    elif o == '-o':
        output_file = a
    else:
        assert False, "unhandled option"
if input_file_b == None or input_file_t == None or output_file == None:
    usage()
    sys.exit(2)

LM = build_LM(input_file_b)
test_LM(input_file_t, output_file, LM)
