import time

import numpy as np
import scipy.interpolate
from environment import *
from scipy import signal
from pycromanager import Acquisition, Bridge, multi_d_acquisition_events, Core
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
env.loadConfiguration(configFileName='TSLAB_DEVICE_CONFIG.cfg')
env.backend.clearCache()
env.backend.clearAllStagedAcquisitions()

env.backend.devices.addDevice('TSLabGalvo', 'COM19')
env.backend.connectDevices()

env.backend.devices['Galvo']

Galvo = env.backend.devices['Galvo'][0]

env.backend.calibration.getCalibration('View','Galvo',1,60)
#XAR = [0,1000]
#YAR = [0,1000]
XAR = [30,35,35,30,30]
YAR = [35,35,30,30,35]
for i in range(50):
    for j in range(len(XAR)-1):
        Galvo.cut([XAR[j], YAR[j]], [XAR[j+1], YAR[j+1]], 1)
        time.sleep(.01)