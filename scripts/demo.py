from apd import *
apdSystem = APDSystem(configFileName='TSLAB_DEVICE_CONFIG.cfg',  #
                    rootDataFolder='') #local
lib = AcquisitionPluginLibrary()

# acquisition=lib.xySequence([[0,0]]) # list of list of xy pairs [0,0] single xy image on stage at origin
#
# data=apdSystem.acquire(acquisition) # command to acquire list of points


acquisition=lib.xySequence([[0,0],[1,1],[2,2]],timeRange=[2,1]) # list of list of xy pairs [0,0] single xy image on stage at origin
data=apdSystem.acquire(acquisition) # command to acquire list of points
print(data.get_index_keys())

acquisition=lib.xyLooseGrid([-1,1],[-1,1],[0,0],timeRange=[2,1])
data=apdSystem.acquire(acquisition)
print(data.get_index_keys())

acquisition=lib.xyzSequence([[0,0,0],[1,1,1],[2,2,2]],timeRange=[2,1])
data=apdSystem.acquire(acquisition)
print(data.get_index_keys())


