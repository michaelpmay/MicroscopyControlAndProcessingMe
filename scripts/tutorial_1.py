from apd import *
1+1
apdSystem = APDSystem(configFileName='myConfig.cfg',  #
                    rootDataFolder='') #local
lib = AcquisitionPluginLibrary()
acquisition = lib.xySequence([[0,0]])
dataset=apdSystem.acquire(acquisition)