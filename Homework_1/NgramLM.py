#!/usr/bin/python3

import time
from collections import defaultdict

class NgramLM:
    """
        NgramLM is a class aims to create a language model
        and use it to assign a probability to a sequence of words.

        In this class, I use the ngram knowledge will be used to build the LM.
    """

    observed_ngrams = set()

    def __init__(self, name="", gram_size=4,
                 token_based = False, start_end = False,
                 case_sensitive = True, strip_out = False, add_one_smoothing = True):
        assert gram_size > 0, "gram size should be positive"

        # parameters of the language model
        self.name = name
        self.gram_size = gram_size
        self.token_based = token_based
        self.start_end = start_end
        self.case_sensitive = case_sensitive
        self.strip_out = strip_out
        self.add_one_smoothing = add_one_smoothing

        # record n-grams
        self.table = defaultdict(lambda: 0)
        self.total_num = 0

    def train(self, text):
        tokens = self.tokenize(text)
        ngrams_list = self.form_ngrams(tokens)
        for ngrams in ngrams_list:
            self.total_num += 1

            self.table[ngrams] += 1

            # update global vocabulary
            NgramLM.observed_ngrams.add(ngrams)

    def predict(self, text):
        tokens = self.tokenize(text)
        ngrams_list = self.form_ngrams(tokens)
        probability = 1.0

        for ngrams in ngrams_list:
            if ngrams in self.table:
                count = self.table[ngrams]
            else:
                count = 0

            if self.add_one_smoothing:
                probability *= (count + 1) / float(self.total_num + len(NgramLM.observed_ngrams) - len(self.table))
            else:
                probability *= count / float(self.total_num)

            if probability == 0.0:
                break

        return probability

    def tokenize(self, text):
        tokens = []

        if self.token_based:
            text = text.strip().split()

        tokens = [x if self.case_sensitive else x.lower() for x in text]

        # strip out punctuations and numbers
        if self.strip_out:
            tokens = [x for x in tokens if x.isalpha()]

        return tokens

    def form_ngrams(self, tokens):
        if self.start_end:
            tokens = ['^'] + tokens + ['$']

        if len(tokens) < self.gram_size:
            tokens = tokens + [None] * (self.gram_size - len(tokens))

        end_index = len(tokens) - self.gram_size + 1
        ngrams_list = [''.join(tokens[i:i + self.gram_size]) for i in range(end_index)]

        return ngrams_list

    def get_table(self):
        return self.table



