from environment import *
from image_emulator import ImageEmulatorFromArray
from PIL import Image
import numpy as np
builder=EnvironmentBuilder()
builder.setInterface('headless') #headless or gui
#before you go here mount the samba share and point to 'Z:\\Users\\Michael'
# connect to \\munsky-nas.engr.colostate.edu\share and map as Z drive  before running this line
#builder.setRootDataPath('Z:\\Users\\Michael') #sets the root folder for the held data use windows to mount the Z drive with nas!
#builder.setRootDataPath('\\\\munsky-nas.engr.colostate.edu\\share\\Users\\Michael') #sets the root folder for the held data use windows to mount the Z drive with nas!
builder.setRootDataPath('') #current directory
builder.setAuthentication('local') # local, or NoPassword
env=builder.getEnvironment()
env.backend.setUser('mpmay','twinky1994')
env.loadConfiguration(configFileName='myConfig.cfg')
env.backend.clearCache()
env.backend.clearAllStagedAcquisitions()


image=np.array(Image.open('data/test/testimage.jpg'))
emulator=ImageEmulatorFromArray()
emulator.setImageFromArray(image)
emulator.isGaussianZImageDistort=True

#env.backend.loadAcquisition('image_emulator',emulator)
env.backend.loadAcquisition('default')

def hookPostHardware(event,bridge):
    return event

env.backend.acquisition.hooks.hookImageProcess=None
env.backend.acquisition.hooks.hookEventGeneration=None
env.backend.acquisition.hooks.hookPreHardware=None
env.backend.acquisition.hooks.hookPostHardware=hookPostHardware
env.backend.acquisition.hooks.hookPostCamera=None

env.backend.acquire()