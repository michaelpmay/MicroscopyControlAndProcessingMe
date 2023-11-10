from environment import *
from pycromanager import Bridge,Core
from processing_service import
builder=EnvironmentBuilder()
builder.setInterface('headless') #headless or gui
builder.setRootDataPath('') #sets the root folder for the held data use windows to mount the Z drive with nas!
builder.setAuthentication('local') # local, or NoPassword
env=builder.getEnvironment()
env.backend.setUser('mpmay','twinky1994')
env.loadConfiguration('myConfig.cfg')
env.backend.clearCache()
env.backend.clearAllStagedAcquisitions()

positions=[[0,0]]
z_range=[-1,1,0.5]# start end step
env.backend.stageAcquisition('default')
env.backend.tryCompleteAllStagedAcquisitions()

env.backend.stageAcquisition('image_process_service',service)
#env.backend.stageAcquisition('detect_cell','Filter',['Green'],[100])
#env.backend.tryCompleteAllStagedAcquisitions()
#env.backend.stageAcquisition('detect_cell',None,None,None)
#env.backend.tryCompleteAllStagedAcquisitions()