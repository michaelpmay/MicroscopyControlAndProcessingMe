from PIL import  Image
import numpy as np
import glob
import matplotlib.pyplot as plt
import pickle
sharpList=[]
blurryList=[]
numFiles=0
class ImageSummaryStatistics:
    def __init__(self):
        self.sharpness=None

    def calculate(self,image):
        statistics=dict()
        statistics['id']=None
        statistics['xPosition'] = None
        statistics['yPosition'] = None
        statistics['distanceFromOrigin']=None
        statistics['meanR'] = self.getMean(image,0)
        statistics['meanG'] = self.getMean(image,1)
        statistics['meanB'] = self.getMean(image,2)
        statistics['stdR'] = self.getStandardDeviation(image,0)
        statistics['stdG'] = self.getStandardDeviation(image,1)
        statistics['stdB'] = self.getStandardDeviation(image,2)
        statistics['sharpnessR']=self.getSharpness(image,0)
        statistics['sharpnessG'] = self.getSharpness(image,1)
        statistics['sharpnessB'] = self.getSharpness(image,2)
        statistics['coVarianceRR']=self.getCovariance(image,0,0)
        statistics['coVarianceRG']=self.getCovariance(image,0,1)
        statistics['coVarianceRB']=self.getCovariance(image,0,2)
        statistics['coVarianceGR']=self.getCovariance(image,1,0)
        statistics['coVarianceGG']=self.getCovariance(image,1,1)
        statistics['coVarianceGB']=self.getCovariance(image,1,2)
        statistics['coVarianceBR']=self.getCovariance(image,2,0)
        statistics['coVarianceBG']=self.getCovariance(image,2,1)
        statistics['coVarianceBB']=self.getCovariance(image,2,2)

        return statistics


    def getSharpness(self,image,index):
        page=image[:,:,index]
        gy, gx = np.gradient(page)
        gnorm = np.sqrt(gx ** 2 + gy ** 2)
        sharpness = np.average(gnorm)
        return sharpness

    def getMean(self,image,index):
        page=image[:,:,index]
        return np.mean(np.mean(page))

    def getStandardDeviation(self,image,index):
        page=image[:,:,index]
        page=page.flatten()
        return np.std(page)

    def getCovariance(self,image,index1,index2):
        page1=image[:,:,index1].flatten()
        page2 = image[:, :, index2].flatten()
        return np.cov(page1,page2)

statistics=dict()
for fileName in glob.glob('data/users/mpmay/acquisition/1296Images/images/*.jpg'):
    splitnames=fileName.split('_')
    index=splitnames[1].split('.')
    index=int(index[0])
    image=Image.open(fileName)
    image=np.array(image).astype('int32')
    statisticsCalculator=ImageSummaryStatistics()
    statistics[index]=statisticsCalculator.calculate(image)
    statistics[index]['id']=index
    statistics[index]['xy']=None
    statistics[index]['distanceFromOrigin']=None

indexMapXY=dict()
index=0
for x in np.arange(-1800.,1800.,100):
    for y in np.arange(-1800.,1800.,100):
        statistics[index]['xPosition']=x
        statistics[index]['yPosition']=y
        statistics[index]['distanceFromOrigin']=(x**2+y**2)**(0.5)
        index=index+1

with open('data/users/mpmay/imageSummaryStatistics.pkl', 'wb') as f:
    pickle.dump(statistics,f)

with open('data/users/mpmay/imageSummaryStatistics.pkl', 'rb') as f:
    loadedStatistics=pickle.load(f)
