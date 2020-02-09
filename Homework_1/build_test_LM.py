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
gram_size = 4
token_based = False
start_end = False
case_sensitive = True
strip_out = False
add_one_smoothing = True
use_log = True
max_ignore_rate = 0.5


def build_LM(in_file):
    """
    build language models for each label
    each line in in_file contains a label and a string separated by a space
    """
    print('building language models...')
    # This is an empty method
    # Pls implement your code below in

    # LMs is a dict to store the LM for each language
    LMs = {}
    with open(in_file, 'r') as file:
        for line in file:
            (label, text) = line.strip("\r\n").split(" ", 1)
            if label not in LMs:
                LMs[label] = NgramLM(label, gram_size=gram_size, token_based=token_based,
                                     start_end=start_end, case_sensitive=case_sensitive,
                                     strip_out=strip_out, add_one_smoothing=add_one_smoothing)
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
                probability, ignore_rate = LM[label].predict(line, use_log=use_log)
                if probability > max_prob and ignore_rate < max_ignore_rate:
                    max_label = label
                    max_prob = probability

            print(max_label, line, file=out_file)
            lineno += 1


def usage():
    print("usage: " + sys.argv[0] + " -b input-file-for-building-LM -t input-file-for-testing-LM -o output-file")
    print("options:\n"
          "  -b  building file path\n"
          "  -t  testing file path\n"
          "  -o  prediction result file path\n"
          "  -n  set n-gram size\n"
          "  -r  max ignore rate\n"
          "  -c  disable character-based n-grams, use token-based n-grams\n"
          "  -e  enable adding start-end special character\n"
          "  -s  disable case sensitive, all the tokens will be treated as lowercase\n"
          "  -i  ignore punctuations and numbers, strip out them in text\n"
          "  -a  disable add-one-smoothing\n"
          "  -l  disable using log function which aims to avoid floating point underflow\n")


input_file_b = input_file_t = output_file = None
try:
    opts, args = getopt.getopt(sys.argv[1:], 'b:t:o:n:r:cesial')
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
    elif o == '-n':
        gram_size = int(a)
        assert (0 <= gram_size), 'bad gram size [%d]' % gram_size
    elif o == '-r':
        max_ignore_rate = float(a)
        assert (0 <= max_ignore_rate <= 1.0), 'bad ignore rate [%f]' % max_ignore_rate
    elif o == '-c':
        token_based = True
    elif o == '-e':
        start_end = True
    elif o == '-s':
        case_sensitive = False
    elif o == '-i':
        strip_out = True
    elif o == '-a':
        add_one_smoothing = False
    elif o == '-l':
        use_log = False
    else:
        assert False, "unhandled option"
if input_file_b == None or input_file_t == None or output_file == None:
    usage()
    sys.exit(2)

LM = build_LM(input_file_b)
test_LM(input_file_t, output_file, LM)
