from source.image_process import SpotCountLocationsDoughnut,CellDetectorCellMask,SpotCountCellFrequency
import tifffile
from skimage import io
import matplotlib.pyplot as plt
import numpy as np
#images=io.imread('data/analysis/PunctaScan/findNumCells_Part1_1/findNumCells_Part1_NDTiffStack.tif')

#images=io.imread('data/analysis/FindNumCellsSlide2/findNumCells_Part1_1/findNumCells_Part1_NDTiffStack.tif')
#images=io.imread('data/analysis/FindNumCellsSlide3/findNumCells_Part1_1/findNumCells_Part1_NDTiffStack.tif')
#images=io.imread('data/analysis/FindCells9x9/exampleMileStone1_Part1_NDTiffStack.tif')

images=io.imread('data/analysis/PunctaSearch/firstSearch/exampleMileStone1_Part1_NDTiffStack.tif')
#images=io.imread('data/analysis/PunctaScan/findNumCells_Part1_1/findNumCells_Part1_NDTiffStack.tif')
#images=io.imread('data/analysis/renameof9by9_part1_bcause_pycharm_bad.tif')
print(images.shape)
punctaDetector=SpotCountLocationsDoughnut()
detector=CellDetectorCellMask(diameter=250)
spotAttributer=SpotCountCellFrequency()
spotAttributer.spotCounter=SpotCountLocationsDoughnut()
spotAttributer.cellDetector=CellDetectorCellMask(diameter=250)
spotsdetected=[]
thresholds=[]
numCells=[]
meanIntesnity=[]
punctaCount=[]
frequencies=[]
thresholdsValues=[1000]
for k in range(len(thresholdsValues)):
    punctaCount=[]
    for i in range(0,64):
        #plt.imshow(images[i,:,:])

        puncta = punctaDetector.process(images[i, :, :], sig=[2,7], threshold=thresholdsValues[k])
        punctaCount.append(len(puncta[0]['threshholds']))
        #frequencies.extend(spotAttributer.process(images[i, :, :], sig=[2,8],threshold=300))


        #masks=detector.process(images[i,:,:])
        #print(np.max(masks))
        #numCells.append(np.max(masks))

        #meanIntesnity.append(np.mean(images[i,:,:]))
    print(punctaCount)
    TrueCount=[0, 0, 1, 1, 1, 1, 2, 1, 2, 1, 0, 0, 2, 0, 0, 2, 1, 1, 1, 2, 0, 1, 1, 2, 0, 0, 0, 0, 1, 1, 0,
     0, 1, 3, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 2, 0, 0, 1, 1, 0, 0, 0, 1, 2, 2,
     1, 1]
    print(TrueCount)
    error=0
    for j in range(len(TrueCount)):
        error=error+np.sqrt(np.abs(punctaCount[j]-TrueCount[j]))
    print(error)
print(spotsdetected)
print(thresholds)
print(numCells)
print(meanIntesnity)
print(punctaCount)
print(frequencies)
print(len(frequencies))
