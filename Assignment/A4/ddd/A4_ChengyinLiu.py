
import re
import numpy as np

# load up all of the 19997 documents in the corpus
corpus = sc.textFile("s3://risamyersbucket/comp543_Lab5/20_news_same_line.txt")

# each entry in validLines will be a line from the text file
validLines = corpus.filter(lambda x : 'id' in x)

# now we transform it into a bunch of (docID, text) pairs
keyAndText = validLines.map(lambda x : (x[x.index('id="') + 4 : x.index('" url=')], x[x.index('">') + 2:]))

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

# finally, print out some of the dictionary, just for debugging
#dictionary.top(10)

##########################
#task 1
wordDoc = keyAndListOfWords.flatMap(lambda x: ((j, x[0]) for j in x[1]))
wordDicDoc = dictionary.join(wordDoc)
docDic = wordDicDoc.map(lambda x: (x[1][1], x[1][0]))
docDicList = docDic.groupByKey()

#the conversion from listOfAllDictonaryPos to NumPy array
def listToArray(docDicList):
	result = np.zeros(20000)
	for i in docDicList:
		result[i] += 1
	return result

docDicCount = docDicList.map(lambda x: (x[0], listToArray(x[1])))

#test result
print 'Task1:'
a1 = docDicCount.lookup('20_newsgroups/comp.graphics/37261')
print '20_newsgroups/comp.graphics/37261:'
print a1[0][a1[0].nonzero()]
a2 = docDicCount.lookup('20_newsgroups/talk.politics.mideast/75944')
print '20_newsgroups/talk.politics.mideast/75944:'
print a2[0][a2[0].nonzero()]
a3 = docDicCount.lookup('20_newsgroups/sci.med/58763')
print '20_newsgroups/sci.med/58763:'
print a3[0][a3[0].nonzero()]


##########################
#task 2
tf = docDicCount.map(lambda x: (x[0], np.divide(x[1], np.sum(x[1]))))
docNum = np.full(20000, 19997.0)
docDicOne = docDicCount.map(lambda x: (x[0], np.where(x[1] > 0, 1, 0)))
df = docDicOne.reduce(lambda a, b: ('', np.add(a[1], b[1])))[1]
idf = np.log(np.divide(docNum, df))
tfidf = tf.map(lambda x: (x[0], np.multiply(x[1], idf)))

#test result
print 'Task2:'
a1 = tfidf.lookup('20_newsgroups/comp.graphics/37261')
print '20_newsgroups/comp.graphics/37261:'
print a1[0][a1[0].nonzero()]
a2 = tfidf.lookup('20_newsgroups/talk.politics.mideast/75944')
print '20_newsgroups/talk.politics.mideast/75944:'
print a2[0][a2[0].nonzero()]
a3 = tfidf.lookup('20_newsgroups/sci.med/58763')
print '20_newsgroups/sci.med/58763:'
print a3[0][a3[0].nonzero()]

###########################
#task 3
def predictLabel(k, s):
	stringInput = sc.parallelize(('', s))
	regex = re.compile('[^a-zA-Z]')
	wordOne = stringInput.flatMap(lambda x: ((j, 1) for j in regex.sub(' ', x).lower().split()))
	wordDicOne = dictionary.join(wordOne)
	oneDic = wordDicOne.map(lambda x: (1, x[1][0]))
	oneDicList = oneDic.groupByKey()
	oneDicCount = listToArray(oneDicList.top(1)[0][1])
	tfInput = np.divide(oneDicCount, np.sum(oneDicCount))
	tfidfInput = np.multiply(tfInput, idf)
	docDis = tfidf.map(lambda x: (x[0], np.linalg.norm(x[1] - tfidfInput)))
	docDisTop = docDis.top(k, lambda x: -x[1])
	regexClassId = re.compile('(/)(.*?)(/)')
	classCountDis = {}
	bestClassId = ''
	maxClassCount = 0
	for ddt in docDisTop:
		classId = regexClassId.search(ddt[0]).group(2)
		if classCountDis.has_key(classId):
			classCountDis[classId][0] += 1
			if ddt[1] < classCountDis[classId][1]:
				classCountDis[classId][1] = ddt[1]
		else:
			classCountDis[classId] = [1, ddt[1]]
		if classCountDis[classId][0] > maxClassCount:
			bestClassId = classId
			maxClassCount = classCountDis[classId][0]
		elif classCountDis[classId][0] == maxClassCount:
			if classCountDis[classId][1] < classCountDis[bestClassId][1]:
				bestClassId = classId
				maxClassCount = classCountDis[classId][0]
	return bestClassId


predictLabel (10, 'Graphics are pictures and movies created using computers – usually referring to image data created by a computer specifically with help from specialized graphical hardware and software. It is a vast and recent area in computer science. The phrase was coined by computer graphics researchers Verne Hudson and William Fetter of Boeing in 1960. It is often abbreviated as CG, though sometimes erroneously referred to as CGI. Important topics in computer graphics include user interface design, sprite graphics, vector graphics, 3D modeling, shaders, GPU design, implicit surface visualization with ray tracing, and computer vision, among others. The overall methodology depends heavily on the underlying sciences of geometry, optics, and physics. Computer graphics is responsible for displaying art and image data effectively and meaningfully to the user, and processing image data received from the physical world. The interaction and understanding of computers and interpretation of data has been made easier because of computer graphics. Computer graphic development has had a significant impact on many types of media and has revolutionized animation, movies, advertising, video games, and graphic design generally.')
 
predictLabel (10, 'A deity is a concept conceived in diverse ways in various cultures, typically as a natural or supernatural being considered divine or sacred. Monotheistic religions accept only one Deity (predominantly referred to as God), polytheistic religions accept and worship multiple deities, henotheistic religions accept one supreme deity without denying other deities considering them as equivalent aspects of the same divine principle, while several non-theistic religions deny any supreme eternal creator deity but accept a pantheon of deities which live, die and are reborn just like any other being. A male deity is a god, while a female deity is a goddess. The Oxford reference defines deity as a god or goddess (in a polytheistic religion), or anything revered as divine. C. Scott Littleton defines a deity as a being with powers greater than those of ordinary humans, but who interacts with humans, positively or negatively, in ways that carry humans to new levels of consciousness beyond the grounded preoccupations of ordinary life.')
 
predictLabel (10, 'Egypt, officially the Arab Republic of Egypt, is a transcontinental country spanning the northeast corner of Africa and southwest corner of Asia by a land bridge formed by the Sinai Peninsula. Egypt is a Mediterranean country bordered by the Gaza Strip and Israel to the northeast, the Gulf of Aqaba to the east, the Red Sea to the east and south, Sudan to the south, and Libya to the west. Across the Gulf of Aqaba lies Jordan, and across from the Sinai Peninsula lies Saudi Arabia, although Jordan and Saudi Arabia do not share a land border with Egypt. It is the worlds only contiguous Eurafrasian nation. Egypt has among the longest histories of any modern country, emerging as one of the worlds first nation states in the tenth millennium BC. Considered a cradle of civilisation, Ancient Egypt experienced some of the earliest developments of writing, agriculture, urbanisation, organised religion and central government. Iconic monuments such as the Giza Necropolis and its Great Sphinx, as well the ruins of Memphis, Thebes, Karnak, and the Valley of the Kings, reflect this legacy and remain a significant focus of archaeological study and popular interest worldwide. Egypts rich cultural heritage is an integral part of its national identity, which has endured, and at times assimilated, various foreign influences, including Greek, Persian, Roman, Arab, Ottoman, and European. One of the earliest centers of Christianity, Egypt was Islamised in the seventh century and remains a predominantly Muslim country, albeit with a significant Christian minority.')
 
predictLabel (10, 'The term atheism originated from the Greek atheos, meaning without god(s), used as a pejorative term applied to those thought to reject the gods worshiped by the larger society. With the spread of freethought, skeptical inquiry, and subsequent increase in criticism of religion, application of the term narrowed in scope. The first individuals to identify themselves using the word atheist lived in the 18th century during the Age of Enlightenment. The French Revolution, noted for its unprecedented atheism, witnessed the first major political movement in history to advocate for the supremacy of human reason. Arguments for atheism range from the philosophical to social and historical approaches. Rationales for not believing in deities include arguments that there is a lack of empirical evidence; the problem of evil; the argument from inconsistent revelations; the rejection of concepts that cannot be falsified; and the argument from nonbelief. Although some atheists have adopted secular philosophies (eg. humanism and skepticism), there is no one ideology or set of behaviors to which all atheists adhere.')
 
predictLabel (10, 'President Dwight D. Eisenhower established NASA in 1958 with a distinctly civilian (rather than military) orientation encouraging peaceful applications in space science. The National Aeronautics and Space Act was passed on July 29, 1958, disestablishing NASAs predecessor, the National Advisory Committee for Aeronautics (NACA). The new agency became operational on October 1, 1958. Since that time, most US space exploration efforts have been led by NASA, including the Apollo moon-landing missions, the Skylab space station, and later the Space Shuttle. Currently, NASA is supporting the International Space Station and is overseeing the development of the Orion Multi-Purpose Crew Vehicle, the Space Launch System and Commercial Crew vehicles. The agency is also responsible for the Launch Services Program (LSP) which provides oversight of launch operations and countdown management for unmanned NASA launches.')
 
predictLabel (10, 'The transistor is the fundamental building block of modern electronic devices, and is ubiquitous in modern electronic systems. First conceived by Julius Lilienfeld in 1926 and practically implemented in 1947 by American physicists John Bardeen, Walter Brattain, and William Shockley, the transistor revolutionized the field of electronics, and paved the way for smaller and cheaper radios, calculators, and computers, among other things. The transistor is on the list of IEEE milestones in electronics, and Bardeen, Brattain, and Shockley shared the 1956 Nobel Prize in Physics for their achievement.')
 
predictLabel (10, 'The Colt Single Action Army which is also known as the Single Action Army, SAA, Model P, Peacemaker, M1873, and Colt .45 is a single-action revolver with a revolving cylinder holding six metallic cartridges. It was designed for the U.S. government service revolver trials of 1872 by Colts Patent Firearms Manufacturing Company – todays Colts Manufacturing Company – and was adopted as the standard military service revolver until 1892. The Colt SAA has been offered in over 30 different calibers and various barrel lengths. Its overall appearance has remained consistent since 1873. Colt has discontinued its production twice, but brought it back due to popular demand. The revolver was popular with ranchers, lawmen, and outlaws alike, but as of the early 21st century, models are mostly bought by collectors and re-enactors. Its design has influenced the production of numerous other models from other companies.')
 
predictLabel (10, 'Howe was recruited by the Red Wings and made his NHL debut in 1946. He led the league in scoring each year from 1950 to 1954, then again in 1957 and 1963. He ranked among the top ten in league scoring for 21 consecutive years and set a league record for points in a season (95) in 1953. He won the Stanley Cup with the Red Wings four times, won six Hart Trophies as the leagues most valuable player, and won six Art Ross Trophies as the leading scorer. Howe retired in 1971 and was inducted into the Hockey Hall of Fame the next year. However, he came back two years later to join his sons Mark and Marty on the Houston Aeros of the WHA. Although in his mid-40s, he scored over 100 points twice in six years. He made a brief return to the NHL in 1979–80, playing one season with the Hartford Whalers, then retired at the age of 52. His involvement with the WHA was central to their brief pre-NHL merger success and forced the NHL to expand their recruitment to European talent and to expand to new markets.')
