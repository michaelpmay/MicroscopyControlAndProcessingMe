import time
import numpy as np
import scipy.interpolate
from environment import *
from scipy import signal
from pycromanager import Acquisition, multi_d_acquisition_events, Core
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
start = time.time()


ImageDims=[1024*2,1024*2]
ImageDims=[0,0]
origin=[-8221.67,20926.17]
magnification=60
binning=1
nRange=[0]
xRange = np.array(nRange)*ImageDims[0]+origin[0]
yRange = np.array(nRange)*ImageDims[1]+origin[1]
xRange=[origin[0]]
yRange=[origin[1]]
viewSequence=[]
for x in xRange:
    for y in yRange:
        viewSequence.append([x,y])
calibration=env.backend.calibration.getCalibration('View', 'Stage', binning, magnification)
stageSequence=calibration.mapList(viewSequence)

env.backend.loadAcquisition('default')
env.backend.acquisition.events.xy_positions=stageSequence
env.backend.acquisition.events.channel_group='Filter'
env.backend.acquisition.events.channels=['Red','Green','Blue']
#env.backend.acquisition.hooks.hookPostCamera.input={'channelMap':['Red','Green','Violet']}
env.backend.acquisition.events.channel_exposures_ms=[50.,50.,50.]
env.backend.acquisition.events.z_start=-10*4.
env.backend.acquisition.events.z_end=10*4.
env.backend.acquisition.events.z_step=4.
env.backend.acquisition.settings.snap_images=False
env.backend.scheduleCurrentAcquisitionAs('sharpnesscan3color_scheduled.acq')
env.backend.tryCompleteAllStagedAcquisitions()
output=env.backend.loadOutput('sharpnesscan3color_scheduled.acq')
time.sleep(1)
end1 = time.time()- start
print(end1)
maxSharpnessPosition=output['maxSharpnessPosition']
zRange = np.linspace(-7*1, 7*1, 2*7+1)
sequence=[]
for i in range(len(maxSharpnessPosition)):
    for j in range(len(zRange)):
        sequence.append([maxSharpnessPosition[i][0],maxSharpnessPosition[i][1],maxSharpnessPosition[i][2]+zRange[j]])

env.backend.loadAcquisition('default')
env.backend.acquisition.settings.name='TEST'
env.backend.acquisition.settings.show_display=True
env.backend.acquisition.events.xy_positions=None
env.backend.acquisition.events.xyz_positions=sequence
env.backend.acquisition.events.num_time_points=1
env.backend.acquisition.events.time_interval_s=0
env.backend.acquisition.events.z_start=None
env.backend.acquisition.events.z_end=None
env.backend.acquisition.events.z_step=None
env.backend.acquisition.events.channel_group='Filter'
env.backend.acquisition.events.channels=['Red','Green','Blue']
env.backend.acquisition.events.channel_exposures_ms=[300.,100.,120.]
env.backend.acquisition.events.order='tpcz'
env.backend.acquire()
'''
env.backend.loadAcquisition('default')
env.backend.acquisition.settings.name='TEST1'
env.backend.acquisition.settings.show_display=True
env.backend.acquisition.events.xy_positions=None
env.backend.acquisition.events.xyz_positions=sequence
env.backend.acquisition.events.num_time_points=1
env.backend.acquisition.events.time_interval_s=0
env.backend.acquisition.events.z_start=None
env.backend.acquisition.events.z_end=None
env.backend.acquisition.events.z_step=None
env.backend.acquisition.events.channel_group='Filter'
env.backend.acquisition.events.channels=['Red','Green','Violet']
env.backend.acquisition.events.channel_exposures_ms=[200.,100.,120.]
env.backend.acquisition.events.order='tpcz'
env.backend.acquire()

input("DROP INTENSITY BY 25%")

env.backend.loadAcquisition('default')
env.backend.acquisition.settings.name='TEST2'
env.backend.acquisition.settings.show_display=True
env.backend.acquisition.events.xy_positions=None
env.backend.acquisition.events.xyz_positions=sequence
env.backend.acquisition.events.num_time_points=1
env.backend.acquisition.events.time_interval_s=0
env.backend.acquisition.events.z_start=None
env.backend.acquisition.events.z_end=None
env.backend.acquisition.events.z_step=None
env.backend.acquisition.events.channel_group='Filter'
env.backend.acquisition.events.channels=['Red','Green','Violet']
env.backend.acquisition.events.channel_exposures_ms=[300.,100.,120.]
env.backend.acquisition.events.order='tpcz'
env.backend.acquire()

env.backend.loadAcquisition('default')
env.backend.acquisition.settings.name='TEST3'
env.backend.acquisition.settings.show_display=True
env.backend.acquisition.events.xy_positions=None
env.backend.acquisition.events.xyz_positions=sequence
env.backend.acquisition.events.num_time_points=1
env.backend.acquisition.events.time_interval_s=0
env.backend.acquisition.events.z_start=None
env.backend.acquisition.events.z_end=None
env.backend.acquisition.events.z_step=None
env.backend.acquisition.events.channel_group='Filter'
env.backend.acquisition.events.channels=['Red','Green','Violet']
env.backend.acquisition.events.channel_exposures_ms=[200.,100.,120.]
env.backend.acquisition.events.order='tpcz'
env.backend.acquire()

input("DONT HIT ENTER UNTIL THE LASER INTENSITY IS to origional!!!!!!!!!")

env.backend.loadAcquisition('default')
env.backend.acquisition.settings.name='TEST4'
env.backend.acquisition.settings.show_display=True
env.backend.acquisition.events.xy_positions=None
env.backend.acquisition.events.xyz_positions=sequence
env.backend.acquisition.events.num_time_points=1
env.backend.acquisition.events.time_interval_s=0
env.backend.acquisition.events.z_start=None
env.backend.acquisition.events.z_end=None
env.backend.acquisition.events.z_step=None
env.backend.acquisition.events.channel_group='Filter'
env.backend.acquisition.events.channels=['Red','Green','Violet']
env.backend.acquisition.events.channel_exposures_ms=[300.,100.,120.]
env.backend.acquisition.events.order='tpcz'
env.backend.acquire()
'''