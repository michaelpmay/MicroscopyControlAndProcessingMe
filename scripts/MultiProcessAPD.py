import time

import matplotlib.pyplot as plt
from apd import *
from image_emulator import TestImageEmulator, ImageEmulator2Channel,ImageEmulatorWrapper
from distributed_computing import DistributedComputeDaskTask
from calibration import MatrixCalibration
apd=APDSystem()
lib=APDFunctionLibrary()
numROIXYSteps=3 #(number of roi+1)
imagePixSizeXY = [512*numROIXYSteps, 512*numROIXYSteps]
numCellsSimulated = numROIXYSteps*numROIXYSteps*2
ROIImSize=[512,512]
emulator=ImageEmulator2Channel()
image_folder = 'data/core/cell_library'
emulator.loadImageFilePath(image_folder)
emulator.setXYImageSize(ROIImSize)
emulator.setAlpha([-1.,.001,-.002])
currentTime=time.time()
emulator.simulatePositions(imagePixSizeXY, numCellsSimulated)
print(time.time()-currentTime)
#emulator=ImageEmulatorWrapper(system=emulator,isCached=False)
#emulator.tryLoadCache()
xROIRange=range(numROIXYSteps-1)
yROIRange=range(numROIXYSteps-1)
xyROIOrigin=[0,0]

#compute=DistributedComputeDaskTask('129.19.46.78:8786') # this setting is multitreaded on a remote machine
#intsall dask on a remote machine and run "dash scheduler" in one window and "dask worker IPHOST:8786" in the other
compute=DistributedComputeLocal() # this setting the worst case scenario
#compute=DistributedComputeDaskTask('localhost:8786') #this setting is multithreadeing localy

ViewToStageXYCalibrator=MatrixCalibration()
ViewToStageXYCalibrator.setMatrix([[512,0],[0,512]])
ViewToStageXYCalibrator.setZero([0,0])

apdFunction=lib.findCellsInGrid(xROIRange,yROIRange,xyROIOrigin,ROIImSize,channels=['Channel',['Cy5', 'DAPI'],[100.,100.]],
laserIntensityRGBV=[6.,1.,5.,0.],zRange=[-7,7,1],timeRange=None,emulator=emulator,compute=compute,model_type='nuclei',calibration=ViewToStageXYCalibrator,split_roi=True)


apd.run(apdFunction)
#emulator.saveCache()