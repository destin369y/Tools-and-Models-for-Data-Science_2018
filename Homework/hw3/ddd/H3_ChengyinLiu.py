import numpy as np
import scipy.stats as ss

# one coin has a probability of coming up heads of 0.2, the other 0.6
coinProbs = np.zeros (2)
coinProbs[0] = 0.2
coinProbs[1] = 0.6

# reach in and pull out a coin numTimes times
numTimes = 100

#############
#first run with numFlips = 10
print "First run with numFlips = 10:"
#############

# flip it numFlips times when you do
numFlips = 10

# flips will have the number of heads we observed in 10 flips for each coin
flips = np.zeros (numTimes)
for coin in range(numTimes):
        which = np.random.binomial (1, 0.5, 1);
        flips[coin] = np.random.binomial (numFlips, coinProbs[which], 1);

# initialize the EM algorithm
coinProbs[0] = 0.79
coinProbs[1] = 0.51

#counts[0] is the count of heads(1) and tails(0) of coin 0. 
counts = np.zeros(2) 
# run the EM algorithm
for iters in range (20):
    #E step
    contribution0 = ss.binom.pmf(flips, numFlips, coinProbs[0])
    contribution1 = ss.binom.pmf(flips, numFlips, coinProbs[1])
    weight0 = contribution0 / (contribution0 + contribution1)
    weight1 = contribution1 / (contribution0 + contribution1)
    counts[0] = np.sum(weight0 * flips)
    counts[1] = np.sum(weight1 * flips)
    #M step
    coinProbs[0] = counts[0] / np.sum(weight0 * numFlips)
    coinProbs[1] = counts[1] / np.sum(weight1 * numFlips)
    print coinProbs


#############
#second run with numFlips to 2
print "Second run with numFlips = 2:"
#############

# flip it numFlips times when you do
numFlips = 2

# flips will have the number of heads we observed in 10 flips for each coin
flips = np.zeros (numTimes)
for coin in range(numTimes):
        which = np.random.binomial (1, 0.5, 1);
        flips[coin] = np.random.binomial (numFlips, coinProbs[which], 1);

# initialize the EM algorithm
coinProbs[0] = 0.79
coinProbs[1] = 0.51

#counts[0] is the count of heads(1) and tails(0) of coin 0.
counts = np.zeros(2) 
# run the EM algorithm
for iters in range (20):
    #E step
    contribution0 = ss.binom.pmf(flips, numFlips, coinProbs[0])
    contribution1 = ss.binom.pmf(flips, numFlips, coinProbs[1])
    weight0 = contribution0 / (contribution0 + contribution1)
    weight1 = contribution1 / (contribution0 + contribution1)
    counts[0] = np.sum(weight0 * flips)
    counts[1] = np.sum(weight1 * flips)
    #M step
    coinProbs[0] = counts[0] / np.sum(weight0 * numFlips)
    coinProbs[1] = counts[1] / np.sum(weight1 * numFlips)
    print coinProbs

