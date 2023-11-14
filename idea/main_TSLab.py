from source.environment import *
builder=EnvironmentBuilder()
builder.setInterface('headless') #headless or gui
#before you go here mount the samba share and point to 'Z:\\Users\\Michael'
builder.setRootDataPath('Z:\\Users\\Michael') #sets the root folder for the held data use windows to mount the Z drive with nas!
#builder.setRootDataPath('') #current directory
builder.setAuthentication('local') # local, or NoPassword
env=builder.getEnvironment()
env.backend.loadConfiguration('TSLAB_DEVICE_CONFIG.cfg')
env.backend.setUser('mpmay','twinky1994')
env.backend.stageAcquisition('go_home.acq')
env.backend.tryCompleteAllStagedAcquisitions()
env.backend.stageAcquisition('zplane_TSLAB.acq')
env.backend.tryCompleteAllStagedAcquisitions()
env.backend.stageAcquisition('celldetection_TSLAB.acq')
env.backend.tryCompleteAllStagedAcquisitions()