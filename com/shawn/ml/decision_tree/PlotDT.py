# -*- coding:utf-8 -*-
__author__ = 'shawn'
import matplotlib.pyplot as plt

class PlotDT(object):
    decisionNode = dict(boxstyle="sawtooth", fc="0.8")
    leafNode = dict(boxstyle="round4", fc="0.8")
    arrow_args = dict(arrowstyle="<-")

    #获得树的叶节点的数目
    def getNumLeafs(self, myTree):
        numLeafs = 0
        firstStr = list(myTree.keys())[0]#获得当前第一个根节点
        secondDict = myTree[firstStr]#获取该根下的子树
        for key in list(secondDict.keys()):#获得所有子树的根节点，进行遍历
            if type(secondDict[key]).__name__ == 'dict':#如果子节点是dict类型，说明该子节点不是叶子节点
                numLeafs += self.getNumLeafs(secondDict[key])#不是子节点则继续往下寻找子节点，直到找到子节点为止
            else:
                numLeafs += 1#找到子节点，数+1
        return numLeafs

    #获得树的层数
    def getTreeDepth(self, myTree):
        treeDepth = 0
        temp = 0
        firstStr = list(myTree.keys())[0]#获得当前第一个根节点
        secondDict = myTree[firstStr]#获取该根下的子树
        for key in list(secondDict.keys()):#获得所有子树的根节点，进行遍历
            if type(secondDict[key]).__name__ == 'dict':#如果子节点是dict类型，说明该子节点不是叶子节点
                temp = 1 + self.getTreeDepth(secondDict[key])#该节点算一层，加上往下数的层数
            else:
                temp = 1#叶子节点算一层
            if temp > treeDepth:
                treeDepth = temp
        return treeDepth

    #计算父节点到子节点的中点坐标，在该点上标注txt信息
    def plotMidText(self, cntrPt, parentPt, txtString):
        xMid = (parentPt[0] - cntrPt[0])/2.0 + cntrPt[0]
        yMid = (parentPt[1] - cntrPt[1])/2.0 + cntrPt[1]
        self.createPlot.ax1.text(xMid, yMid, txtString)


    def plotTree(self, myTree,parentPt,nodeTxt):
        numLeafs = self.getNumLeafs(myTree)
        depth = self.getTreeDepth(myTree)
        firstStr = list(myTree.keys())[0]
        #cntrPt = (plotTree.xOff + (0.5 + float(numLeafs)/2.0/(plotTree.totalW*plotTree.totalW)),plotTree.yOff)
        #cntrPt = (0.5,1.0)
        cntrPt = ((2 * self.plotTree.xOff + (float(numLeafs) + 1) * (1 / self.plotTree.totalW)) / 2, self.plotTree.yOff)
        print(self.plotTree.xOff)
        self.plotMidText(cntrPt, parentPt, nodeTxt)
        self.plotNode(firstStr, cntrPt, parentPt, self.decisionNode)
        secondDict = myTree[firstStr]
        #print(secondDict)
        self.plotTree.yOff = self.plotTree.yOff - 1.0/self.plotTree.totalD
        for key in list(secondDict.keys()):
            if type(secondDict[key]).__name__ == 'dict':
                self.plotTree(secondDict[key], cntrPt, str(key))
            else:
                self.plotTree.xOff = self.plotTree.xOff + 1.0/self.plotTree.totalW
                self.plotNode(secondDict[key], (self.plotTree.xOff,self.plotTree.yOff),cntrPt,self.leafNode)
                self.plotMidText((self.plotTree.xOff, self.plotTree.yOff),cntrPt, str(key))
        self.plotTree.yOff = self.plotTree.yOff + 1.0/self.plotTree.totalD

    def createPlot(self, inTree):
        fig = plt.figure(1, facecolor='white')
        fig.clf()
        axprops = dict(xticks=[], yticks=[])
        self.createPlot.ax1 = plt.subplot(111, frameon=False, **axprops)
        self.plotTree.totalW = float(self.getNumLeafs(inTree))
        self.plotTree.totalD = float(self.getTreeDepth(inTree))
        self.plotTree.xOff = -0.5/self.plotTree.totalW
        self.plotTree.yOff = 1.0
        self.plotTree(inTree, (0.5, 1.0), '')
        plt.show()

    def plotNode(self, nodeTxt, centerPt, parentPt, nodeType):
        self.createPlot.ax1.annotate(nodeTxt, xy=parentPt, xycoords='axes fraction',
                                    xytext=centerPt, textcoords='axes fraction',
                                    va='bottom', ha='center', bbox=nodeType, arrowprops=self.arrow_args)