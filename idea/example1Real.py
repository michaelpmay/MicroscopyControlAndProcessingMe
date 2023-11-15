from source.apd import *
from source.image_emulator import ImageEmulator2Channel
from source.distributed_computing import DistributedComputeDaskTask

##### THIS IS A CODE FOR Acquisring a set of images with XY
## SETTINGS TO CHANGE ALL THE TIME
apdSystem=APDSystem(rootDataFolder=os.path.join(''),configFileName='TSLAB_DEVICE_CONFIG.cfg',user='default')
##### Acquisition Settings #####
numROIXYSteps=4
xROIRange=imagePixSizeXY = [-512*numROIXYSteps, 512*numROIXYSteps]
yROIRange=[-512*numROIXYSteps, 512*numROIXYSteps]
xyROIOrigin=[0,0]
zRange=None # None or list of [zstart,zend,zstep]
timeRange=None # None or list of [TimeBetweenSeconds, numberOfTimePoints]
channelRange=None # None or list of [channelName,channelItemsList,channelExposureTimesList]
##### Emulation Settings #####
emulator=ImageEmulator2Channel()
emulator.loadImageFilePath('data/core/cell_library')
emulator.setXYImageSize([512,512])
emulator.setAlpha([0.,0.,0.])
numCellsSimulated=50
emulator.simulatePositions([512*5,512*5], numCellsSimulated)

## SETTINGS TO CHANGE SOMETIMES
### Local or Remote Distributed Computing
compute=DistributedComputeLocal()
#compute=DistributedComputeDaskTask('localhost:8765')


## SETTINGS TO CHANGE RARELY
ROIImSize=[512,512]
numROIXYSteps=4
imagePixSizeXY = [512*numROIXYSteps, 512*numROIXYSteps]
numCellsSimulated = numROIXYSteps*numROIXYSteps*2


emulator=ImageEmulator2Channel()
emulator.loadImageFilePath('data/core/cell_library')
emulator.setXYImageSize(ROIImSize)
emulator.setAlpha([0.,0.,0.])
emulator.simulatePositions(imagePixSizeXY, numCellsSimulated)

# [1] Adjust Acquisitision Settings
lib=AcquisitionPluginLibrary()
acquisition=lib.xyLooseGrid(xROIRange,yROIRange,xyROIOrigin,channelRange=None,laserIntensities=None,zRange=None,timeRange=None, emulator=None)

# [2] Adjust Process Settings
process=PostProcessor(computer=compute)
process.add('fovMeanIntensity')
process.add('cellDetectNumCellsInRoi')
process.add('cellDetectSpotLocationsInRoi')

#process.add('fishPipeline')
# [3] Adjust Decision Settings
decision=DecisionNull()
apdSystem.linkAPD(acquisition,process,decision)
apdSystem.run()
