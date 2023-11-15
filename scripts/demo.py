from source.apd import *
from source.image_emulator import TestImageEmulator, ImageEmulator2Channel,ImageEmulatorWrapper
from source.calibration import  MatrixCalibration

## Terminator Scope Config with remote NAS
apdSystem = APDSystem(configFileName='myConfig.cfg',  #
                    rootDataFolder='') #local
lib = AcquisitionPluginLibrary()
acquisition = lib.xyLooseGrid([1, 1], [-1, 1], [0, 0], zRange=[-0.5,0.5,0.5])
apdSystem.acquire(acquisition)
