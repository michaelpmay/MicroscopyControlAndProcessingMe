import time

import numpy as np
import scipy.interpolate
from environment import *
from scipy import signal

builder=EnvironmentBuilder()
builder.setInterface('headless') #headless or gui
#before you go here mount the samba share and point to 'Z:\\Users\\Michael'
# connect to \\munsky-nas.engr.colostate.edu\share and map as Z drive  before running this line
#builder.setRootDataPath('Z:\\Users\\Michael') #sets the root folder for the held data use windows to mount the Z drive with nas!
#builder.setRootDataPath('\\\\munsky-nas.engr.colostate.edu\\share\\Users\\Michael') #sets the root folder for the held data use windows to mount the Z drive with nas!
builder.setRootDataPath('') #current directory
builder.setAuthentication('local') # local, or NoPassword
env=builder.getEnvironment()
env.backend.setUser('default','')
env.loadConfiguration()
env.backend.clearCache()
env.backend.clearAllStagedAcquisitions()

sequence=[[0,0],[1000,1000],[0,0],[1000,1000],[0,0]]

env.backend.loadAcquisition('default')
env.backend.acquisition.settings.name='TestBackFourthLoosest'
env.backend.acquisition.settings.show_display=True
env.backend.acquisition.events.xy_positions=sequence
env.backend.acquisition.events.xyz_positions=None
env.backend.acquisition.events.num_time_points=1
env.backend.acquisition.events.time_interval_s=1.
env.backend.acquisition.events.z_start=None
env.backend.acquisition.events.z_end=None
env.backend.acquisition.events.z_step=None
env.backend.acquisition.events.channel_group='Filter'
env.backend.acquisition.events.channels=['Green']
env.backend.acquisition.events.channel_exposures_ms=[200.]
env.backend.acquisition.events.order='tpcz'
env.backend.acquire()