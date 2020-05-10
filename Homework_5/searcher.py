#!/usr/bin/python3

import sys
import math
import nltk
import array
import heapq
import numpy as np
from indexer import Indexer
from refiner import Refiner
from refiner import QueryInfo
from nltk.corpus import stopwords
from collections import defaultdict
from nltk.stem.porter import PorterStemmer

class Searcher:
    """ Searcher is a class dealing with real-time querying.
        It implements the ranked retrieval based on the VSM(Vector Space Model).
        It also support Phrasal Queries and Pivoted Normalized Document Length.

    Args:
        dictionary_file: the file path of the dictionary
        postings_file: the file path of the postings
        rate: the penalty rate of the pivoted normalized document length
        expand: boolean indicator for using Query Expansion
        feedback: boolean indicator for using Relevance Feedback
        pagerank: boolean indicator for using page rank algorithm
        pivoted: boolean indicator for using pivoted normalized document length
    """

    def __init__(self, dictionary_file, postings_file, rate = 0.01, alpha = 0.1,
                 expand = True, feedback = True, pagerank = True, pivoted = False, score = False):
        self.dictionary_file = dictionary_file
        self.postings_file = postings_file
        self.rate = rate
        self.alpha = alpha
        self.pagerank = pagerank
        self.pivoted = pivoted
        self.score = score

        self.stemmer = PorterStemmer()
        self.indexer = Indexer(dictionary_file, postings_file)
        self.refiner = Refiner(indexer=self.indexer, expand=expand, feedback=feedback)

        self.indexer.LoadDict()

    """ Search and return docIds according to the boolean expression.

    Args:
        query: the query string

    Returns:
        result: the list of K most relevant docIds in response to the query
    """
    def search(self, query, relevant_docs):
        # step 1: let refiner to refine the query and get query_infos
        query_infos, postings_lists = self.refiner.refine(query, relevant_docs)

        # step 2: get candidate docs that need to rank(phrasal query)
        # step 2-1: get all the docs that contains all the terms in the query
        self._get_intersection(query_infos, postings_lists)

        # step 2-2: judging every doc whether it contains the phrase
        self._judge(query_infos, postings_lists)

        # step 3: rank documents get the result
        result, score = self.rank(query_infos, postings_lists)

        # step 4: return the result
        return result, score

    """ Rank the documents and return the K most relevant docIds.
        The result should be in the order of relevant.

    Args:
        query_infos: a list of instances of QueryInfo that contains the query
        postings_lists: the dictionary with terms to posting lists mapping

    Returns:
       result: the list of K most relevant docIds in response to the query
       score: the list of the scores corresponding to the docIds
    """
    def rank(self, query_infos, postings_lists):
        total_scores = None

        # step 1: use different algorithm to rank the documents
        if self.pagerank:
            # step 1-1: use page rank algorithm
            total_scores = self._page_rank(query_infos, postings_lists)
        else:
            # step 1-2: use VSM(vector Sapce Model)
            total_scores = self._vector_rank(query_infos, postings_lists)

        # step 2: get the topK docs from the heap
        heap = [(total_scores[doc], -doc) for doc in total_scores]
        heap = heapq.nlargest(len(total_scores), heap, key=lambda x: x)

        result = [-item[1] for item in heap]

        score = []
        if self.score:
            score = [item[0] for item in heap]

        # step 3: return the topK docs
        return result, score

    """ Rank the documents based on PageRank algorithm

    Args:
        query_infos: a list of instances of QueryInfo that contains the query
        postings_lists: the dictionary with terms to posting lists mapping

    Returns:
       total_scores: the dictionary to record the score of each document
    """
    def _page_rank(self, query_infos, postings_lists):
        total_scores = defaultdict(lambda: 0)

        for query_info in query_infos:
            # step 1: Initialize variables
            terms = query_info.terms

            # step 2: get universe of the docs
            universe, universe_set = self._get_universe(terms, postings_lists)
            doc_num = len(universe)

            # step 3: generate probability transition matrix
            matrix = self._generate_matrix(universe, universe_set)
            scores = np.zeros((doc_num, ))
            scores[0] = 1.0

            print(matrix)
            print(scores)
            input()
            # step 4: perform page rank algorithm
            while True:
                _scores = np.dot(matrix, scores)
                loss = np.sum(np.abs(_scores - scores))
                print('loss', loss)
                scores = _scores
                if loss < 1e-5:
                    break

            print(scores)

            # step 5: update total scores
            for i in range(doc_num):
                doc = universe[i]
                total_scores[doc] += scores[i]

        return total_scores

    """ Rank the documents based on VSM(Vector Space Model)

    Args:
        query_infos: a list of instances of QueryInfo that contains the query
        postings_lists: the dictionary with terms to posting lists mapping

    Returns:
       total_scores: the dictionary to record the score of each document
    """
    def _vector_rank(self, query_infos, postings_lists):
        total_scores = defaultdict(lambda: 0)

        for query_info in query_infos:
            # step 1: Initialize variables
            terms = query_info.terms
            scores = defaultdict(lambda: 0)
            query_vector = query_info.query_vector

            # step 2: processing every document and every term
            for i, term in enumerate(terms):
                candidates = query_info.candidates
                postings_list = postings_lists[term]
                postings = postings_list[1]
                weights = postings_list[2]

                for j in range(0, len(postings)):
                    doc = postings[j]

                    if query_info.is_phrase and (doc not in candidates):
                        continue

                    weight = weights[j]
                    scores[doc] += weight * query_vector[i]

            # step 3: use pivoted document length
            """
            for doc in scores:
                length = self.total_doc[doc]
                if self.pivoted:
                    piv = 1 - self.rate + self.rate * length / self.average
                    scores[doc] /= length * piv
                else:
                    scores[doc] /= length
            """

            # step 4: update total scores
            for doc in scores:
                total_scores[doc] += scores[doc]

        # step 5: return total scores
        return total_scores

    """ Generate probability transition matrix for PageRank algorithm

    Args:
        universe: the universe of the docs that appear in one of the lists
        universe_set: the universe set of the docs that appear in one of the lists
    Returns:
        matrix: the submatrix of the entire probability transition matrix
    """
    def _generate_matrix(self, universe, universe_set):
        doc_num = len(universe)
        matrix = np.zeros((doc_num, doc_num))
        base = np.ones((doc_num, )) / doc_num

        for i in range(doc_num):
            out_num = 0
            for j in range(doc_num):
                start = universe[i]
                end = universe[j]
                if end in self.indexer.outlinks[start]:
                    out_num += 1
                    matrix[i][j] = 1

            if out_num:
                matrix[i] /= out_num / (1- self.alpha)
                print(matrix[i])
                matrix[i] += base * self.alpha
            else:
                matrix[i] = base

        return matrix

    """ Get the universe of the docs that appear in one of the lists.

    Args:
        terms: all terms in the query string
        postings_lists: the dictionary with terms to posting lists mapping
    Returns:
        universe: the universe of the docs that appear in one of the lists
        universe_set: the universe set of the docs that appear in one of the lists
    """
    def _get_universe(self, terms, postings_lists):
        universe_set = set()
        for term in terms:
            postings = postings_lists[term][1]
            length = len(postings)
            for i in range(0, length):
                universe_set.add(postings[i])

        universe = list(universe_set)
        return universe, universe_set

    """ Get the intersection of docs

    Args:
        query_infos: a list of instances of QueryInfo that contains the query
        postings_lists: the dictionary with terms to posting lists mapping
    """
    def _get_intersection(self, query_infos, postings_lists):
        for query_info in query_infos:
            terms = query_info.terms

            if not query_info.is_phrase:
                continue

            if len(terms) == 0:
               query_info.candidates = []
               continue

            # optimize the order of the merge
            costs = []
            for term in terms:
                postings = postings_lists[term][1]
                costs.append((term, len(postings)))

            costs.sort(key = lambda key: key[1])

            # perform pairwise merge
            result = postings_lists[costs[0][0]][1]
            for i in range(1, len(costs)):
                term = costs[i][0]
                postings = postings_lists[term][1]

                p1 = p2 = 0
                len1, len2 = len(result), len(postings)
                temp = array.array('i')

                while p1 < len1 and p2 < len2:
                    doc1 = result[p1]
                    doc2 = postings[p2]

                    if doc1 == doc2:
                        temp.append(doc1)
                        p1, p2 = p1 + 1, p2 + 1
                    elif doc1 < doc2:
                        p1 += 1
                    else:
                        p2 += 1

                result = temp

            # update the candidates
            query_info.candidates = set(result)

    """ Judging whether candidate documents contain the phrase

    Args:
        query_infos: a list of instances of QueryInfo that contains the query
        postings_lists: the dictionary with terms to posting lists mapping
    """
    def _judge(self, query_infos, postings_lists):
        for query_info in query_infos:
            tokens = query_info.tokens

            if not query_info.is_phrase:
                continue

            if len(tokens) <= 1:
                continue

            positions = defaultdict(lambda: [])
            candidates = query_info.candidates

            # get postions for docs
            for i, token in enumerate(tokens):
                postings_list = postings_lists[token]
                postings = postings_list[1]
                length = len(postings)
                for j in range(0, length):
                    docId = postings[j]
                    if docId in candidates:
                        positions[docId].append(postings_list[3][j])

            # judging every doc
            ans = set()
            for doc in positions:
                position = positions[doc]
                pointers = [0] * len(position)

                index = 1
                flag = False
                prev_pos = position[0][0]
                while True:
                    pointer = pointers[index]
                    length = len(position[index])

                    while pointer + 1 < length:
                        tmp = position[index][pointer + 1]
                        if tmp <= prev_pos + 1:
                            pointer += 1
                        else:
                            break

                    pointers[index] = pointer
                    cur_pos = position[index][pointer]

                    if cur_pos != prev_pos + 1:
                        index -= 1
                        pointers[index] += 1
                        if pointers[index] >= len(position[index]):
                            break
                        if index == 0:
                            index += 1

                        pointer = pointers[index - 1]
                        prev_pos = position[index - 1][pointer]
                        continue
                    else:
                        prev_pos = cur_pos
                        index += 1
                        if index >= len(position):
                            flag = True
                            break

                if flag:
                    ans.add(doc)

                query_info.candidates = ans

if __name__ == '__main__':
    # Create a Searcher
    searcher = Searcher('test-dictionary.txt', 'test-postings.txt', score=True)

    test_cases = [
        {"query": '"Computer Science" AND Refiner can tokenize query strings into terms and tokens',
         "relevant_docs": [0, 5] },
        {"query": '"Computer Science" AND Refiner can tokenize query strings into terms and tokens',
         "relevant_docs": [0] },
        {"query": '"Computer Science" AND Refiner can tokenize query strings into terms and tokens',
         "relevant_docs": [5] },
        {"query": '"Computer Science" AND Refiner can tokenize query strings into terms and tokens',
         "relevant_docs": []},
        {"query": '"Computer Science"',
         "relevant_docs": [] }
    ]

    for i, test_case in enumerate(test_cases):
        query = test_case['query']
        relevant_docs = test_case['relevant_docs']
        result, score = searcher.search(query, relevant_docs)
        print("test case [%d]"%i)
        print("query:", query)
        print("relevant_docs", relevant_docs)
        print("result", result)
        print("score", score)
        print("")
