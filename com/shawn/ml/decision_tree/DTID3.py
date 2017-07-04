# -*- coding:utf-8 -*-
from PlotDT import PlotDT

__author__ = 'shawn'

from math import log
import operator

class ID3(object):
    def __init__(self):
        self.dataSet, self.labels, self.distribution = self.createDataSet()

    def createDataSet(self):
        '''
        用于从外部读取数据，生成feature,label
        '''
        dataSet=[]
        file = open(u'data\data_train.txt', 'r')
        done = 0
        distribution = ['c', 'd', 'c', 'd', 'c', 'd', 'd', 'd', 'd', 'd', 'c', 'c', 'c', 'd']
        while not done:
            aLine = file.readline()
            if(aLine != ''):
                attItem = aLine.split(",")[:-1]
                for j in range(len(attItem)):
                    attItem[j] = attItem[j].strip()
                for i in range(len(distribution)):
                    if(distribution[i] == 'c'):
                        try:
                            attItem[i] = float(attItem[i])
                        except:
                            print attItem[i]
                attItem.append("0" if aLine.split(",")[-1].strip()=='<=50K' else "1")
                dataSet.append(attItem)
            else:
                done = 1
        file.close()   #关闭文件
        label=['age', 'workclass', 'fnlwgt', 'education', 'education-num', 'marital-status', 'occupation', 'relationship', 'race',
               'sex', 'capital-gain', 'capital-loss', 'hours-per-week', 'native-country']

        return dataSet, label, distribution

    # dataSet, labels, distribution = createDataSet()

    def calcShannonEnt(self, dataSet):
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

    # print calcShannonEnt(self.dataSet)

    def splitLabels(self,dataSet, axis, value):
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

    def splitContiousLabels(self,dataSet, axis, value, lte):
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

    def chooseBestFeatureToSplit(self, dataSet, distribution):
        '''
        选择最好的feature进行分裂
        '''
        numFeature = len(dataSet[0]) -1
        baseEntropy = self.calcShannonEnt(dataSet)
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
                    subDataSet = self.splitLabels(dataSet, i, value)
                    prob=len(subDataSet)/float(len(dataSet))
                    newEntropy += prob*self.calcShannonEnt(subDataSet)
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
                    try:
                        midVals.append(float(sortedUniqueVals[j]+sortedUniqueVals[j+1])/2)
                    except:
                        print i
                for value in midVals:
                    newEntropy = 0.0
                    subDataSet = self.splitContiousLabels(dataSet, i, value, 'y')
                    prob=len(subDataSet)/float(len(dataSet))
                    newEntropy += prob*self.calcShannonEnt(subDataSet)
                    subDataSet = self.splitContiousLabels(dataSet, i, value, 'n')
                    prob=len(subDataSet)/float(len(dataSet))
                    newEntropy += prob*self.calcShannonEnt(subDataSet)
                    infoGain = baseEntropy - newEntropy
                    if(infoGain > bestInfoGain):
                        bestInfoGain = infoGain
                        bestFeature = i
                        bestFeatureValue = value
        return bestFeature, bestFeatureValue

    # print "bestFeature is "+str(chooseBestFeatureToSplit())

    def majorityCnt(self, labels):
        '''
        节点不可再分时，按照投票原则来选择多的类别
        '''
        classCount = {}
        for vote in labels:
            if vote in classCount.keys():
                classCount[vote] = 0
            classCount[vote] += 1
        sortedClassCount = sorted(classCount.iteritems(), key=operator.itemgetter(1), reverse=True)
        return sortedClassCount[0][0]

    def createTree(self, dataSet, labels, distribution):
        classList = [example[-1] for example in dataSet]
        if classList.count(classList[0]) == len(classList):
            return classList[0]
        if len(dataSet[0]) == 1:
            return self.majorityCnt(labels)
        bestFeat, bestFeatValue = self.chooseBestFeatureToSplit(dataSet, distribution)
        bestFeatLabel = labels[bestFeat]
        myTree = {bestFeatLabel:{}}
        if(distribution[bestFeat]=='d'):
            del labels[bestFeat]
            del distribution[bestFeat]
            featVals = [example[bestFeat] for example in dataSet]
            uniqueVals = set(featVals)
            for value in uniqueVals:
                subLabels = labels[:]
                subdistribution = distribution[:]
                myTree[bestFeatLabel][value] = self.createTree(self.splitLabels(dataSet, bestFeat, value), subLabels, subdistribution)
            # dataSet = self.splitLabels(bestFeat)
        elif(distribution[bestFeat]=='c'):
            subLabels = labels[:]
            subdistribution = distribution[:]
            myTree[bestFeatLabel]['<='+str(bestFeatValue)] = self.createTree(self.splitContiousLabels(dataSet, bestFeat, bestFeatValue, 'y'), subLabels, subdistribution)
            myTree[bestFeatLabel]['>'+str(bestFeatValue)] = self.createTree(self.splitContiousLabels(dataSet, bestFeat, bestFeatValue, 'n'), subLabels, subdistribution)
        return myTree

    def classify(self, inputTree, featLabels, testVec):
        firstStr = inputTree.keys()[0]
        secondDict = inputTree[firstStr]
        featIndex = featLabels.index(firstStr)
        for key in secondDict.keys():
            if self.distribution[featIndex] == 'd':
                if testVec[featIndex] == key:
                    if type(secondDict[key]).__name__ == 'dict':
                        classLabel = self.classify(secondDict[key], featLabels, testVec)
                    else:
                        classLabel = secondDict[key]
            elif self.distribution[featIndex] == 'c':
                firstValue = secondDict.keys()[0]
                splitIndex = -1
                if '<=' in firstValue:
                    splitIndex = 2
                else:
                    splitIndex = 1
                splitValue = float(firstValue[splitIndex:])
                if(testVec[featIndex] <= splitValue):
                    if type(secondDict['<='+firstValue[splitIndex:]]).__name__ == 'dict':
                        classLabel = self.classify(secondDict['<='+firstValue[splitIndex:]], featLabels, testVec)
                    else:
                        classLabel = secondDict['<='+firstValue[splitIndex:]]
                else:
                    if type(secondDict['>'+firstValue[splitIndex:]]).__name__ == 'dict':
                        classLabel = self.classify(secondDict['>'+firstValue[splitIndex:]], featLabels, testVec)
                    else:
                        classLabel = secondDict['>'+firstValue[splitIndex:]]
        return classLabel

    def loadTestDataSet(self):
        '''
        用于从外部读取数据，生成feature,label
        '''
        dataSet=[]
        file = open(u'data\data_test.txt', 'r')
        done = 0
        distribution = ['c', 'd', 'c', 'd', 'c', 'd', 'd', 'd', 'd', 'd', 'c', 'c', 'c', 'd']
        while not done:
            aLine = file.readline()
            if(aLine != ''):
                attItem = aLine.split(",")[:-1]
                for j in range(len(attItem)):
                    attItem[j] = attItem[j].strip()
                for i in range(len(distribution)):
                    if(distribution[i] == 'c'):
                        attItem[i] = float(attItem[i])
                attItem.append("0" if aLine.split(",")[-1].strip()=='<=50K' else "1")
                dataSet.append(attItem)
            else:
                done = 1
        file.close()   #关闭文件
        return dataSet


if __name__ == '__main__':
    id3 = ID3()
    inputTree = id3.createTree(id3.dataSet, id3.labels, id3.distribution)

    labels = ['age', 'workclass', 'fnlwgt', 'education', 'education-num', 'marital-status', 'occupation', 'relationship', 'race',
               'sex', 'capital-gain', 'capital-loss', 'hours-per-week', 'native-country']

    testDataSet = id3.loadTestDataSet()
    totalCount = len(testDataSet)
    rightCount = 0
    for item in testDataSet:
        classlabel = id3.classify(inputTree, labels, item[: -1])
        if classlabel == item[-1]:
            rightCount += 1
    print 'totalCount is:%f, rightCount is:%f, right rate is:%f '%(totalCount, rightCount, float(rightCount)/totalCount)



