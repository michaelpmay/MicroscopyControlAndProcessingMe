import time

import matplotlib.pyplot as plt
from apd import *
from image_emulator import TestImageEmulator, ImageEmulator2Channel,ImageEmulatorWrapper
from distributed_computing import DistributedComputeDaskTask
from calibration import MatrixCalibration
apd=APDSystem(configFileName='TSLAB_DEVICE_CONFIG.cfg')
lib=APDFunctionLibrary()
numROIXYSteps=8+1 #(number of roi+1)
ROIImSize=[512,512]
xROIRange=range(numROIXYSteps-1)
yROIRange=range(numROIXYSteps-1)
xyROIOrigin=[0,0]

#compute=DistributedComputeDaskTask('129.19.63.116:8786') # this setting is multitreaded on a remote machine
#intsall dask on a remote machine and run "dash scheduler" in one window and "dask worker IPHOST:8786" in the other
compute=DistributedComputeLocal() # this setting the worst case scenario
#compute=DistributedComputeDaskTask('localhost:8786') #this setting is multithreadeing localy

ViewToStageXYROICalibrator=MatrixCalibration()
ViewToStageXYROICalibrator.setMatrix([[.06*2000,0],[0,.06*2000]])
ViewToStageXYROICalibrator.setZero([0,0])
currentTime=time.time()

#apdFunction=lib.findNumCells(xROIRange,yROIRange,xyROIOrigin,ROIImSize,channels=['Filter',['Red', 'Green'],[100.,100.]],
#laserIntensityRGBV=None,zRange=None,timeRange=None,emulator=None,compute=compute,model_type='cyto',calibration=ViewToStageXYROICalibrator,show_display=False)
#apd.run(apdFunction)

maxNumCells=100
apdFunction=lib.findNPunctaInGridNoZ(xROIRange,yROIRange,xyROIOrigin,channels=['Filter',['Green', 'Blue'],[100.,100.]],
laserIntensityRGBV=None,zRange=[-3.,3.,.5],timeRange=None,emulator=None,compute=compute,threshold=0,calibration=ViewToStageXYROICalibrator,show_display=False,split_roi=False)
apd.run(apdFunction)
print(time.time()-currentTime)
