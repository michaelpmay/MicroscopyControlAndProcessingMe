from environment import *
import time
import numpy as np
builder=EnvironmentBuilder()
builder.setInterface('headless') #headless or gui
builder.setDataManager('local') #local or remote
builder.setUser('mpmay')# change username here
env=builder.getEnvironment()
env.addDevice('LaserDevice_Coherent','COM21')
env.addDevice('LaserDevice_Coherent','COM22')
env.addDevice('LaserDevice_Coherent','COM23')
#env.addDevice('TSLabArduino','COM20')

response=env.helper()

if response=='acquire':
    env.connectDevices()
    env.devices.devices['Laser'][0].setLaserState(1)
    env.devices.devices['Laser'][1].setLaserState(1)
    env.devices.devices['Laser'][2].setLaserState(1)

time.sleep(1)



xyPositions=[]
for x in np.arange(-1800., 1800., 100):
    for y in np.arange(-1800., 1800., 100):
        xyPositions.append((x,y))

events = a.EventsTicket()
events.num_time_points = 1
events.time_interval_s = 1.
events.z_start = None
events.z_end =  None
events.z_step = None
events.channel_group = 'Filter'
events.channels = ['Red','Green','Blue']
events.channel_exposures_ms = [300., 300., 300.]
events.xy_positions = xyPositions
events.xyz_positions = None
events.order = 'tpcz'
events.keep_shutter_open_between_z_steps = False
events.keep_shutter_open_between_channels = False

def image_process_fn(image, metadata):
    env
    return image, metadata

def pre_hardware_hook_fn(event, bridge, stack):
    return event

def post_hardware_hook_fn(event, bridge, stack):
    return event

def post_camera_hook_fn(event, bridge, stack):
    return event

def event_generation_hook_fn(event, bridge, stack):
    pass

acquisition = a.AcquisitionTicket()
acquisition.directory = 'data/users/mpmay'
acquisition.name = '36PowGrid'
acquisition.image_process_fn = None
acquisition.event_generation_hook_fn = None
acquisition.pre_hardware_hook_fn = None
acquisition.post_hardware_hook_fn = None
acquisition.post_camera_hook_fn = None
acquisition.show_display = False
acquisition.image_saved_fn = None
acquisition.process = False  # multiprocessing on or off (only works on linux)
acquisition.saving_queue_size = 20
acquisition.bridge_timeout = 500

acquisition.debug = False
acquisition.core_log_debug = False
acquisition.port = 4827

env.mediateAcquisition(events,acquisition)