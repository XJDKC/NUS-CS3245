This is the README file for A0214251W's submission

== Python Version ==

I'm using Python Version 3.7 for this assignment.

== General Notes about this assignment ==

In this assignment, I build language models for the these three models based on the file contains the training data.
And then I use the data in test file to test all the LMs to produce the prediction result file. 

Here is a detailed description of each step 
    1. Parse command line arguments:
        In this step, I parse all the command line arguments including the original and what I added later.
            options:
              -b  building file path
              -t  testing file path
              -o  prediction result file path
              -n  set n-gram size
              -r  max ignore rate
              -c  disable character-based n-grams, use token-based n-grams
              -e  enable adding start-end special character
              -s  disable case sensitive, all the tokens will be treated as lowercase
              -i  ignore punctuations and numbers, strip out them in text
              -a  disable add-one-smoothing
              -l  disable using log function which aims to avoid floating point underflow
        As we can see, there are many arguments we can change to get different LMs. 
        For example, we can change the n value of the n-grams language model, we can train and build a language model that ignores case 
        or even punctuations and numbers. To test different ideas, we can easily change the final trained model by passing command line arguments.
    2. Train and build the LMs:
        In this step, I use the NgramLM class I wrote, read every single line from the input.train.txt to build a LM for every language.
        I use a dict to store the language name and its LM. I tokenize each line of string and then create ngrams to finally record
        the number of times each ngrams appears in a language.
    3. Test the LMs:
        In this step, I use the LMs trained in the previous step to predict which language the strings in the test file belong to.
        To support distinguishing other languages, I calculate the ignore rate of each language. The ignore rate indicates 
        the percentage of total ngrams ignored because they did not appear in any language model. 
        For a string, if the ignore rate of each language exceeds a certain value, then the language is not any of the three languages.
        After collecting the prediction results of all models, I judged which language is most likely to be based on the possibility.

== Files included with this submission ==

1. build_test_LM.py: The core file of this assignment which use the NgramLM class to build and test the LMs.
   In this file, I add more command line parameters to support more features which will be helpful for different tests. 
2. NgramLM.py: This file contains class NgramLM which is constructed by  using the n-grams knowledge.
3. README.txt: This file contains this sentence which give an overview of this assignment

== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[x] I, A0214251W, certify that I have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I
expressly vow that I have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[ ] I, A0214251W, did not follow the class rules regarding homework
assignment, because of the following reason:

<Please fill in>

I suggest that I should be graded as follows:
    1. Complete all the requirements
    2. Good programming habits
    3. Good scalability, if I want to use N-gram LM, just import the NgramLM.py and then use specific parameters to create an instance.

== References ==
    1. [To search some Python functions](https://devdocs.io/python/)
    2. [To avoid underflow in floating point division](https://stackoverflow.com/questions/48180177/prevent-underflow-in-floating-point-division-in-python)
    2. 