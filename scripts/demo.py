from source.apd import *
apdSystem = APDSystem(configFileName='myConfig.cfg',  #
                    rootDataFolder='') #local
lib = AcquisitionPluginLibrary()
acquisition = lib.xyLooseGrid([0], [0], [0, 0])
dataset=apdSystem.acquire(acquisition)