from environment import *
from scipy import signal
from pycromanager import Acquisition, Bridge, multi_d_acquisition_events, Core
core = Core()
builder=EnvironmentBuilder()
builder.setInterface('headless') #headless or gui
#before you go here mount the samba share and point to 'Z:\\Users\\Michael'
# connect to \\munsky-nas.engr.colostate.edu\share and map as Z drive  before running this line
builder.setRootDataPath('\\\\munsky-nas.engr.colostate.edu\\share\\Users\\Michael') #sets the root folder for the held data use windows to mount the Z drive with nas!
#builder.setRootDataPath('') #current directory
builder.setAuthentication('local') # local, or NoPassword
env=builder.getEnvironment()
env.backend.setUser('mpmay','twinky1994')
env.loadConfiguration()
env.backend.clearCache()
viewSequence=[]
N=1
xRange=[80/N,0]
yRange=[0,80/N]
for x in xRange:
    for y in yRange:
        viewSequence.append([x,y])
calibration=env.backend.calibration.getCalibration('View', 'Stage', N , 60)
stageSequence=[]
for s in viewSequence:
    stageSequence.append(calibration.map(s))

print(stageSequence)
env.backend.clearAllStagedAcquisitions()
env.backend.addDevice('TSLabGalvo','COM19')
env.backend.loadAcquisition('default')
env.backend.acquisition.settings.name='verifyStage'
env.backend.acquisition.settings.show_display=True
env.backend.acquisition.events.xy_positions=stageSequence
env.backend.acquisition.events.xyz_positions=None
env.backend.acquisition.events.num_time_points=1
env.backend.acquisition.events.time_interval_s=1.
env.backend.acquisition.events.z_start=None
env.backend.acquisition.events.z_end=None
env.backend.acquisition.events.z_step=None
env.backend.acquisition.events.channel_group=None
env.backend.acquisition.events.channels=None
env.backend.acquisition.events.channel_exposures_ms=None
env.backend.acquisition.events.order='tpcz'
time.sleep(1.)
env.backend.acquire()
time.sleep(1.)