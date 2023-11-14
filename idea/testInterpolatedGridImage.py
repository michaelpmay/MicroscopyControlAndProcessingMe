import numpy as np
import scipy.interpolate
from environment import *
from scipy import signal
from pycromanager import Acquisition, Bridge, multi_d_acquisition_events, Core
core = Core()
builder=EnvironmentBuilder()
builder.setInterface('headless') #headless or gui
#before you go here mount the samba share and point to 'Z:\\Users\\Michael'
builder.setRootDataPath('Z:\\Users\\Michael') #sets the root folder for the held data use windows to mount the Z drive with nas!
#builder.setRootDataPath('') #current directory
builder.setAuthentication('local') # local, or NoPassword
env=builder.getEnvironment()
env.backend.setUser('mpmay','twinky1994')
env.loadConfiguration()
env.backend.clearCache()
bridge = Bridge()
mmc = Core()
#mmStudio = bridge.get_studio()
z_stage = mmc.get_focus_device()
mmc.set_property(z_stage, "Use Sequence", "No")

env.backend.loadAcquisition('default')
env.backend.acquisition.hooks.hookImageProcess=None
env.backend.acquisition.settings.show_display=True
env.backend.acquisition.events.xy_positions=None
env.backend.acquisition.events.num_time_points=100
env.backend.acquisition.events.time_interval_s=60.
env.backend.acquisition.events.channel_group='Filter'
env.backend.acquisition.events.channels=['Red', 'Green', 'Blue']
env.backend.acquisition.events.channel_exposures_ms=[60.,60.,60.]
env.backend.acquisition.events.z_start = -3
env.backend.acquisition.events.z_end = 3
env.backend.acquisition.events.z_step = .5
env.backend.acquisition.events.order='tpzc'
env.backend.acquire()