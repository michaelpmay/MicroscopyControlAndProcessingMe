import numpy as np
from pycromanager import *
from source.hooks import *
from source.calibration import NullCalibration
from source.devices import ExternalDeviceManager
class iEventsTicket:
    '''big object holds the parameters for building events'''
    pass

class iAcqusititionSettings:
    '''big object holds the parameters for setting up the acqusition'''
    pass

class iAcquisitionLibrary:
    '''A class that creates different acquisition plugins. Factory Design pattern'''
    pass

class EventsTicket:
    """a big glob of parameters to represent data needed for acquisition"""
    def __init__(self):
        self._num_time_points = 1
        self._time_interval_s = 0
        self._z_start = None
        self._z_end = None
        self._z_step = None
        self._channel_group = None
        self._channels = None
        self._channel_exposures_ms = None
        self._xy_positions = None
        self._xyz_positions = None
        self._order = 'tpzc'
        self._keep_shutter_open_between_channels = False
        self._keep_shutter_open_between_z_steps = False

    @property
    def num_time_points(self):
        return self._num_time_points

    @num_time_points.setter
    def num_time_points(self,value):
        if value == None:
            self._num_time_points = None
            return
        if not isinstance(value, int):
            raise TypeError
        if value<0:
            raise ValueError
        self._num_time_points=value

    @property
    def time_interval_s(self):
        return self._time_interval_s

    @time_interval_s.setter
    def time_interval_s(self, value):
        if value == None:
            self._time_interval_s = None
            return
        if not isinstance(value, (float, int)):
            raise TypeError
        self._time_interval_s = value

    @property
    def z_start(self):
        return self._z_start

    @z_start.setter
    def z_start(self, value):
        if value == None:
            self._z_start = None
            return
        if not isinstance(value, (float, int)):
            raise TypeError
        self._z_start = value

    @property
    def z_end(self):
        return self._z_end

    @z_end.setter
    def z_end(self, value):
        if value==None:
            self._z_end=None
            return
        if not isinstance(value, (float,int)):
            raise TypeError
        self._z_end = value

    @property
    def z_step(self):
        return self._z_step

    @z_step.setter
    def z_step(self, value):
        if value == None:
            self._z_step = None
            return
        if not isinstance(value, (float, int)):
            raise TypeError
        self._z_step = value

    @property
    def channel_group(self):
        return self._channel_group

    @channel_group.setter
    def channel_group(self, value):
        if value == None:
            self._channel_group = None
            return
        if not isinstance(value, str):
            raise TypeError
        self._channel_group = value

    @property
    def channels(self):
        return self._channels

    @channels.setter
    def channels(self, value):
        if value == None:
            self._channels = None
            return
        if not isinstance(value, list):
            raise TypeError
        self._channels = value

    @property
    def channel_exposures_ms(self):
        return self._channel_exposures_ms

    @channel_exposures_ms.setter
    def channel_exposures_ms(self, value):
        if value == None:
            self._channel_exposures_ms = None
            return
        if not isinstance(value, list):
            raise TypeError
        for i in range(len(value)):
            if not isinstance(value[i],(int,float)):
                raise TypeError
            if (value[i]<0):
                raise ValueError
        self._channel_exposures_ms = value

    @property
    def xy_positions(self):
        return self._xy_positions

    @xy_positions.setter
    def xy_positions(self, value):
        if value == None:
            self._xy_positions = None
            return
        if not isinstance(value, list):
            raise TypeError
        self._xy_positions = value

    @property
    def xyz_positions(self):
        return self._xyz_positions

    @xyz_positions.setter
    def xyz_positions(self, value):
        if value == None:
            self._xyz_positions = None
            return
        if not isinstance(value, list):
            raise TypeError
        self._xyz_positions = value

    @property
    def order(self):
        return self._order

    @order.setter
    def order(self,value):
        if not isinstance(value,str):
            raise TypeError
        if len(value)!=4:
            raise ValueError
        self._order=value

    @property
    def keep_shutter_open_between_channels(self):
        return self._keep_shutter_open_between_channels

    @keep_shutter_open_between_channels.setter
    def keep_shutter_open_between_channels(self,value):
        if not isinstance(value,bool):
            raise TypeError
        self._keep_shutter_open_between_channels=value

    @property
    def keep_shutter_open_between_z_steps(self):
        return self._keep_shutter_open_between_z_steps

    @keep_shutter_open_between_z_steps.setter
    def keep_shutter_open_between_z_steps(self, value):
        if not isinstance(value, bool):
            raise TypeError
        self._keep_shutter_open_between_z_steps = value

    @property
    def properties(self):
        props=dict()
        props["Event Time Points [integer]"]=self.num_time_points
        props["Time Interval [float seconds]"]=self.time_interval_s
        props["ZStack [Start,End,Step]"]=[self.z_start,self.z_end,self.z_step]
        props["Channel [GroupName,ChannelNames,ChannelExposuresMs]"]=[self._channel_group,self._channels,self._channel_exposures_ms]
        props["XY Positions [list]"]= self.xy_positions
        props["XYZ Positions [list]"] = self.xyz_positions
        props["Imaging Order [tpzc]"] = self.order
        props['Shutter Open Between Channels [True/False]']=self._keep_shutter_open_between_channels
        props['Shutter Open Between ZSteps [True/False]'] = self._keep_shutter_open_between_z_steps
        return props

    def load(self,properties):
        self.num_time_points=properties["Event Time Points [integer]"]
        self.time_interval_s =properties["Time Interval [float seconds]"]
        [self.z_start, self.z_end, self.z_step]=properties["ZStack [Start,End,Step]"]
        [self.channel_group, self.channels,self.channel_exposures_ms]=properties["Channel [GroupName,ChannelNames,ChannelExposuresMs]"]
        self.xy_positions=properties["XY Positions [list]"]
        self.xyz_positions=properties["XYZ Positions [list]"]
        self.order=properties["Imaging Order [tpzc]"]
        self.keep_shutter_open_between_channels=properties['Shutter Open Between Channels [True/False]']
        self.keep_shutter_open_between_z_steps=properties['Shutter Open Between ZSteps [True/False]']


class AcquisitionSettings:
    directory = None
    name = None
    image_process_fn = None
    event_generation_hook_fn = None
    pre_hardware_hook_fn = None
    post_hardware_hook_fn = None
    post_camera_hook_fn = None
    show_display = None
    image_saved_fn = None
    process = None
    saving_queue_size = None
    bridge_timeout = None
    debug = None
    core_log_debug = None
    port=None
    snap_images=None
    is_seeding=None
    def __init__(self):
        self.directory = None
        self.name = None
        self.image_process_fn = None
        self.event_generation_hook_fn = None
        self.pre_hardware_hook_fn = None
        self.post_hardware_hook_fn = None
        self.post_camera_hook_fn = None
        self.show_display = False
        self.image_saved_fn = None
        self.process = False
        self.saving_queue_size = None
        self.bridge_timeout = None
        self.debug = None
        self.core_log_debug = None
        self.port=4827
        self.snap_images=True
        self.is_seeding=False

    @property
    def properties(self):
        props=dict()
        props['Acquisition Directory [string]']=self.directory
        props['Acquisition Name [string]']=self.name
        props['Show Display [True/False]']=self.show_display
        props['Multi-Processing [True/False]']=self.process
        props['Save Buffer Size [int]']=self.saving_queue_size
        props['Pycro-Bridge Timeout [float]']=self.bridge_timeout
        props['Debug [True/False]']=self.debug
        props['Core Log Debug [True/False]']=self.core_log_debug
        props['Port [int]']=self.port
        props['Snap Image at Each Point [True/False]']=self.snap_images
        props['Seed Events [True/False]']=self.is_seeding
        return props

    def load(self,properties):
        self.directory=properties['Acquisition Directory [string]']
        self.name =properties['Acquisition Name [string]']
        self.show_display=properties['Show Display [True/False]']
        self.process=properties['Multi-Processing [True/False]']
        self.saving_queue_size=properties['Save Buffer Size [int]']
        self.bridge_timeout=properties['Pycro-Bridge Timeout [float]']
        self.debug=properties['Debug [True/False]']
        self.core_log_debug=properties['Core Log Debug [True/False]']
        self.port=properties['Port [int]']
        self.snap_images=properties['Snap Image at Each Point [True/False]']
        self.is_seeding=properties['Seed Events [True/False]']


class AcquisitionPlugin:
    events=None
    settings=None
    hooks=None
    def __init__(self):
        self.events=EventsTicket()
        self.settings=AcquisitionSettings()
        self.hooks=AcquisitionHooks()
        self.laserIntensities=None
    def run(self):
        events=self.getEvents()
        #print('Number of events in schedule:{0}'.format(len(events)))
        if not self.settings.is_seeding:
            with  Acquisition(directory=self.settings.directory,
                          name=self.settings.name,
                          image_process_fn=self.hooks.hookImageProcess,
                          #event_generation_hook_fn=self.hooks.hookEventGeneration,
                          pre_hardware_hook_fn=self.hooks.hookPreHardware,
                          post_hardware_hook_fn=self.hooks.hookPostHardware,
                          post_camera_hook_fn=self.hooks.hookPostCamera,
                          show_display=self.settings.show_display,
                          process=self.settings.process,
                          saving_queue_size=self.settings.saving_queue_size,
                          debug=self.settings.debug,
                          core_log_debug=self.settings.core_log_debug,
                          port=self.settings.port) as acq:
                acq.acquire(events)

        else:
            acq=Acquisition(directory=self.settings.directory,
                        name=self.settings.name,
                        image_process_fn=self.hooks.hookImageProcess,
                        #event_generation_hook_fn=self.hooks.hookEventGeneration,
                        pre_hardware_hook_fn=self.hooks.hookPreHardware,
                        post_hardware_hook_fn=self.hooks.hookPostHardware,
                        post_camera_hook_fn=self.hooks.hookPostCamera,
                        show_display=self.settings.show_display,
                        #image_saved_fn=self.hooks.hookImageSaved,
                        process=self.settings.process,
                        saving_queue_size=self.settings.saving_queue_size,
                        debug=self.settings.debug,
                        core_log_debug=self.settings.core_log_debug,
                        port=self.settings.port)
        self.setHardwareLaserIntensities()
        acq.acquire(events)
        dataset = acq.get_dataset()
        return dataset

    def getEvents(self):
        events= multi_d_acquisition_events(
            num_time_points=self.events.num_time_points,
            time_interval_s=self.events.time_interval_s,
            z_start=self.events.z_start,
            z_end=self.events.z_end,
            z_step=self.events.z_step,
            channel_group=self.events.channel_group,
            channels=self.events.channels,
            channel_exposures_ms=self.events.channel_exposures_ms,
            xy_positions=self.events.xy_positions,
            xyz_positions=self.events.xyz_positions,
            order=self.events.order,
            keep_shutter_open_between_channels=self.events.keep_shutter_open_between_channels,
            keep_shutter_open_between_z_steps=self.events.keep_shutter_open_between_z_steps)
        if self.settings.is_seeding:
            self.hooks.hookImageProcess.input['events']=events
            events=events[0]
        if self.settings.snap_images==False:
            for event in events:
                event.pop('axes')
        return events

    @property
    def properties(self):
        props=dict()
        props.update(self.settings.properties)
        props.update(self.events.properties)
        props.update(self.hooks.properties)
        return props

    def load(self,properties):
        self.events.load(properties)
        self.settings.load(properties)
        if 'Hooks Name' in properties:
            self.hooks = HookSet().load(properties)
        else:
            self.hooks = AcquisitionHooks().load(properties)

    @property
    def output(self):
        output=self.hooks.output
        return output

    def setHardwareLaserIntensities(self):
        if self.laserIntensities:
            dManager=ExternalDeviceManager()
            g=Globals()
            for i in range(self.laserIntensities):
                dManager.devices[g.KEY_DEVICE_LASERS][i].setLaserPowerInWatts(self.laserIntensities)


class AcquisitionBuilder:
    plugin=None
    def __init__(self):
        self.plugin=AcquisitionPlugin()

    def getPlugin(self):
        return self.plugin

    def addTimedEvents(self,num_time_points,time_interval_s):
        self.plugin.events.num_time_points=num_time_points
        self.plugin.events.time_interval_s=time_interval_s

    def addZEvents(self,zStart,zEnd,zStep):
        self.plugin.events.z_start = zStart
        self.plugin.events.z_end   = zEnd
        self.plugin.events.z_step  = zStep

    def addGridEvents(self,xRange,yRange):
        sequence=[]
        for x in xRange:
            for y in yRange:
                sequence.append((x,y))
        self.plugin.events.xy_positions = sequence

    def addXYSequence(self,sequence):
        self.plugin.events.xy_positions=sequence

    def addXYZSequence(self,sequence):
        self.plugin.events.xyz_positions=sequence

    def addChannelEvents(self,channelGroup,channels,exposureMs):
        self.plugin.events.channel_group=channelGroup
        self.plugin.events.channels=channels
        self.plugin.events.channel_exposures_ms=exposureMs

    def addLaserIntensities(self,laserIntensities):
        self.plugin.laserIntensities=laserIntensities

    def getEvents(self):
        return self.plugin.getEvents()

    def setSaveDirectory(self,directory):
        self.plugin.settings.directory=directory

    def setSaveName(self,name):
        self.plugin.settings.name=name

    def linkHooks(self,hooks,*args,**kwargs):
        if not isinstance(hooks,(str,HookSet)):
            raise TypeError
        if isinstance(hooks,str):
            lib=HookSetLibrary()
            hooks=lib.get(hooks,*args,**kwargs)
        self.plugin.hooks.link(hooks)

    def setHooks(self,hooks,*args,**kwargs):
        if not isinstance(hooks,(str,HookSet)):
            raise TypeError
        if isinstance(hooks,str):
            lib=HookSetLibrary()
            hooks=lib.get(hooks,*args,**kwargs)
        self.plugin.hooks=hooks

    def setIsMultiprocesing(self,boolean):
        if not isinstance(boolean,bool):
            raise TypeError
        self.plugin.settings.process=boolean

    def setSavingQueueSize(self,size):
        if not isinstance(size,int):
            raise TypeError
        if size<=0:
            raise TypeError
        self.plugin.settings.saving_queue_size=size

    def setBridgeTimeoutMs(self,timeout):
        if not isinstance(timeout,int):
            raise TypeError
        self.plugin.settings.bridge_timeout=timeout

    def setIsDebug(self,boolean):
        if not isinstance(boolean,bool):
            raise TypeError
        self.plugin.settings.debug=boolean

    def setIsCoreLogDebug(self,boolean):
        if not isinstance(boolean,bool):
            raise TypeError
        self.plugin.settings.core_log_debug=boolean

    def setPort(self,port):
        if not isinstance(port,int):
            raise TypeError
        if port<0:
            raise TypeError
        self.plugin.settings.port=port

    def setIsShowDisplay(self,boolean):
        if not isinstance(boolean,bool):
            raise TypeError
        self.plugin.settings.show_display=boolean

    def setIsShutterOpenBetweenChannels(self,boolean):
        if not isinstance(boolean,bool):
            raise TypeError
        self.plugin.events.keep_shutter_open_between_channels=boolean

    def setIsShutterOpenBetweenZSteps(self,boolean):
        if not isinstance(boolean,bool):
            raise TypeError
        self.plugin.events.keep_shutter_open_between_z_steps=boolean

    def setIsSnappingImages(self,boolean):
        if not isinstance(boolean,bool):
            raise TypeError
        self.plugin.settings.snap_images=boolean

    def setEventsOrder(self,string):
        self.plugin.events.order=string

    def setIsSeeding(self,boolean):
        if not isinstance(boolean,bool):
            raise TypeError
        self.plugin.settings.is_seeding=boolean


class AcquisitionPluginLibrary:
    def __init__(self):
        pass
    
    def get(self,key,*args,**kwargs):
        if not isinstance(key,str):
            raise TypeError("a string please")
        if key in ('get','list'):
            raise KeyError
        return eval("self."+key+"(*args,**kwargs)")
    
    def list(self):
        names=[]
        objectNames=dir(self)
        for name in objectNames:
            if name[0:2]!="__":
                if name not in ('get','list'):
                    names.append(name)
        return names
    
    def default(self):
        builder = AcquisitionBuilder()
        # Build the events
        builder.addTimedEvents(3, 0.)
        #builder.addZEvents(0., 1., .5)
        builder.addChannelEvents('Channel', ['Cy5', 'DAPI', 'FITC', 'Rhodamine'], [10., 10., 10., 10.])
        builder.addXYSequence([[0, 0],[0,1],[1,0],[1,1]])
        # builder.addXYZSequence([[0,0,0],[0,1,2]]) # CANT do XYZ if addXYSequence and addZEvents are used
        builder.setEventsOrder('tpzc')
        # build the hooks
        lib=HookSetLibrary()
        hooks=lib.get('default')
        builder.linkHooks(hooks)
        # build save location
        builder.setSaveDirectory(None)  # if None env will set as USER DEFAULT FOLDER
        builder.setSaveName('default')  # if None will not save anything

        # build settings
        builder.setIsShowDisplay(False)
        builder.setIsDebug(False)
        builder.setIsCoreLogDebug(False)
        builder.setIsMultiprocesing(False)  # linux only
        builder.setSavingQueueSize(50)
        builder.setBridgeTimeoutMs(500)
        builder.setPort(4827)
        builder.setIsSeeding(False)

        # get the result of the building
        plugin = builder.getPlugin()
        return plugin

    def detect_cell(self,channel,channelMap,channelExposure):
        builder = AcquisitionBuilder()
        # Build the events
        builder.addTimedEvents(3, 0.)
        builder.addChannelEvents(channel, channelMap, channelExposure)
        builder.addXYSequence([[0, 0]])
        # builder.addXYZSequence([[0,0,0],[0,1,2]]) # CANT do XYZ if addXYSequence and addZEvents are used
        builder.setEventsOrder('tpzc')
        # build the hooks
        lib=HookSetLibrary()
        hooks=lib.get('detect_cell')
        builder.linkHooks(hooks)
        # build save location
        builder.setSaveDirectory(None)  # if None env will set as USER DEFAULT FOLDER
        builder.setSaveName('detect_cell')  # if None will not save anything

        # build settings
        builder.setIsShowDisplay(True)
        builder.setIsDebug(False)
        builder.setIsCoreLogDebug(False)
        builder.setIsMultiprocesing(False)  # linux only
        builder.setSavingQueueSize(50)
        builder.setBridgeTimeoutMs(500)
        builder.setPort(4827)
        builder.setIsSeeding(False)

        # get the result of the building
        plugin = builder.getPlugin()
        return plugin

    def zPosnCalibration(self):
        builder = AcquisitionBuilder()
        builder.addZEvents(-12, 12, 1.0)  # - zmin, zmax, step
        builder.addChannelEvents('Filter', ['Red'], [100])  # -- filter chanels, exposure times
    #    builder.addChannelEvents('Filter', ['Red','Green','Blue'], [100,100,100])  # -- filter chanels, exposure times
        builder.setEventsOrder('tpzc')
        # build the hooks
        lib = HookSetLibrary()
        hooks = lib.get('seedeventssharpness1color')
        hooks.hookImageProcess.input['channelMap'] = ['Red']
        builder.linkHooks(hooks)
        # build save location
        builder.setSaveDirectory(None)  # if None env will set as USER DEFAULT FOLDER

        # build settings
        builder.setIsDebug(False)
        builder.setIsCoreLogDebug(False)
        builder.setIsMultiprocesing(False)  # linux only
        builder.setSavingQueueSize(50)
        builder.setBridgeTimeoutMs(500)
        builder.setPort(4827)
        builder.setIsSeeding(True)

        # get the result of the building
        plugin = builder.getPlugin()
        return plugin

    def fovScan(self):
        builder = AcquisitionBuilder()
        builder.addChannelEvents('Filter', ['Red','Green','Blue'], [100,100,100])  # -- filter chanels, exposure times
        builder.setEventsOrder('tpzc')
        # build the hooks
        lib = HookSetLibrary()
        # hooks = lib.get('default')
        hooks = lib.get('default')
        builder.linkHooks(hooks)
        # build save location
        builder.setSaveDirectory(None)  # if None env will set as USER DEFAULT FOLDER

        # build settings
        builder.setIsDebug(False)
        builder.setIsCoreLogDebug(False)
        builder.setIsMultiprocesing(False)  # linux only
        builder.setSavingQueueSize(50)
        builder.setBridgeTimeoutMs(500)
        builder.setPort(4827)
        builder.setIsSeeding(False)

        # get the result of the building
        plugin = builder.getPlugin()
        return plugin

    def seedevents(self):
        builder = AcquisitionBuilder()
        # Build the events
        builder.addTimedEvents(3, 0.)
        builder.addZEvents(0., 1., .5)
        #builder.addChannelEvents('Channel', ['Cy5', 'DAPI', 'FITC', 'Rhodamine'], [10., 10., 10., 10.])
        builder.addXYSequence([[0, 0], [0, 1]])
        # builder.addXYZSequence([[0,0,0],[0,1,2]]) # CANT do XYZ if addXYSequence and addZEvents are used
        builder.setEventsOrder('tpzc')
        # build the hooks
        lib=HookSetLibrary()
        hooks=lib.get('default')
        builder.linkHooks(hooks)
        # build save location
        builder.setSaveDirectory(None)  # if None env will set as USER DEFAULT FOLDER
        builder.setSaveName('seedevents')  # if None will not save anything

        # build settings
        builder.setIsShowDisplay(True)
        builder.setIsDebug(False)
        builder.setIsCoreLogDebug(False)
        builder.setIsMultiprocesing(False)  # linux only
        builder.setSavingQueueSize(50)
        builder.setBridgeTimeoutMs(500)
        builder.setPort(4827)
        builder.setIsSeeding(True)

        # get the result of the building
        plugin = builder.getPlugin()
        return plugin

    def verbose(self):
        builder=AcquisitionBuilder()
        builder.addTimedEvents(3, 0.)
        builder.addZEvents(0., 1., .5)
        #builder.addChannelEvents('Channel', ['Cy5', 'DAPI', 'FITC', 'Rhodamine'], [10., 10., 10., 10.])
        builder.addXYSequence([[0, 0], [0, 1]])
        # build save location
        builder.setSaveDirectory(None)  # if None env will set as USER DEFAULT FOLDER
        builder.setSaveName('verbose')  # if None will not save anything
        # get the hooks
        builder.setHooks('verbose')
        # build settings
        builder.setIsShowDisplay(False)
        builder.setIsDebug(False)
        builder.setIsCoreLogDebug(False)
        builder.setIsMultiprocesing(False)  # linux only
        builder.setSavingQueueSize(50)
        builder.setBridgeTimeoutMs(500)
        builder.setPort(4827)
        plugin=builder.getPlugin()
        return plugin

    def findzplane3color(self,positions,z_range,channel,channelMap,channelExposure):
        builder=AcquisitionBuilder()
        builder.setHooks('findzplane3color',channel,channelMap)
        builder.setSaveName('findzplane3color')
        builder.addChannelEvents(channel, channelMap, channelExposure)
        builder.addXYSequence(positions)
        builder.addZEvents(z_range[0], z_range[1], z_range[2])
        builder.setEventsOrder('tpzc')
        builder.setIsShowDisplay(False)
        builder.setIsDebug(False)
        builder.setIsCoreLogDebug(False)
        builder.setIsMultiprocesing(False)  # linux only
        builder.setSavingQueueSize(50)
        builder.setBridgeTimeoutMs(500)
        builder.setPort(4827)
        plugin=builder.getPlugin()
        return plugin

    def findzplane1color(self,positions,z_range,channel,channelMap,channelExposure):
        builder = AcquisitionBuilder()
        builder.setHooks('findzplane1color',channel,channelMap)
        builder.setSaveName('findzplane1color')
        builder.addChannelEvents(channel, channelMap,channelExposure)
        builder.addXYSequence(positions)
        builder.addZEvents(z_range[0], z_range[1], z_range[2])
        builder.setEventsOrder('tpzc')
        builder.setIsShowDisplay(False)
        builder.setIsDebug(False)
        builder.setIsCoreLogDebug(False)
        builder.setIsMultiprocesing(False)  # linux only
        builder.setSavingQueueSize(50)
        builder.setBridgeTimeoutMs(500)
        builder.setPort(4827)
        plugin = builder.getPlugin()
        return plugin

    def interpolatezplane(self,positions=[[-1000,-1000],[1000,-1000],[1000,1000],[-1000,1000]]):
        builder = AcquisitionBuilder()
        builder.setHooks('interpolatezplane')
        builder.addXYSequence(positions)
        builder.setEventsOrder('tpzc')
        builder.setIsShowDisplay(False)
        builder.setIsDebug(False)
        builder.setIsCoreLogDebug(False)
        builder.setIsMultiprocesing(False)  # linux only
        builder.setSavingQueueSize(50)
        builder.setBridgeTimeoutMs(500)
        builder.setPort(4827)
        plugin = builder.getPlugin()
        return plugin


    def celldetection(self):
        builder = AcquisitionBuilder()
        builder.addTimedEvents(1, 0.)
        # builder.addChannelEvents('Channel', ['Cy5', 'DAPI', 'FITC', 'Rhodamine'], [10., 10., 10., 10.])
        xRange=np.arange(-50,50.1,25)
        yRange=np.arange(-50,50.1,25)
        sequence=[]
        for i in range(len(xRange)):
            for j in range(len(yRange)):
                sequence.append([xRange[i],yRange[j]])
        builder.addXYSequence(sequence)
        # build save location
        builder.setSaveDirectory(None)  # if None env will set as USER DEFAULT FOLDER
        builder.setSaveName('celldetection')  # if None will not save anything
        # get the hooks
        builder.setHooks('celldetection')
        # build settings
        builder.setIsShowDisplay(False)
        builder.setIsDebug(False)
        builder.setIsCoreLogDebug(False)
        builder.setIsMultiprocesing(False)  # linux only
        builder.setSavingQueueSize(50)
        builder.setBridgeTimeoutMs(500)
        builder.setPort(4827)
        plugin = builder.getPlugin()
        return plugin

    def visitmarkedcells(self,positions=[[0,0]],zplanefunction=None):
        builder = AcquisitionBuilder()
        # Build the events
        builder.addTimedEvents(30, 0.)
        #builder.addZEvents(0., 1., .5)
        # builder.addChannelEvents('Channel', ['Cy5', 'DAPI', 'FITC', 'Rhodamine'], [10., 10., 10., 10.])
        builder.addXYSequence([[0, 0], [0, 1]])
        # builder.addXYZSequence([[0,0,0],[0,1,2]]) # CANT do XYZ if addXYSequence and addZEvents are used
        builder.setEventsOrder('tpzc')
        # build the hooks
        lib = HookSetLibrary()
        if zplanefunction==None:
            hooks = lib.get('default')
        else:
            hooks=lib.get('')
        builder.linkHooks(hooks)
        # build save location
        builder.setSaveDirectory(None)  # if None env will set as USER DEFAULT FOLDER
        builder.setSaveName('default')  # if None will not save anything

        # build settings
        builder.setIsShowDisplay(False)
        builder.setIsDebug(False)
        builder.setIsCoreLogDebug(False)
        builder.setIsMultiprocesing(False)  # linux only
        builder.setSavingQueueSize(50)
        builder.setBridgeTimeoutMs(500)
        builder.setPort(4827)
        builder.setIsSeeding(False)

        # get the result of the building
        plugin = builder.getPlugin()
        return plugin

    def particledetect(self):
        builder = AcquisitionBuilder()
        # Build the events
        builder.addTimedEvents(30, 1.)
        #builder.addChannelEvents('Channel', ['Cy5', 'DAPI', 'FITC', 'Rhodamine'], [10., 10., 10., 10.])
        # builder.addXYZSequence([[0,0,0],[0,1,2]]) # CANT do XYZ if addXYSequence and addZEvents are used
        builder.setEventsOrder('tpzc')
        # build the hooks
        lib=HookSetLibrary()
        hooks=lib.get('particledetect')
        builder.linkHooks(hooks)
        # build save location
        builder.setSaveDirectory(None)  # if None env will set as USER DEFAULT FOLDER
        builder.setSaveName('particledetect')  # if None will not save anything

        # build settings
        builder.setIsShowDisplay(True)
        builder.setIsDebug(False)
        builder.setIsCoreLogDebug(False)
        builder.setIsMultiprocesing(False)  # linux only
        builder.setSavingQueueSize(50)
        builder.setBridgeTimeoutMs(500)
        builder.setPort(4827)
        builder.setIsSeeding(False)

        # get the result of the building
        plugin = builder.getPlugin()
        return plugin

    def sharpnesscan4color(self):
        builder=AcquisitionBuilder()
        builder.addZEvents(-1,1,1)
        xRange = np.linspace(-1000, 1000, 11)
        yRange = np.linspace(-1000, 1000, 11)
        sequence = []
        for i in range(len(xRange)):
            for j in range(len(yRange)):
                position = [xRange[i], yRange[j]]
                sequence.append(position)
        builder.addXYSequence(sequence)
        builder.setHooks('findzplane4color',channels=channels,exposures=exposures)
        # build save location
        builder.setSaveDirectory(None)  # if None env will set as USER DEFAULT FOLDER
        builder.setSaveName('sharpnessscan')  # if None will not save anything

        # build settings
        builder.setIsShowDisplay(True)
        builder.setIsDebug(False)
        builder.setIsCoreLogDebug(False)
        builder.setIsMultiprocesing(False)  # linux only
        builder.setSavingQueueSize(50)
        builder.setBridgeTimeoutMs(500)
        builder.setPort(4827)
        builder.setIsSeeding(False)

        # get the result of the building
        plugin = builder.getPlugin()
        return plugin

    def sharpnesscan3color(self):
        builder=AcquisitionBuilder()
        builder.addZEvents(-1,1,1)
        xRange = np.linspace(-1000, 1000, 11)
        yRange = np.linspace(-1000, 1000, 11)
        sequence = []
        for i in range(len(xRange)):
            for j in range(len(yRange)):
                position = [xRange[i], yRange[j]]
                sequence.append(position)
        builder.addXYSequence(sequence)
        builder.setHooks('findzplane3color')
        # build save location
        builder.setSaveDirectory(None)  # if None env will set as USER DEFAULT FOLDER
        builder.setSaveName('sharpnessscan')  # if None will not save anything

        # build settings
        builder.setIsShowDisplay(True)
        builder.setIsDebug(False)
        builder.setIsCoreLogDebug(False)
        builder.setIsMultiprocesing(False)  # linux only
        builder.setSavingQueueSize(50)
        builder.setBridgeTimeoutMs(500)
        builder.setPort(4827)
        builder.setIsSeeding(False)

        # get the result of the building
        plugin = builder.getPlugin()
        return plugin

    def postsharpnesscan4color(self):
        builder = AcquisitionBuilder()
        builder.setSaveName('postsharpnesscan4color')  # if None will not save anything
        # build settings
        builder.setIsShowDisplay(True)
        builder.setIsDebug(False)
        builder.setIsCoreLogDebug(False)
        builder.setIsMultiprocesing(False)  # linux only
        builder.setSavingQueueSize(50)
        builder.setBridgeTimeoutMs(500)
        builder.setPort(4827)
        builder.setIsSeeding(False)

        # get the result of the building
        plugin = builder.getPlugin()
        return plugin

    def tracktranscription(self):

        builder = AcquisitionBuilder()
        builder.setSaveName('tracktranscription')
        builder.setHooks('tracktranscription')
        builder.setIsShowDisplay(True)
        builder.setIsDebug(False)
        builder.setIsCoreLogDebug(False)
        builder.setIsMultiprocesing(False)  # linux only
        builder.setSavingQueueSize(50)
        builder.setBridgeTimeoutMs(500)
        builder.setPort(4827)
        builder.setIsSeeding(False)

        # get the result of the building
        plugin = builder.getPlugin()

        plugin = builder.getPlugin()
        return plugin

    def directedevolution(self):
        builder = AcquisitionBuilder()
        builder.setSaveName('directedevolution')
        builder.setHooks('directedevolution')
        builder.setIsShowDisplay(True)
        builder.setIsDebug(False)
        builder.setIsCoreLogDebug(False)
        builder.setIsMultiprocesing(False)  # linux only
        builder.setSavingQueueSize(50)
        builder.setBridgeTimeoutMs(500)
        builder.setPort(4827)
        builder.setIsSeeding(False)

        # get the result of the building

        plugin = builder.getPlugin()
        return plugin


    def image_emulator(self,emulator):
        builder = AcquisitionBuilder()
        # Build the events
        #builder.addTimedEvents(3, 0.)
        # builder.addZEvents(0., 1., .5)
        builder.addChannelEvents('Channel', ['Cy5', 'DAPI'], [10., 10., 10.])
        builder.addXYSequence([[0, 0], [0, 1], [1, 0], [1, 1]])
        # builder.addXYZSequence([[0,0,0],[0,1,2]]) # CANT do XYZ if addXYSequence and addZEvents are used
        builder.setEventsOrder('tpzc')
        # build the hooks
        lib = HookSetLibrary()
        hooks = lib.get('image_emulator',emulator)
        builder.linkHooks(hooks)
        # build save location
        builder.setSaveDirectory(None)  # if None env will set as USER DEFAULT FOLDER
        builder.setSaveName('image_emulator')  # if None will not save anything

        # build settings
        builder.setIsShowDisplay(False)
        builder.setIsDebug(False)
        builder.setIsCoreLogDebug(False)
        builder.setIsMultiprocesing(False)  # linux only
        builder.setSavingQueueSize(50)
        builder.setBridgeTimeoutMs(500)
        builder.setPort(4827)
        builder.setIsSeeding(False)

        # get the result of the building
        plugin = builder.getPlugin()
        return plugin

    def findzplane3color_from_roi(self, positions, z_range, channel, channelMap, channelExposure):
        builder = AcquisitionBuilder()
        builder.setHooks('findzplane3color', channel, channelMap)
        builder.setSaveName('findzplane3color')
        builder.addChannelEvents(channel, channelMap, channelExposure)
        builder.addXYSequence(positions)
        builder.addZEvents(z_range[0], z_range[1], z_range[2])
        builder.setEventsOrder('tpzc')
        builder.setIsShowDisplay(False)
        builder.setIsDebug(False)
        builder.setIsCoreLogDebug(False)
        builder.setIsMultiprocesing(False)  # linux only
        builder.setSavingQueueSize(50)
        builder.setBridgeTimeoutMs(500)
        builder.setPort(4827)
        plugin = builder.getPlugin()
        return plugin

    def xyLooseGrid(self,xRangeROI,yRangeROI,xyOriginROI,calibration=NullCalibration(),timeRange=None,zRange=None,channelRange=None,name='xyLooseGrid',show_display=True,emulator=None,laserIntensities=None):
        builder = AcquisitionBuilder()
        if timeRange:
            builder.addTimedEvents(timeRange[0], timeRange[1])
        if zRange:
            builder.addZEvents(zRange[0], zRange[0], zRange[0])
        if channelRange:
            builder.addChannelEvents(channelRange[0], channelRange[1], channelRange[2])
        if laserIntensities:
            builder.addLaserIntensities(laserIntensities)
        sequence=[]
        for y in yRangeROI:
            for x in xRangeROI:
                sequence.append([x+xyOriginROI[0],y+xyOriginROI[0]])
        sequence=calibration.mapList(sequence)
        builder.addXYSequence(sequence)
        builder.setEventsOrder('tpzc')
        # build the hooks
        lib = HookSetLibrary()
        if emulator:
            hooks=lib.get('image_emulator',emulator)
        else:
            hooks = lib.get('default')
        builder.linkHooks(hooks)
        # build save location
        builder.setSaveDirectory(None)  # if None env will set as USER DEFAULT FOLDER
        builder.setSaveName(name)  # if None will not save anything

        # build settings
        builder.setIsShowDisplay(show_display)
        builder.setIsDebug(False)
        builder.setIsCoreLogDebug(False)
        builder.setIsMultiprocesing(False)  # linux only
        builder.setSavingQueueSize(50)
        builder.setBridgeTimeoutMs(500)
        builder.setPort(4827)
        builder.setIsSeeding(False)

        # get the result of the building
        plugin = builder.getPlugin()
        return plugin

    def xyTightGrid(self,xRangeROI,yRangeROI,xyOriginROI,imageShape,calibration=NullCalibration(),timeRange=None,zRange=None,channelRange=None,name='xyTightGrid'):
        builder = AcquisitionBuilder()
        if timeRange:
            builder.addTimedEvents(timeRange[0],timeRange[1])
        if zRange:
            builder.addZEvents(zRange[0], zRange[0], zRange[0])
        if channelRange:
            builder.addChannelEvents(channelRange[0],channelRange[1],channelRange[2])
        builder = AcquisitionBuilder()
        sequence = []
        for y in yRangeROI:
            for x in xRangeROI:
                sequence.append([x * imageShape[0] + xyOriginROI[0], y * imageShape[1] + xyOriginROI[0]])
        sequence = calibration.map(sequence)
        builder.addXYSequence(sequence)
        builder.setEventsOrder('tpzc')
        # build the hooks
        lib = HookSetLibrary()
        hooks = lib.get('default')
        builder.linkHooks(hooks)
        # build save location
        builder.setSaveDirectory(None)  # if None env will set as USER DEFAULT FOLDER
        builder.setSaveName(name)  # if None will not save anything

        # build settings
        builder.setIsShowDisplay(False)
        builder.setIsDebug(False)
        builder.setIsCoreLogDebug(False)
        builder.setIsMultiprocesing(False)  # linux only
        builder.setSavingQueueSize(50)
        builder.setBridgeTimeoutMs(500)
        builder.setPort(4827)
        builder.setIsSeeding(False)

        # get the result of the building
        plugin = builder.getPlugin()
        return plugin

    def xySequence(self,sequence,calibration=NullCalibration(),timeRange=None,zRange=None,channelRange=None):
        builder = AcquisitionBuilder()
        # Build the events
        if timeRange:
            builder.addTimedEvents(timeRange[0],timeRange[1])
        if zRange:
            builder.addZEvents(zRange[0], zRange[0], zRange[0])
        if channelRange:
            builder.addChannelEvents(channelRange[0],channelRange[1],channelRange[2])
        sequence=calibration.map(sequence)
        builder.addXYSequence(sequence)
        builder.setEventsOrder('tpzc')
        # build the hooks
        lib=HookSetLibrary()
        hooks=lib.get('default')
        builder.linkHooks(hooks)
        # build save location
        builder.setSaveDirectory(None)  # if None env will set as USER DEFAULT FOLDER
        builder.setSaveName('xySequence')  # if None will not save anything

        # build settings
        builder.setIsShowDisplay(False)
        builder.setIsDebug(False)
        builder.setIsCoreLogDebug(False)
        builder.setIsMultiprocesing(False)  # linux only
        builder.setSavingQueueSize(50)
        builder.setBridgeTimeoutMs(500)
        builder.setPort(4827)
        builder.setIsSeeding(False)

        # get the result of the building
        plugin = builder.getPlugin()
        return plugin

    def xyzSequence(self,sequence,timeRange=None,zRange=None,channelRange=None):
        builder = AcquisitionBuilder()
        # Build the events
        if timeRange:
            builder.addTimedEvents(timeRange[0],timeRange[1])
        if zRange:
            builder.addZEvents(zRange[0], zRange[0], zRange[0])
        if channelRange:
            builder.addChannelEvents(channelRange[0],channelRange[1],channelRange[2])
        builder.addXYZSequence(sequence)
        builder.setEventsOrder('tpzc')
        # build the hooks
        lib=HookSetLibrary()
        hooks=lib.get('default')
        builder.linkHooks(hooks)
        # build save location
        builder.setSaveDirectory(None)  # if None env will set as USER DEFAULT FOLDER
        builder.setSaveName('xyzSequence')  # if None will not save anything

        # build settings
        builder.setIsShowDisplay(False)
        builder.setIsDebug(False)
        builder.setIsCoreLogDebug(False)
        builder.setIsMultiprocesing(False)  # linux only
        builder.setSavingQueueSize(50)
        builder.setBridgeTimeoutMs(500)
        builder.setPort(4827)
        builder.setIsSeeding(False)

        # get the result of the building
        plugin = builder.getPlugin()
        return plugin