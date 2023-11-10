import time
import numpy as np
import scipy.interpolate
from environment import *
from scipy import signal
from pycromanager import Acquisition, Bridge, multi_d_acquisition_events, Core
from acquisition import AcquisitionBuilder, AcquisitionHookLibrary
from devices import Serial
from acquisition import AcquisitionPluginLibrary

#User Settings
rootDataPath = '\\\\munsky-nas.engr.colostate.edu\\share\\TermData'
# connect to \\munsky-nas.engr.colostate.edu\share and map as Z drive  before running this line
userName = 'Brian'
userPwd = ''
saveName = 'SH_ER_DUSP1_Test_021023'

#General Settings
showDisplayOption = True  # Show images as we take them or just save them to file?

#z-position determination scan settings
colors_zPosCalibration = ['Red']
xyValues_zPosnCalibration = [[0,0],[0,1000],[0,2000],[1000,2000],[1000,1000],[1000,0],[2000,0],[2000,1000],[2000,2000]]
exposureTimes_zPosnCalibration = [100]

# FOV Scan Settings
stepSize = 80
rangeX = range(0,stepSize*2+1,stepSize)
rangeY = range(0,stepSize*2+1,stepSize)
zRange = [0]  # position of z-stacks relative to the center plane
#zRange = np.linspace(-11*1/2., 11*1/2., 2*11+1)  # position of z-stacks relative to the center plane
exposureTimes_FOVs = [300,100,0] #[637nm, 561nm, 488nm]
colors = ['Red','Green','Blue'] #opposite order with previous and next lines??
laserIntensities = [1., 5., 20.] # [488nm, 561nm, 637nm]

# Laser Settings sweep
# laserPwerMtpl = np.linspace(0.25,2.,8)

#*******************************************************
# Common Settings (Do not edit anything in this section)
#*******************************************************
#Environment Builder (Do not edit anything here)
builder=EnvironmentBuilder()
builder.setInterface('headless') #headless or gui
builder.setRootDataPath(rootDataPath) #sets the root folder for the held data use windows to mount the Z drive with nas!
builder.setAuthentication('local') # local, or NoPassword
env=builder.getEnvironment()
env.backend.setUser(userName,userPwd)
env.loadConfiguration(configFileName='TSLAB_DEVICE_CONFIG.cfg')
env.backend.clearCache()
env.backend.clearAllStagedAcquisitions()


#*******************************************************
#Program 1 - Run z-sweep at specified z-step at list of specified xy-points in single color
# Build the events
lib = AcquisitionPluginLibrary()
plugin = lib.get('zPosnCalibration')
plugin.events.xy_positions = xyValues_zPosnCalibration
plugin.settings.name = saveName  # if None will not save anything
plugin.settings.show_display = showDisplayOption

# set laser intensities
for i in range(len(laserIntensities)):
    env.backend.devices['Laser'][i].serial = Serial(env.backend.devices['Laser'][i].serial.port, isDummy=0)
    env.backend.devices['Laser'][i].open()
    env.backend.devices['Laser'][i].setLaserPowerInWatts(laserIntensities[i])
    env.backend.devices['Laser'][i].close()

env.backend.acquisition = plugin
env.backend.scheduleCurrentAcquisitionAs('sharpnesscan1color_scheduled.acq')
env.backend.tryCompleteAllStagedAcquisitions()

input('Press enter to continue when imaging is complete.')
# TODO - need to add a wait function - for now, we will ask the user to hit return when ready.
output = env.backend.acquisition.output

# Wait until complete and then print results of calibration.
print(output['maxSharpness'])
print(output['maxSharpnessPosition'])

# Compute a regression map to find z(x,y) = [1 x y]*M
QQ = np.array(output['maxSharpnessPosition'])
A = np.ones((9,3))
A[:,1:3] = QQ[:,0:2]
B = QQ[:,2]
M = np.linalg.pinv(A)@B

print ('M = ')
print(M)
#*******************************************************
#Program 2 - Sweep over range of laser intensities at text-file provided list of x,y,z points in two colors
xyzValues_FOVs =[]
for x in rangeX:
    for y in rangeY:
        for j in range(len(zRange)):
            z = [1, x, y]@M  # Calcuate z- position for middle of stack
            print(z)
            if abs(z)<=12:
                xyzValues_FOVs.append([x, y, z+zRange[j]])

print(xyzValues_FOVs)

input('Press enter to continue if happy with positions.')
# TODO - need to add a wait function - for now, we will ask the user to hit return when ready.

xyzValues_FOVs =[]
for x in rangeX:
    for y in rangeY:
        for j in range(len(zRange)):
            z = 1.0  # Calcuate z- position for middle of stack
            if abs(z)<=8:
                xyzValues_FOVs.append([x, y, z+zRange[j]])

#for k in range(len(laserPwerMtpl)):
#    localLaserIntens = laserPwerMtpl[k]*np.array(laserIntensities)
# Laser Power
from devices import Serial
for i in range(len(laserIntensities)):
    env.backend.devices['Laser'][i].serial = Serial(env.backend.devices['Laser'][i].serial.port, isDummy=0)
    env.backend.devices['Laser'][i].open()
    env.backend.devices['Laser'][i].setLaserPowerInWatts(laserIntensities[i])
    env.backend.devices['Laser'][i].close()

lib = AcquisitionPluginLibrary()
plugin = lib.get('fovScan')
plugin.events.xy_positions = None
plugin.events.xyz_positions = xyzValues_FOVs
plugin.settings.name = saveName  # if None will not save anything
plugin.settings.show_display = showDisplayOption
plugin.events.channel_exposures_ms = exposureTimes_FOVs

env.backend.acquisition = plugin
env.backend.scheduleCurrentAcquisitionAs('FOV_scan.acq')
env.backend.tryCompleteAllStagedAcquisitions()




