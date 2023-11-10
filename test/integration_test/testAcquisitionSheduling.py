import time

from environment import *
builder=EnvironmentBuilder()
builder.setInterface('headless') #headless or gui
#before you go here mount the samba share and point to 'Z:\\Users\\Michael'
#builder.setRootDataPath('Z:\\Users\\Michael') #sets the root folder for the held data use windows to mount the Z drive with nas!
builder.setRootDataPath('') #current directory
builder.setAuthentication('local') # local, or NoPassword
env=builder.getEnvironment()
env.backend.setUser('default','')
env.backend.stageAcquisition('zplane')
#env.backend.stageAcquisition('verbose')
#env.backend.stageAcquisition('default')
#env.backend.acquisition.hooks.hookPreHardware({},None,None)
#env.backend.acquisition.hooks.hookPostHardware({},None,None)
#env.backend.acquisition.hooks.hookPostCamera({},None,None)
#env.backend.acquisition.hooks.hookPostHardware({},None,None)
env.backend.tryCompleteAllStagedAcquisitions()
1+1