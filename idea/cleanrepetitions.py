from environment import *
from image_process import CentroidDetector
import numpy as np
import scipy.interpolate
builder=EnvironmentBuilder()
builder.setInterface('headless') #headless or gui
#before you go here mount the samba share and point to 'Z:\\Users\\Michael'
# connect to \\munsky-nas.engr.colostate.edu\share and map as Z drive  before running this line
#builder.setRootDataPath('Z:\\Users\\Michael') #sets the root folder for the held data use windows to mount the Z drive with nas!
builder.setRootDataPath('\\\\munsky-nas.engr.colostate.edu\\share\\Users\\Michael') #sets the root folder for the held data use windows to mount the Z drive with nas!
#builder.setRootDataPath('') #current directory
builder.setAuthentication('local') # local, or NoPassword
env=builder.getEnvironment()
env.backend.setUser('mpmay','twinky1994')
env.loadConfiguration()
env.backend.clearCache()
env.backend.clearAllStagedAcquisitions()

stageSequence=[[0,0],[0,1]]
builder=a.AcquisitionBuilder()
builder.addTimedEvents(1,0.)
builder.addZEvents(-20,20,4)
builder.addXYSequence(stageSequence)
builder.addChannelEvents('Filter',['Violet','Green','Blue'],[50.,50.,50.])
builder.setEventsOrder('tpzc')
builder.setIsSeeding(True)
builder.setIsShowDisplay(False)
builder.setIsDebug(False)
builder.setIsCoreLogDebug(False)
builder.setPort(4827)
builder.setSavingQueueSize(100)
builder.setBridgeTimeoutMs(500)
hLib=a.AcquisitionHookLibrary()
hooks=hLib.get('seedeventssharpness3color',channelMap=['Violet','Green','Blue'])
builder.setHooks(hooks)
plugin=builder.getPlugin()
env.backend.acquisition=plugin
#env.backend.acquire()
print(env.backend.calibration.listCalibrations())
calibrator=env.backend.calibration.getCalibration('View','Galvo',1,60)
detector=CentroidDetector()
plugin.hooks.hookImageProcess.calibrator=calibrator
plugin.hooks.hookImageProcess.detector=detector

hooks=hLib.get('seeddirectedevolution',detector=detector,calibrator=calibrator)
builder.setHooks(hooks)
plugin=builder.getPlugin()
env.backend.acquisition=plugin
env.backend.acquire()