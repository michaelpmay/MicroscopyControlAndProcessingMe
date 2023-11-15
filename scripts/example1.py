from source.apd import *
from image_emulator import ImageEmulator2Channel
from source.distributed_computing import DistributedComputeDaskTask
apdSystem=APDSystem(rootDataFolder=os.path.join(''),configFileName='myConfig.cfg',user='default')

## SETTINGS TO CHANGE ALL THE TIME

##### Acquisition Settings #####
xROIRange=[0,512,1024]
yROIRange=[0,512,1024]
xyROIOrigin=[0,0]
zRange=None
timeRange=None
channelRange=None
##### Emulation Settings #####
emulator=None
## SETTINGS TO SHAVE SOMETIMES
compute=DistributedComputeLocal()
#compute=DistributedComputeDaskTask('localhost:8765')

## SETTINGS TO CHANGE RARELY
ROIImSize=[512,512]

## Change FOV Settings here


## Change Image Emulation settings here


## DONT TOUCH ANYTHING BBACK HERE OR IT ALL DIES
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
acquisition=lib.xyLooseGrid(xROIRange,yROIRange,xyROIOrigin,channelRange=['Channel',['Cy5', 'DAPI'],[100.,100.]],laserIntensities=None,zRange=zRange,timeRange=timeRange, emulator=None)
acquisition=lib.xyLooseGrid(xROIRange,yROIRange,xyROIOrigin,channelRange=None,laserIntensities=None,zRange=None,timeRange=None, emulator=emulator)
# [2] Adjust Process Settings
process=PostProcessor(computer=compute)
process.add('fovMeanIntensity')
process.add('cellDetectNumCellsInRoi')
process.add('cellDetectSpotLocationsInRoi')
process.add('fishPipeline')
# [3] Adjust Decision Settings
decision=DecisionNull()
apdSystem.linkAPD(acquisition,process,decision)
apdSystem.run()
