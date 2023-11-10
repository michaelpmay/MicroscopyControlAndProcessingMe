from environment import *
builder=EnvironmentBuilder()
builder.setInterface('headless') #headless or gui
builder.setDataManager('local') #local or remote
env=builder.getEnvironment()
env.addDevice('TSLabArduino','test')
env.addDevice('LaserDevice_Coherent','test')#488
env.addDevice('LaserDevice_Coherent','test')#561
env.addDevice('LaserDevice_Coherent','test')#637
env.addDevice('LaserDevice_','test')#405 Galvo
env.open()
env.devices.devices['Laser'][0].reset()
env.devices.devices['Laser'][1].reset()
env.devices.devices['Laser'][2].reset()

env.devices.devices['Laser'][0].setPowerInWatts(.1)
env.devices.devices['Laser'][1].setPowerInWatts(.1)
env.devices.devices['Laser'][2].setPowerInWatts(.1)

events = a.EventsTicket()
events.num_time_points = 2
events.time_interval_s = 0.001
events.z_start = 0.
events.z_end = 1.
events.z_step = 0.5
events.channel_group = 'Channel'
events.channels = ['488', '561', '637']
events.channel_exposures_ms = [10., 10., 10., 10., ]
events.xy_positions = [[0, 0], [0, 1]]
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
acquisition.directory = env.globals.DATA_FOLDER
acquisition.name = 'test'
acquisition.image_process_fn = image_process_fn
acquisition.event_generation_hook_fn = None
acquisition.pre_hardware_hook_fn = pre_hardware_hook_fn
acquisition.post_hardware_hook_fn = post_hardware_hook_fn
acquisition.post_camera_hook_fn = post_camera_hook_fn
acquisition.show_display = False
acquisition.image_saved_fn = None
acquisition.process = False  # multiprocessing on or off (only works on linux)
acquisition.saving_queue_size = 20
acquisition.bridge_timeout = 500

acquisition.debug = False
acquisition.core_log_debug = False
acquisition.port = 4827

env.mediateAcquisition(events,acquisition)