import numpy as np
class ZPlaneEstimator:
    def __init__(self):
        self.alpha=[0,0,0]
        self.condition=0

    def fitFromDataset(self,dataset,acquisition):
        #print(dataset['sharpestZ']['value'])
        #print(dataset['sharpestZ']['index'])
        if (acquisition.events.xy_positions is not None) and (acquisition.events.z_start is not None):
            #print('XY Positions')
            #print(acquisition.events.xy_positions)
            #print(len(dataset['sharpestZ']['index']))
            positions = acquisition.events.xy_positions
        elif acquisition.events.xyz_positions is not None:
            #print('XYZ Positions')
            positions = acquisition.events.xyz_positions
        else:
            raise ValueError
        basisSet=[]
        target=[]
        #print(dataset['sharpestZ']['index'])
        for i in range(len(dataset['sharpestZ']['index'])):
            #print(dataset['sharpestZ']['index'][i])
            basisSet.append([1,dataset['sharpestZ']['index'][i][0],dataset['sharpestZ']['index'][i][1]])
            target.append(dataset['sharpestZ']['index'][i][2])
        #print(basisSet)
        #print(target)
        basisSet=np.array(basisSet)
        target=np.array(target)
        self.alpha=np.linalg.lstsq(basisSet,target,rcond=None)[0]
        #print('basis shape:{0}'.format(basisSet.shape))
        #print('target shape:{0}'.format(target.shape))
        #print('alphaShape:{0}'.format(self.alpha.shape))
        #print('alpha:{0}'.format(self.alpha))
    def calculateZFromXYRanges(self,xRange,yRange):
        if not isinstance(xRange,np.ndarray):
            raise TypeError
        if not isinstance(yRange,np.ndarray):
            raise TypeError
        zArea=[]
        for x in xRange:
            zRange=[]
            for y in yRange:
                zRange.append(self.calculateZFromPoint(x,y))
            zArea.append(zRange)
        zArea=np.array(zArea)
        return zArea


    def calculateZFromPoint(self,x,y):
        return self.alpha[0]+self.alpha[1]*x+self.alpha[2]*y

class iZSearchXYPositionOptimizer:
    def optimize(self,xyPositions):
        '''returns reduces set of positions which optimize the Alpha search'''
        pass
class ZSearchXYPositionOptimizerGreedy(iZSearchXYPositionOptimizer):
    def optimize(self,xyPositions,maxNumPoints=9):
        if not isinstance(xyPositions,(list,tuple)):
            raise TypeError
        xyPositions=self.removeDuplicates(xyPositions)
        if len(xyPositions)<maxNumPoints:
            return xyPositions #deal with edge case when small num of positions requested

        N=len(xyPositions)
        distanceMatrix=np.zeros([N,N])
        for i in range(N):
            for j in range(N):
                distanceMatrix[i,j]=self.distanceSquared(xyPositions[i],xyPositions[j])
        maxDistanceIndex=[]
        for i in range(maxNumPoints):
            if i==0:
                ind = np.unravel_index(np.argmax(distanceMatrix, axis=None), distanceMatrix.shape)
                maxDistanceIndex=list(ind)
            else:
                distances = []
                for j in range(len(xyPositions)):
                    distance=0
                    for k in range(len(maxDistanceIndex)):
                        distance=distance+distanceMatrix[j,maxDistanceIndex[k]]
                    distances.append(distance)
                    if j in maxDistanceIndex:
                        distances[-1]=0 #if the proposed distance is in the set already make sure it cant be picked
                newMaxInd=np.argmax(distances, axis=None)
                maxDistanceIndex.append(newMaxInd)
        maxDistancePositions=[]
        for ind in maxDistanceIndex:
            maxDistancePositions.append(xyPositions[ind])
        return maxDistancePositions

    def getStarringPosition(self,xyPositions):
        xyPositions = np.array(xyPositions)
        minXIndeces = np.where(xyPositions[:, 0] == np.min(xyPositions[:, 0]))
        xyPositions_minX = xyPositions[minXIndeces, :][0]
        minYIndeces = np.where(xyPositions_minX[:, 1] == np.min(xyPositions_minX[:, 1]))
        minXVal = xyPositions[:, 0][minXIndeces[0]]
        minYVal = xyPositions_minX[:, 1][minYIndeces]
        position = [np.array([minXVal[0], minYVal[0]])]
        return position

    def distanceSquared(self,position1,position2):
        totalSquaredDistance=0
        for i in range(len(position1)):
            totalSquaredDistance=totalSquaredDistance+(position1[i]-position2[i])**2
        return totalSquaredDistance

    def removeDuplicates(self,items):
        uniqueItemsDict={}
        for i in items:
            key=str(i[0])+"_"+str(i[1])
            uniqueItemsDict[key]=i
        uniqueItems=[]
        for k in uniqueItemsDict.keys():
            uniqueItems.append(uniqueItemsDict[k])
        return uniqueItems


class ZSearchXYPositionOptimizerFull(iZSearchXYPositionOptimizer):
    def optimize(self,xyPositions):
        if not isinstance(xyPositions,list):
            raise TypeError
        return self.removeDuplicates(xyPositions)

    def removeDuplicates(self,items):
        uniqueItemsDict={}
        for i in items:
            key=str(i[0])+"_"+str(i[1])
            uniqueItemsDict[key]=i
        uniqueItems=[]
        for k in uniqueItemsDict.keys():
            uniqueItems.append(uniqueItemsDict[k])
        return uniqueItems