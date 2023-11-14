import numpy as np
import scipy.interpolate
from environment import *
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


ImageDims=[512-20,512-20]
origin=[0,0]
magnification=60
binning=2
nRange=[-5,-4,-3,-2,-1,0,1,2,3,4,5]
xRange = np.array(nRange)*ImageDims[0]+origin[0]
yRange = np.array(nRange)*ImageDims[1]+origin[1]
viewSequence=[]
for x in xRange:
    for y in yRange:
        viewSequence.append([x,y])
calibration=env.backend.calibration.getCalibration('View', 'Stage', binning, magnification)
stageSequence=calibration.mapList(viewSequence)

env.backend.loadAcquisition('sharpnesscan4color')
env.backend.acquisition.events.xy_positions=stageSequence
env.backend.acquisition.events.channel_group='Filter'
env.backend.acquisition.events.channels=['Violet','Red','Green','Blue']
env.backend.acquisition.events.channel_exposures_ms=[200.,200.,200.,200.]
env.backend.acquisition.events.z_start=-13*2.
env.backend.acquisition.events.z_end=13*2.
env.backend.acquisition.events.z_step=4.
env.backend.acquisition.settings.snap_images=False
env.backend.scheduleCurrentAcquisitionAs('sharpnesscan4color_scheduled.acq')
env.backend.tryCompleteAllStagedAcquisitions()
output=env.backend.loadOutput('sharpnesscan4color_scheduled.acq')
time.sleep(1)
end1 = time.time()- start
print(end1)
maxSharpnessPosition=output['maxSharpnessPosition']
xPoints=[]
yPoints=[]
zPoints=[]
for i in range(len(maxSharpnessPosition)):
    xPoints.append(maxSharpnessPosition[i][0])
    yPoints.append(maxSharpnessPosition[i][1])
    zPoints.append(maxSharpnessPosition[i][2])

zPoints = np.linspace(-15, 15, 2*13+1)
f=scipy.interpolate.interp2d(xPoints,yPoints,zPoints)
sequence=[]
for i in range(len(xRange)):
    for j in range(len(yRange)):
        for k in range(len(zPoints)):
            position=[xPoints[i],yPoints[j],f(xPoints[i],yPoints[j])[0]+zPoints[k]]
            sequence.append(position)

env.backend.loadAcquisition('default')
env.backend.acquisition.settings.name='Slide34LindaGoodBox_200MS'
env.backend.acquisition.settings.show_display=True
env.backend.acquisition.events.xy_positions=None
env.backend.acquisition.events.xyz_positions=sequence
env.backend.acquisition.events.num_time_points=1
env.backend.acquisition.events.time_interval_s=1.
env.backend.acquisition.events.z_start=None
env.backend.acquisition.events.z_end=None
env.backend.acquisition.events.z_step=None
env.backend.acquisition.events.channel_group='Filter'
env.backend.acquisition.events.channels=['Violet','Red','Green','Blue']
env.backend.acquisition.events.channel_exposures_ms=[200.,200.,200.,200.]
env.backend.acquisition.events.order='tpcz'


env.backend.loadAcquisition('default')
env.backend.acquisition.settings.name='Slide34LindaGoodBox_100MS'
env.backend.acquisition.settings.show_display=True
env.backend.acquisition.events.xy_positions=None
env.backend.acquisition.events.xyz_positions=sequence
env.backend.acquisition.events.num_time_points=1
env.backend.acquisition.events.time_interval_s=1.
env.backend.acquisition.events.z_start=None
env.backend.acquisition.events.z_end=None
env.backend.acquisition.events.z_step=None
env.backend.acquisition.events.channel_group='Filter'
env.backend.acquisition.events.channels=['Violet','Red','Green','Blue']
env.backend.acquisition.events.channel_exposures_ms=[100.,100.,100.,100.]
env.backend.acquisition.events.order='tpcz'