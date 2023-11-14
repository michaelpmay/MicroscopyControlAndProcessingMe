import time

import numpy as np
import scipy.interpolate
from environment import *
from scipy import signal

from hooks import HookSet
builder=EnvironmentBuilder()
builder.setInterface('headless') #headless or gui
#before you go here mount the samba share and point to 'Z:\\Users\\Michael'
# connect to \\munsky-nas.engr.colostate.edu\share and map as Z drive  before running this line
#builder.setRootDataPath('Z:\\Users\\Michael') #sets the root folder for the held data use windows to mount the Z drive with nas!
builder.setRootDataPath('') #current directory
builder.setAuthentication('local') # local, or NoPassword
env=builder.getEnvironment()
env.backend.setUser('mpmay','twinky1994')
env.loadConfiguration(configFileName='myConfig.cfg')
env.backend.clearCache()
env.backend.clearAllStagedAcquisitions()
env.backend.loadAcquisition('default')
env.backend.acquisition.settings.debug=True
#env.backend.acquisition.hooks=HookSet()
env.backend.acquire()