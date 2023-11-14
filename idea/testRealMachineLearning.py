import tifffile
from image_process import CellDetectorCellMask
import  matplotlib.pyplot as plt
from distributed import Client
import numpy as np
im=tifffile.imread('data/analysis/TimBrianSearchPart1/exampleMileStone1_Part1_NDTiffStack.tif')
#im=tifffile.imread('data/analysis/APD_9x9/exampleMileStone1_Part1_9x9/exampleMileStone1_Part1_NDTiffStack.tif')
#im=tifffile.imread('data/analysis/FindNumCellsSlide2/findNumCells_Part1_1/findNumCells_Part1_NDTiffStack.tif')
#im=tifffile.imread('data/analysis/FindNumCellsSlide3/findNumCells_Part1_1/findNumCells_Part1_NDTiffStack.tif')
meanIntensities=[]
for i in range(im.shape[0]):
    meanIntensity=np.mean(im[i,:,:])
    meanIntensities.append(meanIntensity)
print(meanIntensities)
print(im.shape)

detector=CellDetectorCellMask(diameter=300,MINIMUM_CELL_AREA=5000)
numCells=[]
for i in range(im.shape[0]):
    mask=detector.process(im[i,:,:])
    numCells.append(np.max(mask))
print(numCells)
