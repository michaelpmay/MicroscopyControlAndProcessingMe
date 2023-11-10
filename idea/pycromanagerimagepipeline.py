from image_process import *
from acquisition import *
from automation import *
from globals import *

g = Globals()
eventsMediator = MultiDEventsMediator()
eventsMediator.num_time_points = 2
eventsMediator.time_interval_s = 0.001
eventsMediator.z_start = 0.
eventsMediator.z_end = 1.
eventsMediator.z_step = 0.5
eventsMediator.channel_group = 'Channel'
eventsMediator.channels = ['Cy5', 'DAPI', 'FITC', 'Rhodamine']
eventsMediator.channel_exposures_ms = [10., 10., 10., 10., ]
eventsMediator.xy_positions = [[0, 0], [0, 1]]
eventsMediator.xyz_positions = None
eventsMediator.order = 'tpcz'
eventsMediator.keep_shutter_open_between_z_steps = False
eventsMediator.keep_shutter_open_between_channels = False
events = eventsMediator.generateEvents()

pipeline=PycromanagerImageProcessPipeline()
lib=MicroscopyImageProcessLibrary
pipeline.append(lib.add(4))
pipeline.append(lib.multiply(2))
image_process_fn=pipeline

def pre_hardware_hook_fn(event, bridge, stack):
    return event

def post_hardware_hook_fn(event, bridge, stack):
    return event

def post_camera_hook_fn(event, bridge, stack):
    return event

acquisitionMediator = AcquisitionMediator()
acquisitionMediator.directory = g.DATA_FOLDER
acquisitionMediator.name = 'test'
acquisitionMediator.image_process_fn = image_process_fn
acquisitionMediator.event_generation_hook_fn = None
acquisitionMediator.pre_hardware_hook_fn = pre_hardware_hook_fn
acquisitionMediator.post_hardware_hook_fn = post_hardware_hook_fn
acquisitionMediator.post_camera_hook_fn = post_camera_hook_fn
acquisitionMediator.show_display = False
acquisitionMediator.image_saved_fn = None
acquisitionMediator.process = False  # multiprocessing on or off (only works on linux)
acquisitionMediator.saving_queue_size = 20
acquisitionMediator.bridge_timeout = 500
acquisitionMediator.debug = False
acquisitionMediator.core_log_debug = False
acquisitionMediator.port = 4827

acquisitionMediator.acquire(events)
