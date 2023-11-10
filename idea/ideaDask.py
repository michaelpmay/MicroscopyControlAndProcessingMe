from dask.distributed import Client,LocalCluster,wait
from distributed_computing import Task, DistributedComputeDaskTask
import tifffile
from image_process import CellDetectorCellMask, SpotCountLocationsDoughnut
import numpy as np
from cellpose import models
''' 
run dask schedule 
run dask worker 8786
'''
images=tifffile.imread('data/analysis/TimBrianSearchPart1/exampleMileStone1_Part1_NDTiffStack.tif')
images=tifffile.imread('data/analysis/FindNumCellsSlide2/findNumCells_Part1_1/findNumCells_Part1_NDTiffStack.tif')
print(images.shape)
import time
client=Client('129.82.94.141:8786')
client.upload_file('distributed_computing.py')
client.upload_file('image_process.py')

#currentTime=time.time()
#for i in range(81):
#    print(i)
#    processImage(image)
#elapsedTime = time.time() - currentTime
#print(elapsedTime)

def processTheImage(detector,image):
    currentTime=time.time()
    detector.process(image)
    elapsedTime = time.time() - currentTime
    return np.random.rand()

detector=CellDetectorCellMask()
detectors=[]
for i in range(len(images)):
    detectors.append(detector)


currentTime=time.time()
A=client.map(processTheImage,detectors,images)
output=client.gather(A)
print(output)
delayTime=time.time()-currentTime
print('totalTime={0}'.format(delayTime))
print('totalTimePer={0}'.format(delayTime/len(images.shape[0])))
