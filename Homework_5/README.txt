This is the README file for A0214251W's submission.
Email Addresses:
e0518535@u.nus.edu

== Python Version ==

We're using Python Version 3.7.6 for this assignment.

== General Notes about this assignment ==

We divide the whole program into two parts, the index part and the search part. The former is to build the inverted index,
calculate and record the normalised weighted tfs corresponding to the postings and save the index into file. The indexer will
also save the term positions in the doc to aid with handling phrasal queries. The searcher loads the inverted index, parse
the query, search for all relevant documents in response to the query.

We adopt the object-oriented programming approach to build the whole project, which greatly reduces the coupling between two parts.

[Indexer]
As for the index part, there are two main functions to solve the problem.
    1. Build index
        1.1 Process and store the fields we identified (court and date)
            1.1.1 Dictionaries are built for these fields, mapping the field content to the doc id
        1.2 Pre-process and store information about the zones (title and content)
            1.2.1 Remove all punctuations from title and content
            1.2.2 Stem the words and change all characters to lower case
            1.2.3 Append ".title" to words found in the title
            1.2.4 Add words to posting and store the doc id
            1.2.5 Store the position of each word in each document
            1.2.6 Index compression techniques used while storing position of each word
	    1.3 Process the term frequencies of each document
	        1.3.1 Normalise and weight the term frequencies
	        1.3.2 Store resulting values in postings corresponding to each term and document
	    1.4 Calculate average length of each document
	        1.4.1 Divide the sum of all lengths of documents by the number of documents
	    1.5 Process postings to increase efficiency when retrieving information later on
	        1.5.1 Convert lists to numpy arrays
	        1.5.2 Sort the numpy arrays

    2. Save to file
	    2.1 For each term, save offset in the dictionary
	    2.2 Dump posting list for term into postings.txt
	    2.3 Dump calculated average in dictionary.txt
	    2.4 Dump mapping of doc ids to document length in dictionary.txt
	    2.5 Dump mapping of court field to doc id in dictionary.txt
	    2.6 Dump mapping of date field to doc id in dictionary.txt
	    2.7 Dump mapping of terms to offset in dictionary.txt

[Refiner]
As for this part, we use query expansion and feedback query to refine the query,
for more details, please look at the comments in the refiner.py

[Searcher]
As for the search part, we use the following steps to process a request.
    1. Tokenize the query into tokens, the program will also count the number of each term
       in the query.
    2. Load postings lists for the terms in the expression from the postings.txt file.
       For terms that appear multiple times in the query, we just load once to reduce memory cost.
       The postings lists include the doc ids, tfs and positions if the phrase query is turned on.
    3. Query Refinement
        3.1 Pseudo Relevant Feedback is used where the documents provided are comp
        3.2 In our case, we decided to do Query Expansion as well
            3.2.1 Retrieve set of similar words to the words in the query and add them to the query before proceeding
    4. Get the docs that need to rank.
       [phrasal query filtering]
       4.1 Get all the docs that contains all the terms in the query.
           Calculate the union of all postings lists, the searcher will merge them
           according to the size of the list.
       4.2 Judging every doc whether it contains the phrase.
           After step 3.1, the candidate docs contain all terms but they may not adjacent.
           So we need to ensure the candidate docs contain the phrase.
    5. Rank the candidate docs and get the result.
       [VSM]
       	   5.1 Construct the query vector
           	Based on the postings lists of terms, we can get the query vector.
           5.2 Processing every document and every term.
           	To get the cosine value of document vector and the query vector as doc's score.
       	   5.3 Divide the score with the document length
           	If the pivoted normalized document length is turned on, the score will be devided by
           	the pivoted normalized document length.
           5.4 Use max-head heap to get all relevant doc ids.
	[PageRank]
	   5.1 Construct matrix
	   5.2 perform pagerank until loss is small enough
           5.3 get the final scores
           5.4 Use max-head heap to get all relevant doc ids.
    6. Return the results

== Files included with this submission ==

* index.py: The file in this assignment using Indexer to build the index and dump to file.
* indexer.py: The file contains the Indexer class which helps to build, load and dump the inverted index.
* search.py: The file in this assignment using Seacher to get all relevant documents.
* searcher.py: The file contains the Searcher class which helps to search the most relevant documents of the query.
* refiner.py: This file contains The Refiner class used to implement query refinement techniques.
* vbcode.py: This file contains the methods used for index compression. (See references - obtained from external library)
* README.txt: This file contains an overview of this assignment and the algorithm's we used to solve it.
* dictionary.txt: This file is generated from index.py, which contains info of average length of documents, length of each document, information of fields as well as position of terms' posting list in postings.txt.
* postings.txt: This file is generated from index.py, which contains idf, doc_id, normalised weighted tf and position of each term in each document.

== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[x] I, A0214251W-A0168291X-A0168954L, certify that we have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, we
expressly vow that we have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.

[ ] I, A0214251W, did not follow the class rules regarding homework
assignment, because of the following reason:

<Please fill in>

We suggest that we should be graded as follows:

<Please fill in>

== References ==
https://nlp.stanford.edu/IR-book/html/htmledition/variable-byte-codes-1.html
This reference was used to understand index compression techniques.
Furthermore, we used external library methods provided by the vbcode repository written by Github user utahta.
We take no credit for the implementation of vbcode.py which is included in our submission and all credit goes to Github user utahta.

External libary Github repo can be found in the following link:
https://github.com/utahta/pyvbcode
