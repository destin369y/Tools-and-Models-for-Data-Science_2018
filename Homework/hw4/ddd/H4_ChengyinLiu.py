#COMP 543, Homework 4
#Chengyin Liu

import heapq as hq
import numpy as np
import time

#create the covariance matrix
covar = np.zeros ((100,100))
np.fill_diagonal (covar, 1)

#and the mean vector
mean = np.zeros (100)

#create 3000 data points
all_data = np.random.multivariate_normal (mean, covar, 3000)

#now create the 20 outliers
for i in range (1, 20):
    mean.fill (i)
    outlier_data = np.random.multivariate_normal (mean, covar, i)
    all_data = np.concatenate ((all_data, outlier_data))

#k for kNN detection
k = 10

#the number of outliers to return
m = 5

#start the timer
start_time = time.time()

#the priority queue of outliers
outliers = []

#YOUR CODE HERE!
#Task 1
for x1 in range(all_data.shape[0]):
    distances = []
    for x2 in range(all_data.shape[0]):
        if x2 != x1:
            dis = np.linalg.norm(all_data[x1] - all_data[x2])
            hq.heappush(distances, -dis)
            if len(distances) > k:
                hq.heappop(distances)
    hq.heappush(outliers, (-distances[0], x1))
    if len(outliers) > m:
        hq.heappop(outliers)


print("--- %s seconds ---" % (time.time() - start_time))

#print the outliers... 
for outlier in outliers:
    print (outlier)

##################
#Task 2
#start the timer
start_time = time.time()

#the priority queue of outliers
outliers = []

#randomly shuffle the data 
np.random.shuffle(all_data)

for x1 in range(all_data.shape[0]):
    discard = False
    distances = []
    for x2 in range(all_data.shape[0]):
        if x2 != x1:
            dis = np.linalg.norm(all_data[x1] - all_data[x2])
            hq.heappush(distances, -dis)
            if len(distances) > k:
                hq.heappop(distances)
            if (len(distances) == k) and (len(outliers) == m) and (-distances[0] < outliers[0][0]):
                discard = True
                break
    if discard == False:
        hq.heappush(outliers, (-distances[0], x1))
        if len(outliers) > m:
            hq.heappop(outliers)


print("--- %s seconds ---" % (time.time() - start_time))

#print the outliers... 
for outlier in outliers:
    print (outlier)