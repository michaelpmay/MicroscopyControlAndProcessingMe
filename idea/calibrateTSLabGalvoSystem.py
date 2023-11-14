import time
import numpy as np
import scipy.interpolate
from environment import *
from calibration import *
from scipy import signal
from pycromanager import Acquisition, Bridge, multi_d_acquisition_events, Core
builder=EnvironmentBuilder()
builder.setInterface('headless') #headless or gui
#before you go here mount the samba share and point to 'Z:\\Users\\Michael'
# connect to \\munsky-nas.engr.colostate.edu\share and map as Z drive  before running this line
#builder.setRootDataPath('\\\\munsky-nas.engr.colostate.edu\\share\\Users\\Michael') #sets the root folder for the held data use windows to mount the Z drive with nas!
builder.setRootDataPath('') #current directory
builder.setAuthentication('local') # local, or NoPassword
env=builder.getEnvironment()
env.backend.setUser('mpmay','twinky1994')
env.backend.calibration.setCalibration('View','Galvo',2,60)
env.loadConfiguration()
env.backend.clearCache()
env.backend.clearAllStagedAcquisitions()
#env.backend.addDevice('TSLabGalvo','COM19')
