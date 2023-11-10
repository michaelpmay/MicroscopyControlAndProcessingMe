import glob
import os
import pickle
import collections
import numpy as np
import cv2
from source.calibration import MatrixMultiCalibration
import urllib.request
from pathlib import Path
import shutil
class iDataManager:
    '''Data manager load and save key value pairs'''
    def save(self,key,value):
        """saves an item with an associated name"""
        pass

    def load(self,key):
        """loads a item using the name"""
        pass

    def remove(self,key):
        """removes the item with the name in the directory"""
        pass


class iIOSystem:
    """implemetns SAVE-AS functionality"""
    def save(self,key,value):
        """takes the data and saves file using a particular format"""
        pass
    def load(self,key):
        """takes the data and loads file using a particular format"""
        pass

class DataManagerCache:
    '''Implements a cache for file-laoding using key value pairs. the cashe has a maximum size and adding items
    beyond tht size will remove the oldest item'''
    hashmap=None
    size=None
    maxNumItems=None
    def __init__(self,size=50):
        self.maxNumItems=size
        self.hashmap=collections.OrderedDict()
        self.size=size

    def load(self,key):
        '''gets value from key by dictionary lookup'''
        return self.hashmap[key]

    def save(self,key,value):
        if not isinstance(key,str):
            raise TypeError
        if len(self.hashmap)==self.maxNumItems:
            self.hashmap.popitem(last=False)
        self.hashmap[key]=value

    def remove(self,key):
        self.hashmap.pop(key)

    @property
    def properties(self):
        props=dict()
        props['CasheBufferSize']=self.maxNumItems
        return props

    def clear(self):
        self.hashmap=collections.OrderedDict()



class IOPickle(iIOSystem):
    def save(self,key,value):
        with open(key,'wb') as file:
            pickle.dump(value,file)

    def load(self,key):
        with open(key,'rb') as file:
            return pickle.load(file)

class IOState(iIOSystem):
    def save(self,key,value):
        #todo
        pass

    def load(self,key):
        #todo
        pass

class IODict(iIOSystem):
    def save(self,key,dictionary):
        if not isinstance(key,str):
            raise TypeError
        if not isinstance(dictionary,dict):
            raise TypeError
        with open(key, 'w+') as file:
            for dictKey in dictionary.keys():
                dictValue=dictionary[dictKey]
                if isinstance(dictValue,np.ndarray):
                    dictValue.tolist()
                file.write('%s=%s\n' % (dictKey, dictValue))

    def load(self,key):
        if not isinstance(key, str):
            raise TypeError
        dictionary=dict()
        with open(key, 'r+') as file:
            completeString =''
            for row in file:
                row=row.replace("\n","")# remove \n from the loaded string
                completeString = completeString + row
                if row[-1]==',':
                    continue # keep reading and appending if the line is incomplete
                splitString=completeString.split("=",1)
                key=splitString[0]
                try:
                    value=eval(splitString[1])
                except:
                    value=splitString[1]
                dictionary[key]=value
                completeString=''
        return dictionary

class IOBytes(iIOSystem):
    def save(self,key,value):
        path = Path(key)
        if not os.path.isdir(path.parent.absolute()):
            os.makedirs(path.parent.absolute())
        with open(key, 'wb') as f:
            f.write(value)

class IOJpeg(iIOSystem):
    def save(self,key,value):
        # todo
        pass
    def load(self,key):
        # todo
        pass

class IOTiff(iIOSystem):
    def save(self,key,value):
        # todo
        pass
    def load(self,key):
        # todo
        pass

class IOImage(iIOSystem):
    def save(self,key,value):
        if not isinstance(key,str):
            raise TypeError
        if not isinstance(value,(np.ndarray,list)):
            raise TypeError
        cv2.imwrite(key,value)

    def load(self,key):
        if not isinstance(key,str):
            raise TypeError
        value=cv2.imread(key)
        if value is None:
            raise ValueError
        return value

class iIOManager:
    def save(self,key,value,type):
        '''saves a data as a type'''
        pass
    def load(self,key,classtype=None):
        '''load a key into a python object. if prefered class is used it will choose that class type'''
        pass
    def addMap(self,key,value,IOFormat):
        pass

class IOManager(iIOManager):
    '''changes the IO based on the data type'''
    def __init__(self):
        self._createObjectToSaveFormatMaps()
        self._createClassPreferences()

    def _createObjectToSaveFormatMaps(self):
        self.addIOMap('ndarray', 'jpg', IOImage())
        self.addIOMap('ndarray', 'png', IOImage())
        self.addIOMap('ndarray', 'tiff', IOImage())
        self.addIOMap('ndarray', 'pkl', IOPickle())

        self.addIOMap('MicroscopyImage', 'jpg', IOImage())
        self.addIOMap('MicroscopyImage', 'png', IOImage())
        self.addIOMap('MicroscopyImage', 'tiff', IOImage())
        self.addIOMap('MicroscopyImage', 'pkl', IOPickle())

        self.addIOMap('bytes','jpg',IOBytes())
        self.addIOMap('bytes', 'png', IOBytes())
        self.addIOMap('bytes', 'tiff', IOBytes())
        self.addIOMap('bytes', 'pkl', IOBytes())
        self.addIOMap('bytes', 'txt', IOBytes())
        self.addIOMap('bytes', 'acq', IOBytes())
        self.addIOMap('bytes', 'cfg', IOBytes())
        self.addIOMap('bytes', 'mcal', IOBytes())
        self.addIOMap('bytes', 'cal', IOBytes())

        self.addIOMap('dict', 'pkl', IODict())
        self.addIOMap('dict', 'acq', IODict())
        self.addIOMap('dict', 'cfg', IODict())
        self.addIOMap('dict', 'cal', IODict())
        self.addIOMap('dict', 'mcal', IODict())

        self.addIOMap('str',   'pkl', IOPickle())
        self.addIOMap('int',   'pkl', IOPickle())
        self.addIOMap('float', 'pkl', IOPickle())
        self.addIOMap('list',  'pkl', IOPickle())
        self.addIOMap('tuple', 'pkl', IOPickle())

    def _createClassPreferences(self):
        self.prefferedClass=dict()
        self.prefferedClass['pkl']='str'
        self.prefferedClass['jpg'] = 'ndarray'
        self.prefferedClass['jpeg'] = 'ndarray'
        self.prefferedClass['tiff'] = 'ndarray'
        self.prefferedClass['png'] = 'ndarray'
        self.prefferedClass['d']='dict'
        self.prefferedClass['acq']='dict'
        self.prefferedClass['cfg']='dict'
        self.prefferedClass['cal']='dict'
        self.prefferedClass['mcal'] = 'dict'

    def addIOMap(self,objectInputClassString,formatOutputString,IOSystem):
        '''ptython data types to save-data types always save functions.
        save-data types to python-types are always load functions.
        example numpy to jpeg is save. tiff to numpy is load'''
        if not hasattr(self,'map'):
            self.map=dict()
        if objectInputClassString not in self.map:
            self.map[objectInputClassString]=dict()
        if formatOutputString not in self.map:
            self.map[formatOutputString]=dict()
        self.map[objectInputClassString][formatOutputString]= IOSystem.save
        self.map[formatOutputString][objectInputClassString] = IOSystem.load
    def save(self,key,object):
        if not isinstance(key,str):
            raise TypeError
        if hasattr(object,'properties'):
            object=object.properties
        savingFormat = os.path.splitext(key)[1][1:].strip()
        objectInputClassString=object.__class__.__name__
        self.map[objectInputClassString][savingFormat](key,object)

    def load(self,key,classtype=None):
        if not isinstance(key,str):
            raise TypeError
        if classtype !=None:
            if not isinstance(classtype,str):
                raise TypeError
        fileExtension=os.path.splitext(key)[1][1:].strip()  #gets the file extension string
        if classtype==None:
            classtype=self.prefferedClass[fileExtension]
        loader=self.map[fileExtension][classtype]
        return loader(key)


class DataStorageLocal(iDataManager):
    folder=None
    io=None
    def __init__(self,folder=None):
        self.io=IOManager()
        self.folder = folder
        if folder:
            self.initialize()

    def initialize(self):
        if os.path.exists(self.folder):
            pass
        else:
            os.mkdir(self.folder)
        self._isInitialized = True

    def load(self,key):
        fullPath=os.path.join(self.folder,key)
        value=self.io.load(fullPath)
        return value

    def save(self,key,value):
        fullFilePath = os.path.join(self.folder, key)
        isPathExists=os.path.exists(self.folder)
        if not isPathExists:
            os.mkdir(self.folder)
        print(fullFilePath)
        self.io.save(fullFilePath,value)

    def remove(self,key):
        fullFilePath = os.path.join(self.folder, key)
        os.remove(fullFilePath)
        pass

    def find(self,expression):
        expression=os.path.join(self.folder,expression)
        names=[]
        lenPathSize=len(self.folder)+1
        for filepath in glob.glob(expression):
            filename=filepath[lenPathSize:] # trims the path portion of the path
            names.append(filename)
        return names

class DataStorageRemoteSMB(iDataManager):
    foldername = None
    io = None
    connection=None
    shareName=None
    def __init__(self):
        self._isInitialized=False
        self.connection=None
        self.shareName=None

    def initialize(self,ipAddress, username,password,share,folder):
        if not isinstance(ipAddress,str):
            raise TypeError
        if not isinstance(username,str):
            raise TypeError
        if not isinstance(password,str):
            raise TypeError
        if not isinstance(share,str):
            raise TypeError
        if not isinstance(folder,str):
            raise TypeError
        self.connection = SMBConnection(username, password, 'client', 'server')
        self.connection.connect(ipAddress)
        self.folderName=folder
        self._isInitialized=True

    @property
    def isInitialized(self):
        return self._isInitialized

    def load(self, key):
        self.connection.retrieveFile(service_name=self.shareName,
                                          path=os.path.join(self.folderName,key,'.pkl'))

    def save(self, key, value):
        if self.isInitialized:
            value=self.io.serialize(value)
            fullpath=os.path.join(self.folderName,key,'.pkl')
            self.connection.storeFile(service_name=self.shareName,  # It's the name of shared folder
                             path=fullpath,
                             file_obj=value)
        else:
            raise PermissionError

    def close(self):
        self.connection.close()


class RemoteIOHttps:
    def __init__(self,url=None):
        self.url=url
    def load(self, key):
        total_url = self.url + key
        response = urllib.request.urlopen(total_url)
        data = response.read()
        return data

class DataStorageRemote:
    localStorage=DataStorageLocal(os.path.join('remote'))
    remoteio=RemoteIOHttps(url='http://munsky-nas.engr.colostate.edu/PythonAutomation/')


    def load(self,key):
        if not isinstance(key,str):
            raise TypeError
        try:
            value=self.localStorage.load(key)
        except:
            value=self.remoteio.load(key)
            self.localStorage.save(key,value)
            value=self.localStorage.load(key) #this line reloads data with proper formating (ie NOT BYTES!)
        return value

    def clearcache(self):
        shutil.rmtree(self.localStorage.folder)



class iDataBuilder:
    def load(self,key):
        '''loads data by building it on the fly'''
        pass

class DataBuilder(iDataBuilder):
    def load(self,key):
        if not isinstance(key,str):
            raise TypeError('key must be a string')
        command='self.'+key+'()'
        value=eval(command)
        return value
    def calibration(self):
        return MatrixMultiCalibration()

class DataManager:
    '''Loads an item in a 3 layered process. First from cashe, then from storage, finally makes it'''
    cache=None
    storage=None
    builder=None
    remote=None

    def __init__(self,casheSize=128):
        self.cache=DataManagerCache(casheSize)
        self.storage=DataStorageLocal()
        self.builder=iDataBuilder()
        self.remote=DataStorageRemote()

    def load(self,key):
        if not isinstance(key,str):
            raise TypeError
        try:
            return self.cache.load(key)
        except:
            try:
                value=self.storage.load(key)
                self.cache.save(key,value)
                return value
            except:
                try:
                    value=self.remote.load(key)
                    self.cache.save(key,value)
                    return value
                except:
                    raise KeyError

    def save(self,key,value):
        if not isinstance(key,str):
            raise TypeError
        self.cache.save(key,value)
        self.storage.save(key, value)

    def remove(self,key):
        self.storage.remove(key)
        try:
            self.cache.remove(key)
        except:
            pass

    def find(self,expression):
        names=self.storage.find(expression)
        return names

    @property
    def properties(self):
        props=dict()
        props.update(self.cache.properties)
        props.update(self.storage.properties)
        #props.update(self.builder.properties)
        return props

    def clearCache(self):
        self.cache.clear()
class MultiDataManager:
    '''a structure of multiple data managers for local and remote acess'''
    locations=None
    def __init__(self):
        self.locations=dict()

    def addLocation(self,key,datamanager):
        if not isinstance(key,str):
            raise TypeError
        if not isinstance(datamanager,DataManager):
            raise TypeError
        if key not in self.locations.keys():
            self.locations[key]=datamanager
        else:
            raise KeyError

    def __getitem__(self, key):
        return self.locations[key]

    def __setitem__(self,key,value):
        self.locations[key]=value

    def initialize(self):
        for locale in self.locations:
            self.locations[locale].storage.initialize()

    @property
    def properties(self):
        props=dict()
        for i in range(len(self.locations)):
            localProps=self.locations[i].properties
            for key in localProps.keys():
                props[key+"_"+str(i)]=localProps.pop(key)
        return props
