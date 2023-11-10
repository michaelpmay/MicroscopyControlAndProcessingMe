from source.globals import Globals
from scipy.signal import convolve2d
import numpy as np
import scipy
import time
from PIL import Image
from scipy import signal
from pycromanager import Core
class iHooks:
    '''a set of many hook objects that are used in the acquisition and changed the behavior'''
    pass

class iHook:
    '''a single hook that can be used to change the loop behavior of the acquisition'''
    def __call__(self,event,stack):
        '''implements the API for a pycromanager hook callback. returning the event is used to imply the hook performed
        properly. hooks get evaluated as a callback throughout imaging '''
        pass

    def run(self,event,stack):
        '''runs the hooks from the pycromanager callback scheme'''
        pass


class iHookChain(iHook):
    '''chains of hooks'''
    def run(self,event,stack):
        '''runs the hooks from the pycromanager callback scheme'''
        pass
    def add(self,hook,callback_type):
        '''adds hook to the type of callback'''
        pass

class iHookSet:
    '''wad of hooks for more eacily passing into pycromanager'''
    def properties(self):
        '''returns savable dict like structure of itself'''
        pass
    def load(self,properties):
        '''lods props into self variables'''
        pass

class iAcquisitionHooks:
    '''wad of hook chains for acquisitons'''
    def properties(self):
        '''returns savable dict like structure of itself'''
        pass
    def link(self,acquisitionHooks):
        '''links acquisition-hooks and runs them in order'''
        pass
    def load(self,properties):
        '''lods props into self variables'''
        pass

class iAcquisitionHooksLibrary:
    '''Library of Acqisition hooks'''
    def get(self,key,args,kwargs):
        pass
    def list(self):
        '''returns list of Hooks'''
        pass

class iImageHook:
    '''a single hook that intakes the image and metadata to change the loop behavior of the acquisition.
    seems to run on another thread but i cant fix that'''
    def __call__(self,image,metadata):
        '''implements the API for a pycromanager image-hook callback. returning the event is used to imply the hook performed
        properly. hooks get evaluated as a callback throughout imaging '''
        pass

    def output(self):
        '''retutns a secondary output unrelated to the main loop'''
        pass

class iImageHookChain:
    '''a single hook that intakes the image and metadata to change the loop behavior of the acquisition.
    seems to run on another thread but i cant fix that'''
    def __call__(self,image,metadata):
        '''implements the API for a pycromanager image-hook callback. returning the event is used to imply the hook performed
        properly. hooks get evaluated as a callback throughout imaging '''
        pass

    def output(self):
        '''retutns a secondary output unrelated to the main loop'''
        pass

    def link(self,link):
        '''adds a hook after this hook. Appends hook to a next pointer and then recursivley calls run.'''
        pass


class iHookLibrary:
    '''A class that creates different acquisition hooks. Factory design pattern.'''
    def get(self,key,args,kwargs):
        '''returns a hook from a key & passes args kwargs'''
        pass

class Hook(iHook):
    function=None
    input={}
    output= {}
    def __init__(self,function=None,input=None):
        if function ==None:
            self.function=lambda self,event,stack:event
        else:
            self.function=function

    def run(self,event,stack):
        return self.function(self,event,stack)

    def __call__(self,event,stack):
        return self.run(event,stack)

    @property
    def properties(self):
        props=dict()
        props['HookInputs']=dict()
        props['HookInputs'].update(self.input)
        return props['HookInputs']

class HookChain(iHookChain):
    def __init__(self):
        self.chain=[]
    def link(self,hook):
        if not  isinstance(hook,(Hook,HookChain)):
            raise TypeError
        self.chain.append(hook)
    def run(self,event,stack):
        for hook in self.chain:
            event=hook.run(event,stack)
        return event

class ImageHook(iImageHook):
    function=None
    input= {}
    output=None

    def __init__(self,function=None):
        if function ==None:
            self.function=lambda self,image,metadata:(image,metadata)
        else:
            if not hasattr(function,'__call__'):
                raise TypeError
            self.function=function


    def run(self,image,metadata):
        return self.function(self,image,metadata)


    def __call__(self,image,metadata):
        return self.run(image,metadata)


class ImageHookChain(iImageHookChain):
    def __init__(self):
        self.chain=[]
    def link(self,node):
        if not isinstance(node,(ImageHook,ImageHookChain)):
            return TypeError
        self.chain.append(node)
    def run(self,image,metadata):
        for hook in self.chain:
            (image,metadata)=hook.run(image,metadata)
        return image,metadata

class HookSet(iHookSet):
    name=None
    hookPreHardware=None
    hookPostHardware=None
    hookPostCamera=None
    hookImageProcess=None
    hookEventGeneration=None
    hookImageSaved=None
    args=None
    kwargs=None
    def __init__(self):
        self.name = 'default' #special name for hooks not given a name
        self.hookPreHardware = None
        self.hookPostHardware = None
        self.hookPostCamera = None
        self.hookImageProcess = None
        self.hookEventGeneration = None
        self.hookImageSaved =None
        self.args=()
        self.kwargs = {}
    @property
    def properties(self):
        props=dict()
        #ignore the tooks and just get the name
        props['Hooks Name']=self.name
        props['Hook Args']=self.args
        props['Hook Kwargs'] = self.kwargs
        return props

    def load(self,properties):
        lib=HookSetLibrary()
        hooks=lib.get(properties['Hooks Name'],*properties['Hook Args'],**properties['Hook Kwargs'])
        self.name = hooks.name
        self.args= hooks.args
        self.kwargs = hooks.kwargs
        self.hookPreHardware = hooks.hookPreHardware
        self.hookPostHardware = hooks.hookPostHardware
        self.hookPostCamera = hooks.hookPostCamera
        self.hookImageProcess = hooks.hookImageProcess
        self.hookEventGeneration = hooks.hookEventGeneration
        self.hookImageSaved = hooks.hookImageSaved

    @property
    def output(self):
        output=dict()
        hooks=[self.hookPreHardware,
        self.hookPostHardware,
        self.hookPostCamera,
        self.hookImageProcess,
        self.hookEventGeneration,
        self.hookImageSaved]
        for hook in hooks:
            if hook != None:
                output.update(hook.output)
        return output


class AcquisitionHooks(iAcquisitionHooks):
    chain=[]
    def __init__(self):
        self.hookEventGeneration = None
        self.hookImageSaved = None
    def link(self,hookSet):
        if not  isinstance(hookSet,HookSet):
            raise TypeError
        self.chain.append(hookSet)

    def hookPreHardware(self,event,stack):
        for hook in self.chain:
            if hook.hookPreHardware is not None:
                event=hook.hookPreHardware(event,stack)
        return event

    def hookPostHardware(self,event,stack):
        for hook in self.chain:
            if hook.hookPostHardware is not None:
                event = hook.hookPostHardware(event, stack)
        return event

    def hookPostCamera(self,event,stack):
        for hook in self.chain:
            if hook.hookPostCamera is not None:
                event = hook.hookPostCamera(event,stack)
        return event

    def hookImageProcess(self,image,metadata):
        for hook in self.chain:
            if hook.hookImageProcess is not None:
                image,metadata = hook.hookImageProcess(image,metadata)
        return image,metadata


    @property
    def properties(self):
        props= {}
        for i in range(len(self.chain)):
            hprops=self.chain[i].properties
            key=str(i)
            props[key]=hprops
        return props
    @property
    def name(self):
        n=[]
        for i in range(len(self.chain)):
            n.append(self.chain[i].name)
        return n
    def load(self,properties):
        lib = HookSetLibrary()
        self.chain=[]
        for i in range(64):
            i_str=str(i)
            if i_str in properties.keys():
                hooks = lib.get(properties[i_str]['Hooks Name'], *properties[i_str]['Hook Args'], **properties[i_str]['Hook Kwargs'])
                hooks.name = properties[i_str]['Hooks Name']
                hooks.args = properties[i_str]['Hook Args']
                hooks.kwargs = properties[i_str]['Hook Kwargs']
                hooks.hookPreHardware = hooks.hookPreHardware
                hooks.hookPostHardware = hooks.hookPostHardware
                hooks.hookPostCamera = hooks.hookPostCamera
                hooks.hookImageProcess = hooks.hookImageProcess
                hooks.hookEventGeneration = hooks.hookEventGeneration
                hooks.hookImageSaved = hooks.hookImageSaved
                self.chain.append(hooks)

class HookSetLibrary:
    def get(self, key,*args,**kwargs):
        if not isinstance(key, (str,list)):
            raise TypeError("a string or list please")
        if isinstance(key,str):
            if key in ('get', 'list'):
                raise KeyError
            hooks=eval("self." + key+"(*args,**kwargs)")
            return hooks

    def list(self):
        names = []
        objectNames = dir(self)
        for name in objectNames:
            if name[0:2] != "__":
                if name not in ('get', 'list'):
                    names.append(name)
        return names

    def default(self):
        hooks=HookSet()
        hooks.name='default'
        return hooks

    def hello_world(self):
        hooks=HookSet()
        hooks.name='hello_world'

        def HiHi(self,event , stack):
          #  print('Hello World')
            return event

        hooks.hookPreHardware=Hook(function=HiHi)
        return hooks

    def verbose(self):
        hooks = HookSet()
        hooks.name = 'verbose'

        def HookPreHardware(self,event , stack):
            string='PreHardware'
            #print(string)

            return event

        def HookPostHardware(self,event , stack):
            string='PostHardware'
            #print(string)
            return event

        def HookPostCamera(self,event , stack):
            string = 'PostCamera'
            #print(string)
            return event

        def HookImageProcess(self,image,metadata ,stack):
            string = 'ImageProcess'
            #print(string)
            return image,metadata

        hooks.hookPreHardware=Hook(function=HookPreHardware)
        hooks.hookPostHardware=Hook(function=HookPostHardware)
        hooks.hookPostCamera=Hook(function=HookPostCamera)
        hooks.hookImageProcess=ImageHook(function=HookImageProcess)
        return hooks

    def null(self):
        hooks = HookSet()
        hooks.name = 'null'

        def HookPreHardware(self,event , stack):
            return event

        def HookPostHardware(self,event , stack):
            return event

        def HookPostCamera(self,event , stack):
            return event

        def HookImageProcess(self,image,metadata):
            return image,metadata

        hooks.hookPreHardware=Hook(function=HookPreHardware)
        hooks.hookPostHardware=Hook(function=HookPostHardware)
        hooks.hookPostCamera=Hook(function=HookPostCamera)
        hooks.hookImageProcess=ImageHook(function=HookImageProcess)
        return hooks

    def detect_cell(self, events=[]):
        hooks = HookSet()
        hooks.name = 'detect_cell'

        return hooks

    def findzplane1color(self,channel,channelMap):
        hooks = HookSet()
        hooks.name = 'findzplane1color'
        hooks.args=(channel,channelMap)
        def HookPostCamera(self, event , stack):
            #print(event)
            return event
        hooks.hookPostCamera = Hook(function=HookPostCamera)
        hooks.hookPostCamera.input['channel'] = channel
        hooks.hookPostCamera.input['channelMap'] = channelMap
        return hooks

    def findzplane3color(self,channel,channelMap):
        hooks = HookSet()
        hooks.name = 'findzplane3color'
        hooks.args = (channel,channelMap)
        def HookPostCamera(self,event , stack):
            #print(self.input['channelMap'])
            #print(event)
            if not hasattr(self,'sharpness'):
                self.sharpness=[]
            if not hasattr(self,'index'):
                self.index=0
            if 'sharpness' not in self.output:
                self.output['sharpness']=[]
                self.output['xRange'] = []
                self.output['yRange'] = []
                self.output['zRange'] = []
                self.output['channelRange'] = []
                self.channelMap=self.input['channelMap']
                #self.shown_image = np.full((512*2, 512*2, 3), 125, dtype=np.uint8)
                self.oldPosition=None
            #print('PostCamera {0}'.format(event))
            core=Core()
            time.sleep(.05)
            core.snap_image()
            tagged_image = core.get_tagged_image()
            # get the pixels in numpy array and reshape it according to its height and width
            image_array = np.reshape(
                tagged_image.pix,
                newshape=[-1, tagged_image.tags["Height"], tagged_image.tags["Width"]],
            )
            # for display, we can scale the image into the range of 0~255
            image_array = (image_array / image_array.max() * 255).astype("uint8")
            #print(event)
            #print(event['channel']['config'])
            index=self.channelMap.index(event['channel']['config'])
            #print(index)
            #self.shown_image[:, :, index] = image_array[0, :, :]
            # return the first channel if multiple exists
            kernel=np.array([[0, 1, 0],
                             [1,-4, 1],
                             [0, 1, 0,]]).astype('uint8')
            sharpnessValue=np.sum(np.sum(convolve2d(image_array[0,:,:],kernel)))/np.sum(np.sum(image_array[0,:,:]))
            print("(sharpness,x,y,z) : ({0},{1},{2},{3})".format(sharpnessValue,event['x'],event['y'],event['z']))
            if event['x'] not in self.output['xRange']:
                self.output['xRange'].append(event['x'])
                self.output['xRange'].sort()
            if event['y'] not in self.output['yRange']:
                self.output['yRange'].append(event['y'])
                self.output['yRange'].sort()
            if event['z'] not in self.output['zRange']:
                self.output['zRange'].append(event['z'])
                self.output['zRange'].sort()
            if event['channel']['config'] not in self.output['channelRange']:
                self.output['channelRange'].append(event['channel']['config'])
                self.output['channelRange'].sort()
            if event['channel']['config']==self.channelMap[0]:
                self.detail=sharpnessValue
            elif event['channel']['config']==self.channelMap[1]:
                self.detail = self.detail+sharpnessValue
            elif event['channel']['config']==self.channelMap[2]:
                self.detail = self.detail+sharpnessValue
                self.output['sharpness'].append([self.detail, event['x'], event['y'], event['z']])
                print("(s,x,y,z) : ({0},{1},{2},{3})".format(self.detail, event['x'], event['y'], event['z']))
                position=[event['x'], event['y']]
                if self.oldPosition==None:
                    self.oldPosition=position
                    self.maxSharpness = []
                    self.maxSharpness.append(self.detail)
                    self.maxSharpnessPosition = []
                    self.maxSharpnessPosition.append([event['x'], event['y'], event['z']])
                    self.output['maxSharpness']=[]
                    self.output['maxSharpnessPosition'] = []
                elif position != self.oldPosition:
                    self.maxSharpness.append(self.detail)
                    self.maxSharpnessPosition.append([event['x'], event['y'], event['z']])
                    self.oldPosition=position
                else:
                    if self.detail>self.maxSharpness[-1]:
                        self.maxSharpness[-1]=self.detail
                        self.maxSharpnessPosition[-1]=[event['x'], event['y'], event['z']]
                self.output['maxSharpness']=self.maxSharpness
                self.output['maxSharpnessPosition'] = self.maxSharpnessPosition
                #cv2.imshow('Image', self.shown_image)
                #cv2.waitKey(1)
            return event
        hooks.hookPostCamera = Hook(function=HookPostCamera)
        hooks.hookPostCamera.input['channelMap']=channelMap
        return hooks

    def findzplane4color(self,channelMap=['Violet','Red','Green','Blue']):
        hooks = HookSet()
        hooks.name = 'findzplane4color'

        def HookPostCamera(self,event , stack):
            print(self.input['channelMap'])
            if not hasattr(self,'sharpness'):
                self.sharpness=[]
            if not hasattr(self,'index'):
                self.index=0
            if 'sharpness' not in self.output:
                self.output['sharpness']=[]
                self.output['xRange'] = []
                self.output['yRange'] = []
                self.output['zRange'] = []
                self.output['channelRange'] = []
                self.channelMap=self.input['channelMap']
                #self.shown_image = np.full((512*2, 512*2, 4), 125, dtype=np.uint8)
                self.oldPosition=None
            print('PostCamera {0}'.format(event))
            core=bridge.get_core()
            time.sleep(.05)
            core.snap_image()
            tagged_image = core.get_tagged_image()
            # get the pixels in numpy array and reshape it according to its height and width
            image_array = np.reshape(
                tagged_image.pix,
                newshape=[-1, tagged_image.tags["Height"], tagged_image.tags["Width"]],
            )
            # for display, we can scale the image into the range of 0~255
            image_array = (image_array / image_array.max() * 255).astype("uint8")
            print(event['channel']['config'])
            index=self.channelMap.index(event['channel']['config'])
            print(index)
            #self.shown_image[:, :, index] = image_array[0, :, :]
            # return the first channel if multiple exists
            kernel=np.array([[0, 1, 0],
                             [1,-4, 1],
                             [0, 1, 0,]]).astype('uint8')
            sharpnessValue=np.sum(np.sum(convolve2d(image_array[0,:,:],kernel)))/np.sum(np.sum(image_array[0,:,:]))
            print("(sharpness,x,y,z) : ({0},{1},{2},{3})".format(sharpnessValue,event['x'],event['y'],event['z']))
            if event['x'] not in self.output['xRange']:
                self.output['xRange'].append(event['x'])
                self.output['xRange'].sort()
            if event['y'] not in self.output['yRange']:
                self.output['yRange'].append(event['y'])
                self.output['yRange'].sort()
            if event['z'] not in self.output['zRange']:
                self.output['zRange'].append(event['z'])
                self.output['zRange'].sort()
            if event['channel']['config'] not in self.output['channelRange']:
                self.output['channelRange'].append(event['channel']['config'])
                self.output['channelRange'].sort()
            if event['channel']['config']==self.channelMap[0]:
                self.detail=sharpnessValue
            elif event['channel']['config']==self.channelMap[1]:
                self.detail = self.detail+sharpnessValue
            elif event['channel']['config']==self.channelMap[2]:
                self.detail = self.detail+sharpnessValue
            elif event['channel']['config']==self.channelMap[3]:
                self.detail = self.detail+sharpnessValue
                self.output['sharpness'].append([self.detail, event['x'], event['y'], event['z']])
                print("(s,x,y,z) : ({0},{1},{2},{3})".format(self.detail, event['x'], event['y'], event['z']))
                position=[event['x'], event['y']]
                if self.oldPosition==None:
                    self.oldPosition=position
                    self.maxSharpness = []
                    self.maxSharpness.append(self.detail)
                    self.maxSharpnessPosition = []
                    self.maxSharpnessPosition.append([event['x'], event['y'], event['z']])
                    self.output['maxSharpness']=[]
                    self.output['maxSharpnessPosition'] = []
                elif position != self.oldPosition:
                    self.maxSharpness.append(self.detail)
                    self.maxSharpnessPosition.append([event['x'], event['y'], event['z']])
                    self.oldPosition=position
                else:
                    if self.detail>self.maxSharpness[-1]:
                        self.maxSharpness[-1]=self.detail
                        self.maxSharpnessPosition[-1]=[event['x'], event['y'], event['z']]
                self.output['maxSharpness']=self.maxSharpness
                self.output['maxSharpnessPosition'] = self.maxSharpnessPosition
                #cv2.imshow('Image', self.shown_image)
                #cv2.waitKey(1)
            return event
        hooks.hookPostCamera = Hook(function=HookPostCamera)
        hooks.hookPostCamera.input['channelMap']=channelMap
        return hooks

    def celldetection(self,channelMap=['Red','Green','Blue']):
        hooks = HookSet()
        hooks.name = 'celldetection'
        def HookPostCamera(self,event , stack):
            if 'mask' not in self.output.keys():
                self.output['mask']=[]
                self.output['roi'] = []
                self.constructed_image = np.full((512*2, 512*2, 3), 125, dtype=np.uint8)
                self.channelMap=self.input['channelMap']
                #self.shown_image = np.full((128, 128, 3), 125, dtype=np.uint8)
            print('PostHardware {0}'.format(event))
            core = bridge.get_core()
            time.sleep(.05)
            core.snap_image()
            tagged_image = core.get_tagged_image()
            # get the pixels in numpy array and reshape it according to its height and width
            image_array = np.reshape(
                tagged_image.pix,
                newshape=[-1, tagged_image.tags["Height"], tagged_image.tags["Width"]],
            )
            image_array = (image_array / image_array.max() * 255).astype("uint8")
            if event['channel']['config']==self.channelMap[0]:
                self.constructed_image[:, :, 0] = image_array[0, :, :]
            if event['channel']['config'] == self.channelMap[1]:
                self.constructed_image[:, :, 1] = image_array[0, :, :]
            if event['channel']['config'] == self.channelMap[2]:
                self.constructed_image[:, :, 2] = image_array[0, :, :]
                model=CellMaskCellpose()
                grayImage=np.sum(self.constructed_image,axis=2)
                mask=model.detect(grayImage[::4,::4])
                mask[mask>0]=1
                print(np.sum(np.sum(mask))/128**2)
                if (np.sum(np.sum(mask))/128**2)>.10:
                    self.output['roi'].append([event['x'], event['y']])
                self.output['mask'].append(mask)
                #self.shown_image[:, :, 0] = mask*200
                #self.shown_image[:, :, 1] = mask*200
                #self.shown_image[:, :, 2] = mask*200
                cv2.imshow('Mask',cv2.resize(self.shown_image,(512*2,512*2)))
                cv2.waitKey(1)
            return event
        hooks.hookPostCamera = Hook(function=HookPostCamera)
        hooks.hookPostCamera.input['channelMap']=channelMap
        return hooks

    def write(self,string='testing'):
        hooks = AcquisitionHooks()
        hooks.name = 'write'
        def HookPreHardware(self,event ,stack):
            if 'string' not in self.output.keys():
                self.output['string']=self.input['string']
        hook=Hook(function=HookPreHardware)
        hook.input={"string":string}
        hooks.hookPreHardware=hook
        return hooks

    def read(self):
        hooks = AcquisitionHooks()
        hooks.name = 'read'
        def HookPreHardware(self,event ,stack):
            print(self.input['string'])
        hooks.hookPreHardware=Hook(function=HookPreHardware)

        return hooks

    def seedevents(self,events):
        hooks=HookSet()
        hooks.name='seedevents'
        def HookImageProcess(self,image,metadata ,stack):
            print(metadata)
            print(image)
            if not hasattr(self,'index'):
                self.index=1 #skip first event
            if self.index<len(self.input['events']):
                stack.put(self.input['events'][self.index])
            else:
                stack.put(None) #this will close the Acquisition!
            self.index=self.index+1
            print(len(stack.queue))

            return image,metadata
        hook=ImageHook(function=HookImageProcess)
        hook.input['events']=events
        hooks.hookImageProcess=hook
        return hooks

    def seedeventssharpness3color(self,channelMap=['Red','Green','Blue']):
        hooks=HookSet()
        hooks.name='seedeventssharpness3color'
        def HookImageProcess(self,image,metadata ,stack):
            print(metadata)
            print(image)
            if not hasattr(self,'index'):
                self.index=1 #skip first event
                self.channelMap = self.input['channelMap']
                self.output['sharpness'] = []
                self.output['xRange'] = []
                self.output['yRange'] = []
                self.output['zRange'] = []
                self.output['channelRange'] = []
                self.channelMap = self.input['channelMap']
                # self.shown_image = np.full((512*2, 512*2, 4), 125, dtype=np.uint8)
                self.oldPosition = None

            event=self.input['events'][self.index-1]
            print(event)
            image_array = (image / image.max() * 255).astype("uint8")
            print(event['channel']['config'])
            index = self.channelMap.index(event['channel']['config'])
            print(index)
            # self.shown_image[:, :, index] = image_array[0, :, :]
            # return the first channel if multiple exists
            kernel = np.array([[0, 1, 0],
                               [1, -4, 1],
                               [0, 1, 0, ]]).astype('uint8')
            sharpnessValue = np.sum(np.sum(convolve2d(image_array, kernel))) / np.sum(
                np.sum(image_array))

            if event['x'] not in self.output['xRange']:
                self.output['xRange'].append(event['x'])
                self.output['xRange'].sort()
            if event['y'] not in self.output['yRange']:
                self.output['yRange'].append(event['y'])
                self.output['yRange'].sort()
            if event['z'] not in self.output['zRange']:
                self.output['zRange'].append(event['z'])
                self.output['zRange'].sort()
            if event['channel']['config'] not in self.output['channelRange']:
                self.output['channelRange'].append(event['channel']['config'])
                self.output['channelRange'].sort()
            if event['channel']['config']==self.channelMap[0]:
                self.detail=sharpnessValue
            elif event['channel']['config']==self.channelMap[1]:
                self.detail = self.detail+sharpnessValue
            elif event['channel']['config']==self.channelMap[2]:
                self.detail = self.detail+sharpnessValue
            elif event['channel']['config']==self.channelMap[3]:
                self.detail = self.detail+sharpnessValue
                self.output['sharpness'].append([self.detail, event['x'], event['y'], event['z']])
                print("(s,x,y,z) : ({0},{1},{2},{3})".format(self.detail, event['x'], event['y'], event['z']))
                position=[event['x'], event['y']]
                if self.oldPosition==None:
                    self.oldPosition=position
                    self.maxSharpness = []
                    self.maxSharpness.append(self.detail)
                    self.maxSharpnessPosition = []
                    self.maxSharpnessPosition.append([event['x'], event['y'], event['z']])
                    self.output['maxSharpness']=[]
                    self.output['maxSharpnessPosition'] = []
                elif position != self.oldPosition:
                    self.maxSharpness.append(self.detail)
                    self.maxSharpnessPosition.append([event['x'], event['y'], event['z']])
                    self.oldPosition=position
                else:
                    if self.detail>self.maxSharpness[-1]:
                        self.maxSharpness[-1]=self.detail
                        self.maxSharpnessPosition[-1]=[event['x'], event['y'], event['z']]
                self.output['maxSharpness']=self.maxSharpness
                self.output['maxSharpnessPosition'] = self.maxSharpnessPosition

            print(sharpnessValue)
            if self.index<len(self.input['events']):
                stack.put(self.input['events'][self.index])
            else:
                stack.put(None) #this will close the Acquisition!
            self.index=self.index+1
            print(len(stack.queue))

            return image,metadata
        hook=ImageHook(function=HookImageProcess)
        hook.input['channelMap']=channelMap
        hooks.hookImageProcess=hook
        return hooks

    def seedeventssharpness1color(self,channelMap=['Red']):
        hooks=HookSet()
        hooks.name='seedeventssharpness1color'
        def HookImageProcess(self,image,metadata ,stack):
            #print(metadata)
            #print(image)
            if not hasattr(self,'index'):
                self.index=1 #skip first event
                self.channelMap = self.input['channelMap']
                self.output['sharpness'] = []
                self.output['xRange'] = []
                self.output['yRange'] = []
                self.output['zRange'] = []
                self.output['channelRange'] = []
                self.channelMap = self.input['channelMap']
                # self.shown_image = np.full((512*2, 512*2, 4), 125, dtype=np.uint8)
                self.oldPosition = None

            try:
                event=self.input['events'][self.index-1]
            except:
                event = None
                stack.put(None) #this will close the Acquisition!
                return event
          #  print(event)
            image_array = (image / image.max() * 255).astype("uint8")
       #     print(event['channel']['config'])
            index = self.channelMap.index(event['channel']['config'])
          #  print(index)
            # self.shown_image[:, :, index] = image_array[0, :, :]
            # return the first channel if multiple exists
            kernel = np.array([[0, 1, 0],
                               [1, -4, 1],
                               [0, 1, 0, ]]).astype('uint8')
            sharpnessValue = np.sum(np.sum(convolve2d(image_array, kernel))) / np.sum(
                np.sum(image_array))

            if event['x'] not in self.output['xRange']:
                self.output['xRange'].append(event['x'])
                self.output['xRange'].sort()
            if event['y'] not in self.output['yRange']:
                self.output['yRange'].append(event['y'])
                self.output['yRange'].sort()
            if event['z'] not in self.output['zRange']:
                self.output['zRange'].append(event['z'])
                self.output['zRange'].sort()
            if event['channel']['config'] not in self.output['channelRange']:
                self.output['channelRange'].append(event['channel']['config'])
                self.output['channelRange'].sort()
            if event['channel']['config']==self.channelMap[0]:
                self.detail=sharpnessValue
                self.output['sharpness'].append([self.detail, event['x'], event['y'], event['z']])
              #  print("(s,x,y,z) : ({0},{1},{2},{3})".format(self.detail, event['x'], event['y'], event['z']))
                position=[event['x'], event['y']]
                if self.oldPosition==None:
                    self.oldPosition=position
                    self.maxSharpness = []
                    self.maxSharpness.append(self.detail)
                    self.maxSharpnessPosition = []
                    self.maxSharpnessPosition.append([event['x'], event['y'], event['z']])
                    self.output['maxSharpness']=[]
                    self.output['maxSharpnessPosition'] = []
                elif position != self.oldPosition:
                    self.maxSharpness.append(self.detail)
                    self.maxSharpnessPosition.append([event['x'], event['y'], event['z']])
                    self.oldPosition=position
                else:
                    if self.detail>self.maxSharpness[-1]:
                        self.maxSharpness[-1]=self.detail
                        self.maxSharpnessPosition[-1]=[event['x'], event['y'], event['z']]
                self.output['maxSharpness']=self.maxSharpness
                self.output['maxSharpnessPosition'] = self.maxSharpnessPosition

         #   print(sharpnessValue)
            if self.index<len(self.input['events']):
                stack.put(self.input['events'][self.index])
            else:
                stack.put(None) #this will close the Acquisition!
            self.index=self.index+1
         #   print(len(stack.queue))

            return image,metadata
        hook=ImageHook(function=HookImageProcess)
        hook.input['channelMap']=channelMap
        hooks.hookImageProcess=hook
        return hooks

    def seedevents3ColorImaging(self,events=[]):
        hooks=HookSet()
        hooks.name='seedevents'
        def HookImageProcess(self,image,metadata ,stack):
            if not hasattr(self,'index'):
                self.index=0
            print(len(stack.queue))
            if self.index<len(self.input['events']):
                stack.put(self.input['events'][self.index])
            else:
                stack.put(None) #this will close the Acquisition!
            self.index=self.index+1
            print(len(stack.queue))

            return image,metadata
        hook=ImageHook(function=HookImageProcess)
        hook.input['events']=events
        hooks.hookImageProcess=hook
        return hooks

    def snap(self):
        hooks = HookSet()
        hooks.name = 'snap'
        def HookPostHardware(self,event ,stack):
            core = bridge.get_core()
            time.sleep(.05)
            core.snap_image()
            tagged_image = core.get_tagged_image()
            # get the pixels in numpy array and reshape it according to its height and width
            image_array = np.reshape(
                tagged_image.pix,
                newshape=[-1, tagged_image.tags["Height"], tagged_image.tags["Width"]],
            )
            # for display, we can scale the image into the range of 0~255
            image_array = (image_array / image_array.max() * 255).astype("uint8")
            #self.shown_image[:, :, self.channelMap[event['channel']['config']]] = image_array[0, :, :]
            return event
        hooks.hookPostCamera.add(Hook(function=HookPostHardware))
        return hooks

    def interpolatezplane(self,maxSharpnessPosition=[[-1,-1,0],[-1,1,0],[1,1,0],[1,-1,0]]):
        hooks = HookSet()
        hooks.name = 'interpolatezplane'
        def HookPostHardware(self,event ,stack):
            print('HookPostHardware {0}'.format(event))
            xRange=[self.input['maxSharpnessPosition'][0][0],self.input['maxSharpnessPosition'][1][0],self.input['maxSharpnessPosition'][2][0],self.input['maxSharpnessPosition'][3][0]]
            yRange=[self.input['maxSharpnessPosition'][0][1],self.input['maxSharpnessPosition'][1][1],self.input['maxSharpnessPosition'][2][1],self.input['maxSharpnessPosition'][3][1]]
            zRange=[self.input['maxSharpnessPosition'][0][2],self.input['maxSharpnessPosition'][1][2],self.input['maxSharpnessPosition'][2][2],self.input['maxSharpnessPosition'][3][2]]
            x=event['x']
            y=event['y']
            print(zRange)
            interpolator=interpolate.interp2d(xRange,yRange,zRange)
            z=interpolator(x,y)[0]
            print(int(z))
            core=bridge.get_core()
            core.set_position(int(z))
            time.sleep(0.1)
            return event
        hooks.hookPostHardware=Hook(function=HookPostHardware)
        hooks.hookPostHardware.input={'maxSharpnessPosition':maxSharpnessPosition}
        return hooks

    def particledetect(self):
        hooks = HookSet()
        hooks.name = 'particledetect'
        def HookImageProcess(self,image,metadata,stack):
            print('HookImageProcess {0}'.format(image))

            return image,metadata
        def HookPostHardware(self,event ,stack):
            if self.isInitialized==False:
                self.initialize()
                self.isInitialized=True
            core=bridge.get_core()
            for i in range(self.zRange):
                core.move(self.zRange[i])
                core.snap_img()
                tagged_image = core.get_tagged_image()
                image_array = np.reshape(
                    tagged_image.pix,
                    newshape=[-1, tagged_image.tags["Height"], tagged_image.tags["Width"]],
                )

                image_near_spot=image_array[(self.loation-6):(self.loation-6)]
                spotimage=scipy.signal.convolve2d(self.kernel2D,image_near_spot)


            return event
        def initialize(self):
            self.zRange=[-1,0,1]
            kernel1D = signal.gaussian(3, 16)
            kernel2D = np.outer(kernel1D, kernel1D)
            self.kernel=kernel2D
            self.location

        hooks.hookImageProcess = ImageHook(function=HookImageProcess)
        hooks.hookPostHardware = Hook(function=HookPostHardware)
        return hooks

    def seeddirectedevolution(self,detector=None,calibrator=None):
        hooks = HookSet()
        hooks.name = 'directedevolution'
        def HookImageProcess(self,image,metadata ,stack):
            if self.isInitialized==False:
                self.index=0
                self.isInitialized=True
            event = self.input['events'][self.index - 1]

            pixCentroid=self.detector.process(image)
            galvoCentroid=self.calibration.calibrate(pixCentroid)

            if self.index<len(self.input['events']):
                stack.put(self.input['events'][self.index])
            else:
                stack.put(None) #this will close the Acquisition!
            self.index=self.index+1
            return image,metadata
        hooks.hookImageProcess=ImageHook(function=HookImageProcess)
        hooks.hookImageProcess.isInitialized=False
        hooks.hookImageProcess.detector=detector
        hooks.hookImageProcess.calibration=calibrator
        return hooks

    def tracktranscription(self):
        hooks=HookSet()
        hooks.name = 'tracktranscription'
        return hooks

    def directedevolution(self):
        hooks=HookSet()
        hooks.name = 'directedevolution'
        return hooks

    def print(self,printString):
        hooks=HookSet()
        hooks.name='print'

        def HookPostHardware(self, event , stack):
            print(self.printString)
        hooks.hookPostHardware=Hook(function=HookPostHardware)
        hooks.hookPostHardware.printString=printString
        return hooks


    def image_emulator(self,emulator):
        hooks = HookSet()
        hooks.name = 'image_emulator'

        def HookImageProcess(self,image,metadata):
            #print('hookImageProcess')
            #print('Emulating Image')
            g = Globals()
            event=g.currentEvent.pop(0)
            channelKeys=self.CHANNEL_KEYS
            #print(event)
            if 'z' in event.keys():
                z=event['z']
            else:
                z=0

            if 'channel' in event['axes'].keys():
                channel=event['axes']['channel']
                if channel in channelKeys:
                    index=channelKeys[channel]
                else:
                    index=len(self.CHANNEL_KEYS)
                    self.CHANNEL_KEYS[channel]=index
            else:
                index=0
            position=[event['x'],event['y'],z]
            image=self.emulator.generate(position,channelIndex=index)
            return (image,metadata)
        def HookPostHardware(self,event,stack):
            g=Globals()
            #print('hookPostHardWare')
            g.currentEvent.append(event)
            return event

        hooks.hookImageProcess=ImageHook(function=HookImageProcess)
        hooks.hookImageProcess.CHANNEL_KEYS={}
        hooks.hookImageProcess.emulator=emulator
        hooks.hookPostHardware=Hook(function=HookPostHardware)
        return hooks

    def findzplane2color(self):
        hooks = HookSet()
        hooks.name = 'findzplane2color'
        return hooks

    def find_roi_with_detector(self,detector):
        hooks = HookSet()
        hooks.name = 'find_roi_with_detector'
        return hooks
