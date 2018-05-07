
#And here is the array-based LDA for use with the second two.

import numpy as np
import time;
 
# there are 2000 words in the corpus
alpha = np.full (2000, .1)
 
# there are 100 topics
beta = np.full (100, .1)
 
# this gets us the probabilty of each word happening in each of the 100 topics
wordsInTopic = np.random.dirichlet (alpha, 100)
 
# wordsInCorpus[i] will give us the vector of words in document i
wordsInCorpus = np.zeros ((50, 2000))
 
# generate each doc
for doc in range (0, 50):
        #
        # get the topic probabilities for this doc
        topicsInDoc = np.random.dirichlet (beta)
        #
        # assign each of the 2000 words in this doc to a topic
        wordsToTopic = np.random.multinomial (2000, topicsInDoc)
        #
        # and generate each of the 2000 words
        for topic in range (0, 100):
                wordsFromCurrentTopic = np.random.multinomial (wordsToTopic[topic], wordsInTopic[topic])
                wordsInCorpus[doc] = np.add (wordsInCorpus[doc], wordsFromCurrentTopic)
 
#task2
start = time.time()
# coOccurrences[i, j] will give the count of the number of times that
# word i and word j appear in the same document in the corpus
coOccurrences = np.zeros ((2000, 2000))
# now, have a nested loop that fils up coOccurrences
for doc in range(0, 50):
        w1 = np.clip (wordsInCorpus[doc], 0, 1)
        coOccurrences += np.outer (w1, w1)

#print coOccurrences[(1, 0)]
#print coOccurrences[(0, 1)]

end = time.time()
print end - start


#task3
start = time.time()
# coOccurrences[i, j] will give the count of the number of times that
# word i and word j appear in the same document in the corpus
coOccurrences = np.zeros ((2000, 2000))
# now, have a nested loop that fils up coOccurrences
w2 = np.clip (wordsInCorpus, 0, 1)
w2t = np.transpose (w2)
coOccurrences = np.dot (w2t, w2)

#print coOccurrences[(1, 0)]
#print coOccurrences[(0, 1)]

end = time.time()
print end - start




