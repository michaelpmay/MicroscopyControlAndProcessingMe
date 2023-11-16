from source.apd import *
from source.image_emulator import TestImageEmulator, ImageEmulator2Channel,ImageEmulatorWrapper
from source.calibration import  MatrixCalibration

## Terminator Scope Config with remote NAS
apdSystem = APDSystem(configFileName='myConfig.cfg',  #
                    rootDataFolder='') #local
lib = AcquisitionPluginLibrary()
acquisition = lib.xyLooseGrid([0], [0], [0, 0])
dataset=apdSystem.acquire(acquisition)
acquisition = lib.xyLooseGrid([0,1], [0,1], [0, 0])
dataset=apdSystem.acquire(acquisition)
acquisition = lib.xyLooseGrid([0,1], [0,1], [0, 0],zRange=[-1,1,.5])
dataset=apdSystem.acquire(acquisition)
acquisition = lib.xyLooseGrid([0], [0], [0, 0],zRange=[-1,1,.5],timeRange=[0,1])
dataset=apdSystem.acquire(acquisition)
acquisition = lib.xyLooseGrid([0], [0], [0, 0],zRange=[-1,1,.5],timeRange=[0,1],channelRange=['Channel',['DAPI','Cy5'],[100,100]])
dataset=apdSystem.acquire(acquisition)
1+12