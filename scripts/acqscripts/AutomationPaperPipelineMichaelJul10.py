import numpy as np
from environment import *
from hooks import HookSet, AcquisitionHooks
from PIL import Image
from image_emulator import ImageEmulatorFromArray
from image_process import CellDetectorCellMask
from decision import DecisionPickROIFromMask,DecisionSelectOptimalZPlaneFromSharpness,DecisionSelectOptimalZPlaneFromEstimator
from utility import ZPlaneEstimator
from postprocessors import PostProcessor
builder=EnvironmentBuilder()
builder.setInterface('headless') #headless or gui
#before you go here mount the samba share and point to 'Z:\\Users\\Michael'
# connect to \\munsky-nas.engr.colostate.edu\share and map as Z drive  before running this line
#builder.setRootDataPath('Z:\\Users\\Michael') #sets the root folder for the held data use windows to mount the Z drive with nas!
builder.setRootDataPath('') #current directory
builder.setAuthentication('local') # local, or NoPassword
env=builder.getEnvironment()
env.backend.setUser('mpmay','twinky1994')
env.loadConfiguration(configFileName='myConfig.cfg')
env.backend.clearCache()
env.backend.clearAllStagedAcquisitions()

image=np.array(Image.open('data/test/testimage.jpg'))
#emulator=ImageEmulatorFromSimulation() # todo
emulator=ImageEmulatorFromArray()
emulator.setImageFromArray(image[:,:,0])
emulator.isGaussianZImageDistort=True

#PART1 OF PAPER: FIND FOV FROM CELLPOSE ROI DETECTOR
# Acquire
env.backend.loadAcquisition('image_emulator',emulator)
dataset=env.backend.acquireAndReturnDataset()

# Process
processor=PostProcessor(data=dataset,acq=env.backend.acquisition)
processor.add('cell_detect_num_cells_in_roi')
processed_data=processor.get()

# Decide
decision=DecisionPickROIFromMask()
decision.numCellsThreshold=1
decision.detector.default_flow_threshold=.1
decision.detector.MINIMUM_CELL_AREA = 30

#PART2 OF PAPER: Image ZStack each ROI
# Acquire
env.backend.acquisition=decision.propose(processed_data,env.backend.acquisition)
env.backend.acquisition.events.z_start=-5
env.backend.acquisition.events.z_end=5
env.backend.acquisition.events.z_step=1
dataset=env.backend.acquireAndReturnDataset()
# Process
processor=PostProcessor(data=dataset,acq=env.backend.acquisition)
processor.add('sharpness')
processor.add('sharpestz')
processed_data=processor.get()
# Decide

#PART3 OF PAPER ESTIMATE ZPLANE(alpha1,alpha2,alpha3)
zEstimator=ZPlaneEstimator()
zEstimator.fitAlphaFromDataset(processed_data)

decision=DecisionSelectOptimalZPlaneFromEstimator(zEstimator)
env.backend.acquisition=decision.propose(processed_data,env.backend.acquisition)
#env.backend.acquireAndReturnDataset()

#Part4 OF PAPER:
dataset=env.backend.acquireAndReturnDataset()

