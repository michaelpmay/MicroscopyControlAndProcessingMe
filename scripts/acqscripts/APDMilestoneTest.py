import matplotlib.pyplot as plt

from apd import *
from image_emulator import TestImageEmulator, ImageEmulator2Channel,ImageEmulatorWrapper
apd=APDSystem()
lib=APDFunctionLibrary()
numROIXYSteps=3
imagePixSizeXY = [512*numROIXYSteps, 512*numROIXYSteps]
numCellsSimulated = numROIXYSteps*numROIXYSteps*2
ROIImSize=[512,512]
emulator=ImageEmulator2Channel()
image_folder = 'data/core/cell_library'
emulator.loadImageFilePath(image_folder)
emulator.setXYImageSize(ROIImSize)
emulator.setAlpha([-1.,.001,-.002])
emulator.simulatePositions(imagePixSizeXY, numCellsSimulated)
#emulator=ImageEmulatorWrapper(system=emulator,isCached=False)
#emulator.tryLoadCache()
xROIRange=range(numROIXYSteps-1)
yROIRange=range(numROIXYSteps-1)
xyROIOrigin=[0,0]
apdFunction=lib.findCellsInGrid(xROIRange,yROIRange,xyROIOrigin,ROIImSize,channels=['Channel',['Cy5', 'DAPI'],[100.,100.]],
laserIntensityRGBV=[6.,1.,5.,0.],zRange=[-3,3,1],timeRange=None,emulator=emulator,split_roi=True)
apd.run(apdFunction)
#emulator.saveCache()