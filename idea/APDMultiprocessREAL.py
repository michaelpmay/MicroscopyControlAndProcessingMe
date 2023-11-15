import time

import matplotlib.pyplot as plt
from source.apd import *
from source.image_emulator import TestImageEmulator, ImageEmulator2Channel,ImageEmulatorWrapper
from source.distributed_computing import DistributedComputeDaskTask
from source.calibration import MatrixCalibration
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

maxNumCells=100
apdFunction=lib.findNCellsInGridNoZ(xROIRange,yROIRange,xyROIOrigin,channels=['Filter',['Green', 'Blue'],[100.,100.]],
laserIntensityRGBV=None,zRange=[-3.,3.,.5],timeRange=None,emulator=None,compute=compute,calibration=ViewToStageXYROICalibrator,show_display=False,split_roi=False)
apd.runFunction(apdFunction)
print(time.time()-currentTime)
