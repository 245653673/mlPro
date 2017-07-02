# -*- coding:utf-8 -*-
__author__ = 'shawn'

from math import log
import operator

def createDataSet():
    '''
    用于从外部读取数据，生成feature,label
    '''
    dataSet=[]
    file = open(u'data\data_train.txt', 'r')
    done = 0
    distribution = ['c', 'd', 'c', 'd', 'c', 'd', 'd', 'd', 'd', 'd', 'c', 'c', 'c', 'd']
    while not  done:
        aLine = file.readline()
        if(aLine != ''):
            attItem = aLine.split(",")[:-1]
            for i in range(len(distribution)):
                if(distribution[i] == 'c'):
                    attItem[i] = float(attItem[i])
            attItem.append("0" if aLine.split(",")[-1].strip()=='<=50K' else "1")
            dataSet.append(attItem)
        else:
            done = 1
    file.close()   #关闭文件
    label=['age', 'workclass', 'fnlwgt', 'education', 'education-num', 'marital-status', 'occupation', 'relationship', 'race',
           'sex', 'capital-gain', 'capital-loss', 'hours-per-week', 'native-country']

    return dataSet, label, distribution

dataSet, labels, distribution = createDataSet()

def calcShannonEnt(dataSet):
    '''
    计算香浓滴
    '''
    totalCount = len(dataSet)
    labelCounts = {}
    for item in dataSet:
        currentLabel = item[-1]
        if currentLabel not in labelCounts:
            labelCounts[currentLabel] = 0
        labelCounts[currentLabel] +=1
    shannonEnt = 0.0
    for key in labelCounts:
        prob = float(labelCounts[key])/totalCount
        shannonEnt -= prob*log(prob, 2)
    return shannonEnt

print calcShannonEnt(dataSet)

def splitLabels(dataSet, axis, value):
    '''
    计算某个特定值得labels
    '''
    retDataSet = []
    for item in dataSet:
        if item[axis] == value:
            reducedItem = item[:axis]
            reducedItem.extend(item[axis+1:])
            retDataSet.append(reducedItem)
    return retDataSet

def splitContiousLabels(dataSet, axis, value, lte):
    '''
    计算连续值得labels,属性可以重用
    '''
    retDataSet = []
    for item in dataSet:
        if lte=='y':
            if item[axis] <= value:
                retDataSet.append(item)
        if lte=='n':
            if item[axis] > value:
                retDataSet.append(item)
    return retDataSet

def chooseBestFeatureToSplit(dataSet):
    '''
    选择最好的feature进行分裂
    '''
    numFeature = len(dataSet[0]) -1
    baseEntropy = calcShannonEnt(dataSet)
    bestInfoGain = 0.0
    bestFeature = -1
    bestFeatureValue = ''
    for i in range(numFeature):
        # 处理离散值
        if distribution[i] == 'd':
            featList = [example[i] for example in dataSet]
            uniqueVals = set(featList)
            newEntropy = 0.0
            for value in uniqueVals:
                subDataSet = splitLabels(dataSet, i, value)
                prob=len(subDataSet)/float(len(dataSet))
                newEntropy += prob*calcShannonEnt(subDataSet)
            infoGain = baseEntropy - newEntropy
            if(infoGain > bestInfoGain):
                bestInfoGain = infoGain
                bestFeature = i
                bestFeatureValue = value
        #处理连续值
        if distribution[i] == 'c':
            featList = [example[i] for example in dataSet]
            uniqueVals = set(featList)
            sortedUniqueVals = sorted(uniqueVals)
            midVals = []
            for j in range(0, len(sortedUniqueVals)-1, 2):
                midVals.append(float(sortedUniqueVals[j]+sortedUniqueVals[j+1])/2)
            for value in midVals:
                newEntropy = 0.0
                subDataSet = splitContiousLabels(dataSet, i, value, 'y')
                prob=len(subDataSet)/float(len(dataSet))
                newEntropy += prob*calcShannonEnt(subDataSet)
                subDataSet = splitContiousLabels(dataSet, i, value, 'n')
                prob=len(subDataSet)/float(len(dataSet))
                newEntropy += prob*calcShannonEnt(subDataSet)
                infoGain = baseEntropy - newEntropy
                if(infoGain > bestInfoGain):
                    bestInfoGain = infoGain
                    bestFeature = i
                    bestFeatureValue = value
    return bestFeature, bestFeatureValue

print "bestFeature is "+str(chooseBestFeatureToSplit(dataSet))

def majorityCnt(labels):
    '''
    节点不可再分时，按照投票原则来选择多的类别
    '''
    classCount = {}
    for vote in labels:
        if vote in classCount.keys():
            classCount[vote] = 0
        classCount[vote] +=1
    sortedClassCount = sorted(classCount.iteritems(), key=operator.itemgetter(1), reverse=True)
    return sortedClassCount[0][0]

def createTree(dataSet, labels):
    classList = [example[-1] for example in dataSet]
    if classList.count(classList[0]) == len(classList):
        return classList[0]
    if len(dataSet[0]) == 1:
        return majorityCnt(labels)
    bestFeat, bestFeatValue = chooseBestFeatureToSplit(dataSet)
    bestFeatLabel = labels[bestFeat]
    myTree = {bestFeatLabel:{}}
    if(distribution[bestFeat]=='d'):
        del labels[bestFeat]
        del distribution[bestFeat]
        featVals = [example[bestFeat] for example in dataSet]
        uniqueVals = set(featVals)
        for value in uniqueVals:
            subLabels = labels[:]
            myTree[bestFeatLabel][value] = createTree(splitLabels(dataSet, bestFeat, value), subLabels)
    if(distribution[bestFeat]=='c'):
        subLabels = labels[:]
        myTree[bestFeatLabel]['<='+str(bestFeatValue)] = createTree(splitContiousLabels(dataSet, bestFeat, bestFeatValue, 'y'), subLabels)
        myTree[bestFeatLabel]['>'+str(bestFeatValue)] = createTree(splitContiousLabels(dataSet, bestFeat, bestFeatValue, 'n'), subLabels)
    return myTree

print createTree(dataSet, labels)








