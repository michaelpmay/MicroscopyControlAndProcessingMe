from source.apd import *
from source.image_emulator import TestImageEmulator, ImageEmulator2Channel,ImageEmulatorWrapper
from source.calibration import  MatrixCalibration

## Terminator Scope Config with remote NAS
apdSystem=APDSystem(configFileName='myConfig.cfg',rootDataFolder='') #local

## Change FOV Settings here
numROIXYSteps=4
imagePixSizeXY = [512*numROIXYSteps, 512*numROIXYSteps]
numCellsSimulated = numROIXYSteps*numROIXYSteps*2
ROIImSize=[512,512]

## change Calibration settings
calibration=MatrixCalibration()
calibration.setMatrix([[512,0],[0,512]])
calibration.setZero([0,0])

xROIRange=range(numROIXYSteps-1)
yROIRange=range(numROIXYSteps-1)
xyROIOrigin=[0,0]


lib=AcquisitionPluginLibrary()
acquisition=lib.xyLooseGrid([1,1],[-1,1],[0,0])

apdSystem.acquire(acquisition)
