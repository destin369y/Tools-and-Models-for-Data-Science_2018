

#For your reference, here is the dictionary-based LDA for use with the first sub-problem.

import numpy as np
import time;
 
# this returns a number whose probability of occurence is p
def sampleValue (p):
        return np.flatnonzero (np.random.multinomial (1, p, 1))[0]
 
# there are 2000 words in the corpus
alpha = np.full (2000, .1)
 
# there are 100 topics
beta = np.full (100, .1)
 
# this gets us the probabilty of each word happening in each of the 100 topics
wordsInTopic = np.random.dirichlet (alpha, 100)
# wordsInCorpus[i] will be a dictionary that gives us the number of each word in the document
wordsInCorpus = {}
 
# generate each doc
for doc in range (0, 50):
        #
        # no words in this doc yet
        wordsInDoc = {}
        #
        # get the topic probabilities for this doc
        topicsInDoc = np.random.dirichlet (beta)
        #
        # generate each of the 2000 words in this document
        for word in range (0, 2000):
                #
                # select the topci and the word
                whichTopic = sampleValue (topicsInDoc)
                whichWord = sampleValue (wordsInTopic[whichTopic])
                #
                # and record the word
                wordsInDoc [whichWord] = wordsInDoc.get (whichWord, 0) + 1
                #
        # now, remember this document
        wordsInCorpus [doc] = wordsInDoc


#print wordsInCorpus[0]
 
start = time.time()
# coOccurrences will be a map where the key is a
# (wordOne, wordTwo) pair, and the value is the number of times
# those two words co-occurred in a document, so this will be a
# value between zero and 50
coOccurrences = {}
# now, have a nested loop that fils up coOccurrences
# YOUR CODE HERE

for doc in range(0, 50):
        for wordOne in wordsInCorpus[doc]:
                for wordTwo in wordsInCorpus[doc]:
                        if coOccurrences.has_key((wordOne, wordTwo)):
                                coOccurrences[(wordOne, wordTwo)] += 1
                        else:
                                coOccurrences[(wordOne, wordTwo)] = 1

#print coOccurrences[(1, 0)]
#print coOccurrences[(0, 1)]

end = time.time()
print end - start







