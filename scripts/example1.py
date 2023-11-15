from source.apd import *
from source.image_emulator import ImageEmulator2Channel
from source.distributed_computing import DistributedComputeDaskTask
apdSystem=APDSystem(rootDataFolder=os.path.join(''),configFileName='myConfig.cfg',user='default')

# IMage Settings to Acquire a grid of images
numROIXYSteps=4
xROIRange=[0,1,2]*512
yROIRange=[0,1,2]*512
xyROIOrigin=[0,0]
ROIImSize=[512,512]

# Settings for Image Emulation
emulator=ImageEmulator2Channel()
emulator.setXYImageSize(ROIImSize)
numCellsSimulated=50
canvasSizeXY=[512*numROIXYSteps,512*numROIXYSteps]
emulator.simulatePositions(canvasSizeXY,numCellsSimulated)

compute=DistributedComputeLocal()

lib=AcquisitionPluginLibrary()
acquisition=lib.xyLooseGrid(xROIRange,yROIRange,xyROIOrigin,
                            channelRange=None,
                            laserIntensities=None,
                            zRange=None,
                            timeRange=None,
                            emulator=emulator)

process=PostProcessor(computer=compute)
process.add('fovMeanIntensity')
process.add('cellDetectNumCellsInRoi',model_type='cyto')
process.add('cellDetectSpotLocationsInRoi')
#process.add('fishPipeline')

decision=DecisionNull()
apdSystem.linkAPD(acquisition,process,decision)
apdSystem.run()
