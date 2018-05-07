#COMP 543, A5
#Chengyin Liu, cl93


import re
import numpy as np
import math

##########################
#task 1

# load up all of the documents in the corpus
#corpus = sc.textFile("/comp543/A5/TestingDataOneLinePerDoc.txt")
#corpus = sc.textFile("s3://risamyersbucket/A5/TestingDataOneLinePerDoc.txt")
corpus = sc.textFile("s3://risamyersbucket/A5/TrainingDataOneLinePerDoc.txt")

# each entry in validLines will be a line from the text file
validLines = corpus.filter(lambda x : 'id' in x)

# now we transform it into a bunch of (docID, text) pairs
keyAndText = validLines.map(lambda x : (x[x.index('id="') + 4 : x.index('" url=')], x[x.index('">') + 2 : x.index('</doc>')]))

# now we split the text in each (docID, text) pair into a list of words
# after this, we have a data set with (docID, ["word1", "word2", "word3", ...])
# we have a bit of fancy regular expression stuff here to make sure that we do not
# die on some of the documents
regex = re.compile('[^a-zA-Z]')
keyAndListOfWords = keyAndText.map(lambda x : (str(x[0]), regex.sub(' ', x[1]).lower().split()))

# now get the top 20,000 words... first change (docID, ["word1", "word2", "word3", ...])
# to ("word1", 1) ("word2", 1)...
allWords = keyAndListOfWords.flatMap(lambda x: ((j, 1) for j in x[1]))

# now, count all of the words, giving us ("word1", 1433), ("word2", 3423423), etc.
allCounts = allWords.reduceByKey(lambda a, b: a + b)

# and get the top 20,000 words in a local array
# each entry is a ("word1", count) pair
topWords = allCounts.top(20000, lambda x : x[1])

# and we'll create a RDD that has a bunch of (word, dictNum) pairs
# start by creating an RDD that has the number 0 thru 20000
# 20000 is the number of words that will be in our dictionary
twentyK = sc.parallelize(range(20000))

# now, we transform (0), (1), (2), ... to ("mostcommonword", 1) ("nextmostcommon", 2), ...
# the number will be the spot in the dictionary used to tell us where the word is located
# HINT: make use of topWords in the lambda that you supply
dictionary = twentyK.map(lambda x: (topWords[x][0], x))

def lookupList(wordList):
	for i in range(len(wordList)):
		pos = dictionary.lookup(wordList[i])
		if len(pos) < 1 or pos[0] < 0 or pos[0] > 19999:
			print -1
		else:
			print pos[0]


#test result
wordList = ['applicant', 'and', 'attack', 'protein', 'car']
lookupList(wordList)


##########################
#task 2
#(word, docId)
#[(u'purported', 'AU11')]
#wordDoc.count() = 32731546
wordDoc = keyAndListOfWords.flatMap(lambda x: ((j, x[0]) for j in x[1]))
#(word, (dicPos, docId))
#[(u'verses', (8060, '28324998'))]
#wordDicDoc.count() = 30554707
wordDicDoc = dictionary.join(wordDoc)
#(docId, dicPos)
#('AU98', 12643)
#[('3573484', 8060)]
#docDic.count() = 30554707
docDic = wordDicDoc.map(lambda x: (x[1][1], x[1][0]))
#(docId, [dicPos0, dicPos1, ...])
#('AU98', <pyspark.resultiterable.ResultIterable at 0x7f19bcdf3110>)
#docDicList.count() = 18724
docDicList = docDic.groupByKey()

#the conversion from listOfAllDictonaryPos to NumPy array
#dim = 20000
dim = dictionary.count()
def listToArray(docDicList, dim):
	result = np.zeros(dim)
	for i in docDicList:
		result[i] += 1
	return result

#(docId, array([word0Count, word1Count, ...]))
#('AU98', array([73., 32.,  7., ...,  0.,  0.,  0.]))
docDicCount = docDicList.map(lambda x: (x[0], listToArray(x[1], dim)))
#(docId, array([tf0, tf1, ...]))
#('AU98', array([0.10296192, 0.04513399, 0.00987306, ..., 0., 0., 0.]))
tf = docDicCount.map(lambda x: (x[0], np.divide(x[1], np.sum(x[1]))))
#(docId, array([word0Exist, word1Exist, ...]))
#('AU98', array([1, 1, 1, ..., 0, 0, 0]))
docDicOne = docDicCount.map(lambda x: (x[0], np.where(x[1] > 0, 1, 0)))
#df = array([18722, 18723, 18718, ...,     9,    34,    33])
#df.shape = (20000, 0)
df = docDicOne.reduce(lambda a, b: (('', np.add(a[1], b[1]))))[1]
#docNum = 18724
docNum = tf.count()
#array([18724, 18724, 18724, ..., 18724, 18724, 18724])
docNumVector = np.full(dim, docNum)
#array([0.  , 0.   , 0.  , ..., 7.64012317, 6.30991828, 6.3403593 ])
idf = np.log(np.divide(docNumVector, df))
#(docId,  array([tfidf0, tfidf1, ...]))
#('AU98', array([0., 0., 0., ..., 0., 0., 0.]))
tfidf = tf.map(lambda x: (x[0], np.multiply(x[1], idf)))

#normalize training data
#array([0.00000000e+00, 0.00000000e+00, 0.00000000e+00, ..., 1.83949776e-05, 1.86049058e-05, 2.05179275e-05])
meanVector = tfidf.values().sum() / tfidf.values().count()
#array([0.   , 0.   , 0.    , ..., 0.00153214, 0.00126482, 0.00150243])
sdVector = tfidf.values().sampleStdev()
#array([1.   , 1.   , 1.     , ..., 0.00153214, 0.00126482, 0.00150243])
sdVector[sdVector == 0] = 1
#(docId,  array([tfidfNorm0, tfidfNorm1, ...]))
#('AU98', array([ 0. ,  0. ,  0. , ..., -0.0120061 , -0.01470957, -0.01365651]))
#[('3289553', array([ 0.  ,  0.  ,  0.  , ..., -0.02067663, -0.04213051, -0.03380713]))]
tfidfNorm = tfidf.map(lambda x: (x[0], (x[1] - meanVector) / sdVector))
#tfidfNorm = tfidfNormNan.map(lambda x: (x[0], np.nan_to_num(x[1])))

#get classLabels
#('AU98', (array, 1))
tfidfLabel = tfidfNorm.map(lambda x: (x[0], (x[1], (1 if(x[0][0:2] == 'AU') else 0))))

#initialize regression coeficients
#array([0., 0., 0., ..., 0., 0., 0.])
#weights.shape = (20000,)
weights = np.zeros((dim,))
#iteration number
maxCycles = 100
#loss dif
lossDif = 0.0001
#learning rate
alpha = 0.05
#initial penalization
reg = 0.001

def sigmoid(inX):
	return 1.0 / (1.0 + math.exp(-inX))

loss = 1.0
lossPre = 1.0
#gradient descent
for i in range(maxCycles):
	#('AU98', (array, 1, 0.5))
	tfidfLabelH = tfidfLabel.map(lambda x: (x[0], (x[1][0], x[1][1], sigmoid(np.dot(x[1][0], weights)))))
	tfidfLabelH = tfidfLabelH.map(lambda x: (x[0], (x[1][0], x[1][1], (1 - 1e-9) if(x[1][2] >= 1) else x[1][2])))
	#('AU98', 0.6931471805599453)
	cost = tfidfLabelH.map(lambda x: (x[0], (- x[1][1] * math.log(x[1][2]) - (1 - x[1][1]) * math.log(1 - x[1][2]))))
	#loss = 0.693147180559926
	#loss = (1.0 / docNum) * (cost.reduce(lambda a, b: (('', a[1] + b[1])))[1])
	loss = (1.0 / docNum) * (cost.reduce(lambda a, b: (('', a[1] + b[1])))[1]) + reg / (2.0 * docNum) * np.sum(np.square(weights))
	print i, ':', loss
	#('AU98', (array([ 0. ,  0. ,  0. , ..., -0.0120061 ,-0.01470957, -0.01365651]), -0.5))
	tfidfError = tfidfLabelH.map(lambda x: (x[0], (x[1][0], x[1][2] - x[1][1])))
	#('AU98', array([-0. , -0. , -0. , ...,  0.00600305, 0.00735479,  0.00682826]))
	tfidfGra = tfidfError.map(lambda x: (x[0], x[1][0] * x[1][1]))
	#array
	tfidfGraSum = tfidfGra.reduce(lambda a, b: (('', np.add(a[1], b[1]))))[1]
	#array([ 0.00000000e+00,  0.00000000e+00,  0.00000000e+00, ...,2.41737957e-07,  1.77384285e-07, -5.27398309e-07])
	#weightsUpdate = alpha * (1.0 / docNum) * tfidfNormGraSum
	weightsUpdate = alpha * ((1.0 / docNum) * tfidfGraSum + (reg / docNum) * weights)
	#array([ 0.00000000e+00,  0.00000000e+00,  0.00000000e+00, ..., -2.41737957e-06, -1.77384285e-06,  5.27398309e-06])
	#weights.shape = (20000,)
	weights = weights - weightsUpdate
	if abs(loss - lossPre) < lossDif:
		break
	if loss <= lossPre:
		alpha *= 1.05
	else:
		alpha *= 0.5
	lossPre = loss

#weights
#array([ 0. ,  0. ,  0. , ...,  0.01058728, -0.00357445, -0.00044511])
print weights


#test result
K = 50
#(19999, u'tempore')
dictionaryNumWord = dictionary.map(lambda x: (x[1], x[0]))
#array([dicPos0, dicPos1, ...])
#weightsTopK.shape = (50,)
weightsTopK = weights.argsort()[-K:][::-1]
#weights[np.argpartition(weights, -K)[-K:]]
for i in weightsTopK:
	pos = dictionaryNumWord.lookup(i)
	print pos[0]


##########################
#task 3
#input_test = sc.textFile("/comp543/A5/SmallTrainingDataOneLinePerDoc.txt")
#input_test = sc.textFile("s3://risamyersbucket/A5/SmallTrainingDataOneLinePerDoc.txt")
input_test = sc.textFile("s3://risamyersbucket/A5/TestingDataOneLinePerDoc.txt")

validLines_test = input_test.filter(lambda x : 'id' in x)
keyAndText_test = validLines_test.map(lambda x : (x[x.index('id="') + 4 : x.index('" url=')], x[x.index('">') + 2 : x.index('</doc>')]))
regex = re.compile('[^a-zA-Z]')
keyAndListOfWords_test = keyAndText_test.map(lambda x : (str(x[0]), regex.sub(' ', x[1]).lower().split()))
wordDoc_test = keyAndListOfWords_test.flatMap(lambda x: ((j, x[0]) for j in x[1]))
wordDicDoc_test = dictionary.join(wordDoc_test)
docDic_test = wordDicDoc_test.map(lambda x: (x[1][1], x[1][0]))
docDicList_test = docDic_test.groupByKey()
docDicCount_test = docDicList_test.map(lambda x: (x[0], listToArray(x[1], dim)))
tf_test = docDicCount_test.map(lambda x: (x[0], np.divide(x[1], np.sum(x[1]))))
tfidf_test = tf_test.map(lambda x: (x[0], np.multiply(x[1], idf)))
tfidfNorm_test = tfidf_test.map(lambda x: (x[0], (x[1] - meanVector) / sdVector))

#predict
#('AU990', (1, 0.7824348231325567))
labelH_test = tfidfNorm_test.map(lambda x: (x[0], ((1 if(x[0][0:2] == 'AU') else 0), np.dot(x[1], weights))))
#threshold probability
t = 20
#('AU990', (1, 1))
labelPredict = labelH_test.map(lambda x: (x[0], (x[1][0], 1 if(x[1][1] > t) else 0)))

#TP =74
TP = labelPredict.map(lambda x: (x[0], 1 if(x[1][0] == 1 and x[1][1] == 1) else 0)).values().sum()
#FP = 6
FP = labelPredict.map(lambda x: (x[0], 1 if(x[1][0] == 0 and x[1][1] == 1) else 0)).values().sum()
#P =74
P = labelPredict.map(lambda x: (x[0], 1 if(x[1][0] == 1) else 0)).values().sum()
#precision = 0.925
precision = (1.0 * TP) / (TP + FP)
#recall = 1.0
recall = (1.0 * TP) / P
#f1 = 0.961038961038961
#f1 = 0.9826897470039947
f1 = 2 * precision * recall / (precision + recall)

#3 false positives
fpOneZero = labelPredict.map(lambda x: (x[0], 1 if(x[1][0] == 0 and x[1][1] == 1) else 0))
fp3 = fpOneZero.top(3, lambda x: x[1])
for i in range(3):
	keyAndText_test.lookup(fp3[i][0])
