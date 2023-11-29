from apd import *
from image_emulator import ImageEmulator2Channel
apdSystem = APDSystem(configFileName='myConfig.cfg', rootDataFolder='') #local
lib = AcquisitionPluginLibrary()

emulator=ImageEmulator2Channel()
emulator.simulatePositions([1000,1000],10)

acquisition = lib.xySequence([[0,0]])
dataset=apdSystem.acquire(acquisition)

acquisition = lib.xyzSequence([[0,0,0]])
dataset=apdSystem.acquire(acquisition)