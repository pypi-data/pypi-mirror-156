import json
import jsonpath
import fnmatch
import pandas as pd
import numpy as np
import re

# 安裝 WordNet
import nltk
nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('omw-1.4', quiet=True)
from nltk.corpus import wordnet as wn

data = open("java_doc/JAVA_DOC.json", "r", encoding='UTF-8').read()
javaDocData = json.loads(data)

javaDocWeightsData = pd.read_csv('java_doc/Java_Doc_Weights.csv', index_col = 0)
javaDocSimilarityData = pd.read_csv('java_doc/Java_Doc_Similarity.csv', index_col = 0)

data = open("java_doc/Java_Doc_Function_Similarity.json", "r", encoding='UTF-8').read()
javaDocFunctionSimilarityData = json.loads(data)

#將相同分數的索引按照索引名稱排序，之後將結果 print 出來
#input: DataFrame similarityDataFrameTop10, str functionNameQueryTerm, str functionName'
def _sort_index(similarityDataFrameTop10, functionNameQueryTerm, functionName):
    if len(similarityDataFrameTop10) > 1:
        scoreList = []    
        scoreList = np.sort(np.unique(similarityDataFrameTop10[functionNameQueryTerm].values))[::-1]
        
        for scoreId, score in enumerate(scoreList):
            dataFrame = similarityDataFrameTop10[similarityDataFrameTop10[functionNameQueryTerm] == score].sort_index()
            
            if scoreId == 0:
                scoreGroupDataFrame = dataFrame
                
            else:                    
                resultGroupDataFrame = pd.concat([scoreGroupDataFrame, dataFrame], axis=0)
                scoreGroupDataFrame = resultGroupDataFrame
                
        if len(scoreList) == 1:
            resultGroupDataFrame = scoreGroupDataFrame
        
        print('------------------------------')
        for splitId, splitString in enumerate(re.split(',|\n', str(functionName))):
            if splitId != len(re.split(',|\n', str(functionName))) - 1:
                if len(splitString) != 0:
                    print(splitString + ',')
            
            else:
                print(splitString + '：\n')
        
        printIndexList = resultGroupDataFrame.index
        printValueList = resultGroupDataFrame.values    
           
        for resultId in range(len(printIndexList)):
            print('NO.' + str(resultId + 1) + ' SIMILARITY：' + str(round(printValueList[resultId][0], 5)))                             
            for splitId, splitString in enumerate(re.split(',|\n', printIndexList[resultId])):
                if splitId != len(re.split(',|\n', printIndexList[resultId])) - 1:
                    if len(splitString) != 0:
                        print(splitString + ',')
                
                else:
                    print(splitString + '\n')      
            
        print('------------------------------')
    
    else:
        print('這個 function 除了自己以外沒有其他相似的 function。')

#用 class 名稱搜尋得到功能敘述
#input str queryTerm, dict data 默認為 javaDocData
def class_name_to_describe(queryTerm, data = javaDocData):
    numberOfExecutions = 0
    
    for className in data:
        if className.split('_')[-1] == queryTerm.split('_')[-1]:               
            print(className + ':\nDescribe:\n', data[className]['Describe'], '\n')
            numberOfExecutions += 1

    if numberOfExecutions == 0:
        print('查無此 class，或著您的搜尋詞有輸入錯誤。')

#用功能敘述搜尋 class 名稱
def describe_to_class_name(queryTerm, data = javaDocWeightsData):
    lemmatizer = nltk.stem.WordNetLemmatizer()
    stop_words = set(nltk.corpus.stopwords.words('english'))
    
    word_set = nltk.word_tokenize(queryTerm.lower())        
    # remove stop words
    word_set = [w for w in word_set if w not in stop_words]
    # lemmatization
    word_set = [lemmatizer.lemmatize(w) for w in word_set]
    
    wordList = []
    for word in word_set:
        if word in data.index:        
            wordList.append(word)
    
    if len(word_set) != 0 and len(wordList) != 0:
        queryTermWeightsList = []
        for word in wordList:
            wordWeights = pd.DataFrame(data.loc[word])
            wordWeights.columns = ['weights']        
            wordWeights.drop(wordWeights[wordWeights['weights'] == 0].index, inplace = True)
            queryTermWeightsList.append([wordWeights.index.tolist(), wordWeights.values.tolist()])
        
        if len(wordList) != 1:        
            for queryTermWeightsId, queryTermWeights in enumerate(queryTermWeightsList):
                if queryTermWeightsId == 0:
                    intersection = list(set(queryTermWeightsList[0][0]).intersection(set(queryTermWeightsList[1][0])))
                    union = list(set(queryTermWeightsList[0][0]).union(set(queryTermWeightsList[1][0])))
                    
                else:
                    intersection = list(set(intersection).intersection(set(queryTermWeights[0])))
                    union = list(set(union).union(set(queryTermWeights[0])))
            
            intersectionWeightsList = []
            unionWeightsList = []
            
            for intersectionWord in intersection:
                weightScore = 0
                
                for queryTermWeights in queryTermWeightsList:
                    weightScore += queryTermWeights[1][queryTermWeights[0].index(intersectionWord)][0]
                
                intersectionWeightsList.append(weightScore)
            
            for unionWord in union:
                weightScore = 0
                
                for queryTermWeights in queryTermWeightsList:
                    if unionWord in queryTermWeights[0]:
                        weightScore += queryTermWeights[1][queryTermWeights[0].index(unionWord)][0]
                        
                    else:
                        weightScore += 0
                    
                unionWeightsList.append(weightScore)
            
            intersectionWeightsList = pd.DataFrame(intersectionWeightsList, index=intersection, columns=['weights'])
            intersectionWeightsList = intersectionWeightsList.sort_values(by = ['weights'], ascending = False)
            
            if len(intersection) < 10:
                unionWeightsList = pd.DataFrame(unionWeightsList, index=union, columns=['weights'])
                
                for intersectionWord in intersection:
                    unionWeightsList.drop(intersectionWord, inplace = True)
                
                unionWeightsList = unionWeightsList.sort_values(by = ['weights'], ascending = False)        
                resultWeightsList = pd.concat([intersectionWeightsList, unionWeightsList], axis=0)
                print(resultWeightsList[:10])                
                
            else:
                print(intersectionWeightsList[:10])                
        
        else:
            wordWeights = wordWeights.sort_values(by = ['weights'], ascending = False)
            print(wordWeights[:10])            
    
    else:
        print('您並沒有輸入任何的搜索詞，或者您的搜索詞皆為停用詞，或者您的搜索詞皆不在資料集中')

#用 class 的功能敘述搜尋相似的 class
def class_describe_to_similar_class_name(queryTerm, data = javaDocSimilarityData):
    numberOfExecutions = 0
    
    for className in data:
        if className.split('_')[-1] == queryTerm.split('_')[-1]:               
            queryTermSimilarity = pd.DataFrame(data[className])
            queryTermSimilarity.columns = ['Similarity']
            queryTermSimilarity = queryTermSimilarity.sort_values(by = ['Similarity'], ascending = False)
            print(className + ':')
            print(queryTermSimilarity[1:11], '\n')
            numberOfExecutions += 1

    if numberOfExecutions == 0:
        print('查無此 class，或著您的搜尋詞有輸入錯誤。')        

#用 class 名稱加 function 功能敘述，搜尋同一個 class 之下類似的 function      
def class_name_and_function_name_to_similar_function_name(classNameQueryTerm, functionNameQueryTerm, mode = 0, data = javaDocFunctionSimilarityData):
    if mode == 0 or mode == 1:        
        classNumberOfExecutions = 0
    
        for className in data:
            if className.split('_')[-1] == classNameQueryTerm.split('_')[-1]:
                print('\n' + className + ':')
                numberOfExecutions = 0
            
                for functionName in data[className]:                    
                    if functionNameQueryTerm == nltk.word_tokenize(functionName)[0]:
                        values = data[className][functionName].values()
                        index = data[className][functionName].keys()
                
                        similarityDataFrame = pd.DataFrame(values, index = index, columns = [functionNameQueryTerm])
                        similarityDataFrame.drop(similarityDataFrame[similarityDataFrame[functionNameQueryTerm] == 0].index, inplace = True)
                        similarityDataFrame = similarityDataFrame.sort_values(by = [functionNameQueryTerm], ascending = False)
                        
                        if mode == 0:                
                            index = similarityDataFrame.index
                            values = similarityDataFrame[functionNameQueryTerm].values
                            noIncludeQueryTermKeyList = []
                            noIncludeQueryTermValuesList = []
                            
                            for indexNum, indexName in enumerate(index):                
                                if functionNameQueryTerm != nltk.word_tokenize(indexName)[0]:
                                    noIncludeQueryTermKeyList.append(indexName)
                                    noIncludeQueryTermValuesList.append(round(values[indexNum], 5))
                                    
                            noIncludeQueryTermDataFrame = pd.DataFrame(noIncludeQueryTermValuesList, index = noIncludeQueryTermKeyList, columns = [functionNameQueryTerm])
                            similarityDataFrameTop10 = noIncludeQueryTermDataFrame[:10]
                            
                        elif mode == 1:              
                            similarityDataFrameTop10 = similarityDataFrame[1:11]
                            
                        _sort_index(similarityDataFrameTop10, functionNameQueryTerm, functionName)
            
                        numberOfExecutions += 1
                
                classNumberOfExecutions += 1
                
                if numberOfExecutions == 0:
                    print('查無此 function，或者您的搜尋詞輸入錯誤，或是該 function 無功能敘述。')
                    
        if classNumberOfExecutions == 0:
            print('查無此 class，或著您的搜尋詞有輸入錯誤，或是該類別沒有 function。')
            
    else:
        print('模式輸入錯誤請輸入 0 或 1')
    

'''---------------------------------------------------------------------------------------------------------'''        
#class_name_to_describe('JButton')
#describe_to_class_name('a structure with key and value')
#class_describe_to_similar_class_name('ArrayList')
#class_name_and_function_name_to_similar_function_name('Arrays', 'sort')
