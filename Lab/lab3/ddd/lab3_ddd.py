
import numpy as np

# there are 2000 words in the corpus
alpha = np.full (2000, .1)

# there are 100 topics
beta = np.full (100, .1)

# this gets us the probabilty of each word happening in each of the 100 topics
wordsInTopic = np.random.dirichlet (alpha, 100)

# produced [doc, topic, word] gives us the number of times that the given word was
# produced by the given topic in the given doc
produced = np.zeros ((50, 100, 2000))

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
                produced[doc, topic] = np.random.multinomial (wordsToTopic[topic], wordsInTopic[topic])

#1
a1 = produced[18, 17, :].sum()
print "answer1: ", a1

#2
a2 = produced[18, 17:46, :].sum()
print "answer2: ", a2

#3
a3 = produced.sum()
print "answer3: ", a3

#4
a4 = produced[:, 17, :].sum()
print "answer4: ", a4

#5
a5 = produced[:, np.array([17, 23]), :].sum()
print "answer5: ", a5

#6
a6 = produced[:, np.arange(0, 100, 2), :].sum()
print "answer6: ", a6

#7
a7 = produced[:, 15, :].sum(0)
print "answer7: ", a7

#8
a8 = produced[:, :, :].sum(0).argmax(0)
print "answer8: ", a8

#9
a9 = produced[:, np.arange(0, 100, 1), produced.sum(0).argmax(1)].sum(0)
print "answer9: ", a9.shape

