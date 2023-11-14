import numpy as np
# User Settings
ImageDims=[64,64]  # xy step sizes for tiling
origin=[0,0] # position of xy when running this code
magnification=60 # ID for which turret is used to save as metadata
binning=1 # ID for callibration.
#nRangex=[-3,-2,-1,0,1,2,3] #  Range for x stepping
#nRangey=[-3,-2,-1,0,1,2,3] #  Range for y stepping
nRangex=[0] #  Range for xy stepping
nRangey=[0] #  Range for xy stepping
laserIntensities = [2., 14., 50.] # violet,
laserPwerMtpl = np.linspace(0.25,2.,8)
channels = ['Red', 'Green', 'Blue']
exposureTimes = [53.64, 53.64, 53.64]
zlims = None  # [zmin, zmax]
zstep = 4. # step size in z
timeStep = 0.
nTimeFrames = 1

# Do not change below here
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
builder.setRootDataPath('\\\\munsky-nas.engr.colostate.edu\\share\\Users\\Brian') #sets the root folder for the held data use windows to mount the Z drive with nas!
#builder.setRootDataPath('') #current directory

builder.setAuthentication('local') # local, or NoPassword
env=builder.getEnvironment()
env.backend.setUser('Brian','')
env.loadConfiguration(configFileName='TSLAB_DEVICE_CONFIG.cfg')
env.backend.clearCache()
env.backend.clearAllStagedAcquisitions()

# settings for devices
print(env.backend.devices.listDevicesAvailable())

# settings for geometry and positioning
xRange = np.array(nRangex)*ImageDims[0]+origin[0]
yRange = np.array(nRangey)*ImageDims[1]+origin[1]
viewSequence=[]
for x in xRange:
    for y in yRange:
        viewSequence.append([x,y])
calibration=env.backend.calibration.getCalibration('View', 'Stage', binning, magnification)
stageSequence=calibration.mapList(viewSequence)

for k in range(len(laserPwerMtpl)):
    localLaserIntens = laserPwerMtpl[k]*np.array(laserIntensities)
    # Laser Power
    from devices import Serial
    for i in range(len(laserIntensities)):
        env.backend.devices['Laser'][i].serial = Serial(env.backend.devices['Laser'][i].serial.port, isDummy=0)
        env.backend.devices['Laser'][i].open()
        env.backend.devices['Laser'][i].setLaserPowerInWatts(localLaserIntens[i])
        env.backend.devices['Laser'][i].close()

    env.backend.loadAcquisition('default')  # Load a template
    env.backend.acquisition.events.num_time_points = nTimeFrames
    env.backend.acquisition.events.time_interval_s = timeStep
    env.backend.acquisition.events.xy_positions=stageSequence
    env.backend.acquisition.events.channel_group='Filter'
    env.backend.acquisition.events.channels=channels
    #env.backend.acquisition.hooks.hookPostCamera.input={'channelMap':['Red','Green','Violet']}
    env.backend.acquisition.events.channel_exposures_ms=exposureTimes
    if zlims:
        env.backend.acquisition.events.z_start = zlims[0]
        env.backend.acquisition.events.z_end = zlims[1]
        env.backend.acquisition.events.z_step = zstep
    else:
        env.backend.acquisition.events.z_start=None
        env.backend.acquisition.events.z_end=None
        env.backend.acquisition.events.z_step=None

    env.backend.acquisition.settings.snap_images=False
    env.backend.scheduleCurrentAcquisitionAs('sharpnesscan3color_scheduled.acq')
    env.backend.tryCompleteAllStagedAcquisitions()