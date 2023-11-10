import os.path

import source.data_manager as d
import source.acquisition as a
import source.globals as g
import source.human_interface as i
import source.devices as dv
import source.authentication as auth
import source.calibration as c
import time
from datetime import datetime
from source.calibration import MatrixMultiCalibration
from pycromanager import Acquisition
from datetime import datetime
from source.verbosity import Verbosity,ReportFull,ReportSilent
from skimage import io
from source.globals import Globals
from source.hooks import HookSetLibrary
class iBackend:
    '''master control of modules'''
    def setUser(self,username=None,password=None):
        '''sets the current user. seting a user can be done with the interface and changes user related global variables '''
        pass

    def listDevices(self):
        '''lists the active deivece generic types'''
        pass

    def listDevicesAvailable(self):
        '''lists the devices in the library'''
        pass

    def listPortsAvailable(self):
        '''returns the list of avaiable ports as a list and inclused a dummy port'''
        pass

    def addDevice(self,key,port):
        '''adds device from key, and usb port'''
        pass

    def connectDevices(self):
        '''connects ALL devices to the associated port'''
        pass

    def disconnectDevices(self):
        '''diconects all devices at once to the associated port'''
        pass

    def listHardware(self):
        '''list the physical hardware before the abstraciton layer'''
        pass

    def listUsers(self):
        '''list available users'''
        pass


class Backend(iBackend):
    datamanager=None
    acquisition=None
    globals=None
    devices=None
    authentication=None
    calibration=None
    verbosity=None
    image_processor=None
    def __init__(self,config=None,verbosity="full"):
        if config:
            if not isinstance(config,str):
                raise TypeError
        if not config:
            config='config.txt'
        self._initializeGlobalsFromFile(config)
        self._initializeDataManager()
        self._initializeAcquisitionPlugin()
        self._initializeCalibration()
        self._initializeDevices()
        self._initializeAuthentication()
        self._initializeVerbosity(verbosity)


    def _initializeGlobalsFromFile(self,config):
        self.globals=g.Globals(config)

    def _initializeDataManager(self):
        coredata = d.DataManager()
        coredata.cache = d.DataManagerCache()
        coredata.storage = d.DataStorageLocal(folder=self.globals.DATA_CORE_PATH)
        coredata.builder = d.DataBuilder()

        userdata=d.DataManager()
        userdata.cache=d.DataManagerCache()
        userdata.storage=d.DataStorageLocal(folder=self.globals.DATA_USER_PATH)
        userdata.builder=d.DataBuilder()

        acqdata=d.DataManager()
        acqdata.cache = d.DataManagerCache()
        acqdata.storage = d.DataStorageLocal(folder=self.globals. DATA_ACQUISITION_PATH)
        acqdata.builder = d.DataBuilder()

        staged = d.DataManager()
        staged.cache = d.DataManagerCache()
        staged.storage = d.DataStorageLocal(folder=self.globals.DATA_STAGED_PATH)
        staged.builder = d.DataBuilder()

        completed = d.DataManager()
        completed.cache = d.DataManagerCache()
        completed.storage = d.DataStorageLocal(folder=self.globals. DATA_COMPLETED_PATH)
        completed.builder = d.DataBuilder()

        scripts = d.DataManager()
        scripts.cache = d.DataManagerCache()
        scripts.storage = d.DataStorageLocal(folder=self.globals.DATA_SCRIPTS_PATH)
        scripts.builder = d.DataBuilder()

        error = d.DataManager()
        error.cache = d.DataManagerCache()
        error.storage = d.DataStorageLocal(folder=self.globals.DATA_ERROR_PATH)
        error.builder = d.DataBuilder()

        self.datamanager=d.MultiDataManager()
        self.datamanager.addLocation(self.globals.DATAKEY_USERDATA, userdata)
        self.datamanager.addLocation(self.globals.DATAKEY_COREDATA, coredata)
        self.datamanager.addLocation(self.globals.DATAKEY_STAGED,  staged)
        self.datamanager.addLocation(self.globals.DATAKEY_COMPLETED, completed)
        self.datamanager.addLocation(self.globals.DATAKEY_ACQUISITIONDATA, acqdata)
        self.datamanager.addLocation(self.globals.DATAKEY_SCRIPTS, scripts)
        self.datamanager.addLocation(self.globals.DATAKEY_ERROR, error)
        self.datamanager.addLocation(self.globals.DATAKEY_OUTPUT, error)
    def _initializeAcquisitionPlugin(self):
        self.acquisition=a.AcquisitionPlugin()

    def _initializeDevices(self):
        self.devices=dv.ExternalDeviceManager()

    def _initializeAuthentication(self):
        self.authentication=auth.Authentication()
        self.authentication.validator=auth.ValidatorLocal(self.globals.PASS_LOCAL_FILE,self.globals.NAMES_LOCAL_FILE,)

    def _initializeCalibration(self):
        try:
            calibrationProperties=self.datamanager['Core'].load('calibration.mcal')
            self.calibration=MatrixMultiCalibration()
            self.calibration.load(calibrationProperties)
        except:
            calibration=MatrixMultiCalibration()
            self.calibration = calibration
            self.datamanager['Core'].save('calibration.mcal',calibration)
    def _initializeVerbosity(self,verbosity):
        self.verbosity=Verbosity()
        if verbosity=="full":
            self.verbosity.mode=ReportFull()
        if verbosity=="silent":
            self.verbosity.mode=ReportSilent()
        self.verbosity.log.logFileName=os.path.join(self.globals.ROOT_DATA_PATH,self.globals.DATA_FOLDER, self.globals.LOG_HISTORY)


    def listDeviceInterfaces(self):
        list=self.devices.listDeviceInterfaces()
        return list

    def listDeviceHardware(self):
        list=self.devices.listDeviceHardware()
        return list

    def listDevicesAvailable(self):
        list=self.devices.listDevicesAvailable()
        return list

    def listAcquisitionHistory(self):
        file=open(self.verbosity.log.logFileName)
        historyList=[]
        for line in file:
            historyList.append(line.replace('\n',''))
        file.close()
        return historyList

    def addDevice(self,key,port):
        self.devices.addDevice(key,port)
        self.verbosity.add('Device was added {0}:{1}'.format(key,port))
        self.verbosity.print()

    def connectDevices(self):
        self.devices.open()

    def disconnectDevices(self):
        self.devices.close()

    def acquire(self):
        if not isinstance(self.acquisition,a.AcquisitionPlugin):
            raise TypeError
        if self.acquisition.settings.directory==None:
            self.acquisition.settings.directory=self.globals.DATA_ACQUISITION_PATH
        self.acquisition.run()
        self.verbosity.add('Acquisition Complete')
        self.verbosity.print()

    def acquireAndReturnDataset(self):
        if not isinstance(self.acquisition,a.AcquisitionPlugin):
            raise TypeError
        if self.acquisition.settings.directory==None:
            self.acquisition.settings.directory=self.globals.DATA_ACQUISITION_PATH
        dataset=self.acquisition.runAndReturnDataset()
        self.verbosity.add('Acquisition Complete')
        self.verbosity.print()
        return dataset

    def loadImageData(self,key):
        if not isinstance(key,str):
            raise TypeError
        dataHomeFolder = self.datamanager[self.globals.DATAKEY_ACQUISITIONDATA].storage.folder
        listOfData = os.listdir(dataHomeFolder)
        if key not in listOfData:
            raise KeyError
        subfolder = os.path.join(dataHomeFolder, key, "Full resolution")
        contents = os.listdir(subfolder)
        for c in contents:
            if c.endswith(".tif"):
                fullFileName=os.path.join(subfolder,c)
                images = io.imread(fullFileName)
        return images

    def listImageData(self):
        dataHomeFolder=self.datamanager[self.globals.DATAKEY_ACQUISITIONDATA].storage.folder
        listOfData=os.listdir(dataHomeFolder)
        return listOfData

    def loadAcquisition(self,key,*args,**kwargs):
        if not isinstance(key,str):
            raise TypeError
        name,extension=os.path.splitext(key)
        if extension==".acq":
            pluginData=self.datamanager[self.globals.DATAKEY_SCRIPTS].load(key)
            self.acquisition.load(pluginData)
        elif extension==str():
            lib=a.AcquisitionPluginLibrary()
            plugin=lib.get(key,*args,**kwargs)
            self.acquisition = plugin
        else:
            raise KeyError

    def loadStagedAcquisition(self,key):
        if not isinstance(key,str):
            raise TypeError
        try:
            pluginData=self.datamanager[self.globals.DATAKEY_STAGED].load(key)
            self.acquisition.load(pluginData)
        except:
            try:
                lib=a.AcquisitionPluginLibrary()
                plugin=lib.get(key)
                self.acquisition = plugin
            except:
                raise KeyError

    def saveAcquisition(self,filename):
        properties=self.acquisition.properties
        self.datamanager[self.globals.DATAKEY_SCRIPTS].save(filename,properties)

    def stageAcquisition(self,filename,*args,**kwargs):
        if not isinstance(filename,str):
            raise TypeError
        name,extension=os.path.splitext(filename)
        if extension==".acq":
            properties=self.datamanager[self.globals.DATAKEY_SCRIPTS].load(filename)
        if extension==str(): #is an empty string
            lib=a.AcquisitionPluginLibrary()
            acquisition=lib.get(name,*args,**kwargs)
            properties=acquisition.properties
        names=self.listStagedAcquisitions()
        index=0
        isUniqueName=False #assume the name is not unique in order to get into loop
        while not isUniqueName:
            proposalName=name+"_"+str(index)+".acq"
            if proposalName not in names:
                isUniqueName=True
            else:
                index=index+1
        self.datamanager[self.globals.DATAKEY_STAGED].save(proposalName,properties)
        self.verbosity.add("[{0}] {1} was scheduled\n".format(datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),name))
        self.verbosity.print()

    def completeStagedAcquisition(self,acqFile):
        name,ext=os.path.splitext(acqFile)
        self.loadStagedAcquisition(acqFile)
        self.acquisition.settings.name=name
        self.acquisition.settings.directory=self.globals.DATA_ACQUISITION_PATH
        self.acquire()
        finishedAcqusitionFileName=name+'_finished.acq'
        finshedFileNames=self.datamanager[self.globals.DATAKEY_COMPLETED].find('*.acq')
        isInFileNames=True
        index=0#initialize as true to get in loop
        while isInFileNames:
            if finishedAcqusitionFileName in finshedFileNames:
                finishedAcqusitionFileName=name+'_finished_'+str(index)+'.acq'
                index = index + 1
            else:
                isInFileNames=False
        self.saveCompletedAcquisition(finishedAcqusitionFileName)
        self.datamanager[self.globals.DATAKEY_STAGED].remove(acqFile)
        self.saveAcquisitionOutput(name)
        self.verbosity.add("[{0}] {1} was completed\n", datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), name)
        self.verbosity.print()

    def tryCompleteStagedAcquisition(self,name):
        self.connectDevices()
        try:
            self.completeStagedAcquisition(name)
        except RuntimeError:
            self.verbosity.add("[{0}] {1} has failed\n", datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), name)
            self.verbosity.print()
            self.moveFailedAcqusition(name)
        self.disconnectDevices()

    def tryCompleteAllStagedAcquisitions(self):
        names =self.listStagedAcquisitions()
        for name in names:
            self.tryCompleteStagedAcquisition(name)
            time.sleep(2.)

    def saveCompletedAcquisition(self,filename):
        properties = self.acquisition.properties
        self.datamanager[self.globals.DATAKEY_COMPLETED].save(filename, properties)


    def setUser(self,username,password):
        if not isinstance(username,str):
            return TypeError
        if not isinstance(password,str):
            return TypeError
        self.authentication.validate(username, password)
        self.authentication.setUser(username)
        self.globals.configureUser(username)
        g=self.globals


        self.datamanager[self.globals.DATAKEY_USERDATA].storage.folder = os.path.join(g.ROOT_DATA_PATH, g.DATA_FOLDER,g.DATA_USER_FOLDER, username)
        self.datamanager[self.globals.DATAKEY_USERDATA].storage.folder=os.path.join(g.ROOT_DATA_PATH,g.DATA_FOLDER,g.DATA_USER_FOLDER,username)
        self.datamanager[self.globals.DATAKEY_STAGED].storage.folder = os.path.join(g.ROOT_DATA_PATH,g.DATA_FOLDER, g.DATA_USER_FOLDER, username,g. DATA_STAGED_FOLDER)
        self.datamanager[self.globals.DATAKEY_ACQUISITIONDATA].storage.folder = os.path.join(g.ROOT_DATA_PATH,g.DATA_FOLDER, g.DATA_USER_FOLDER, username,g.DATA_ACQUISITION_FOLDER)
        self.datamanager[self.globals.DATAKEY_COMPLETED].storage.folder = os.path.join(g.ROOT_DATA_PATH,g.DATA_FOLDER, g.DATA_USER_FOLDER, username,g. DATA_COMPLETED_FOLDER)
        self.datamanager[self.globals.DATAKEY_SCRIPTS].storage.folder = os.path.join(g.ROOT_DATA_PATH,g.DATA_FOLDER, g.DATA_USER_FOLDER, username,g.DATA_SCRIPTS_FOLDER)
        self.datamanager[self.globals.DATAKEY_ERROR].storage.folder = os.path.join(g.ROOT_DATA_PATH,g.DATA_FOLDER, g.DATA_USER_FOLDER,username, g.DATA_ERROR_FOLDER)
        self.datamanager[self.globals.DATAKEY_OUTPUT].storage.folder = os.path.join(g.ROOT_DATA_PATH, g.DATA_FOLDER,g.DATA_USER_FOLDER, username,g.DATA_OUTPUT_FOLDER)
        paths=[self.datamanager[self.globals.DATAKEY_USERDATA].storage.folder,self.datamanager[self.globals.DATAKEY_STAGED].storage.folder,
               self.datamanager[self.globals.DATAKEY_ACQUISITIONDATA].storage.folder, self.datamanager[self.globals.DATAKEY_COMPLETED].storage.folder,
               self.datamanager[self.globals.DATAKEY_SCRIPTS].storage.folder,self.datamanager[self.globals.DATAKEY_ERROR].storage.folder,
               self.datamanager[self.globals.DATAKEY_OUTPUT].storage.folder]
        for path in paths:
            isFolderExist=os.path.exists(path)
            if not isFolderExist:
                os.mkdir(path)

    def newUser(self,username,password):
        self.authentication.newUser(username,password)

    def listUser(self):
        return self.authentication.username

    def listUsers(self):
        return self.authentication.listUsers()

    def listPortsAvailable(self):
        return self.devices.listPortsAvailable()

    @property
    def properties(self):
        props=dict()
        props.update(self.datamanager.properties)
        props.update(self.acquisition.properties)
        props.update(self.devices.properties)
        props.update(self.globals.properties)

    def listAvailableAcquisitions(self):
        names=[]
        lib = a.AcquisitionPluginLibrary()
        names.extend(lib.list())
        names.extend(self.datamanager[self.globals.DATAKEY_SCRIPTS].find('*.acq'))
        return names

    def listStagedAcquisitions(self):
        names=[]
        names.extend(self.datamanager[self.globals.DATAKEY_STAGED].find('*.acq'))
        return names

    def listCompletedAcqusititions(self):
        names = []
        names.extend(self.datamanager[self.globals.DATAKEY_COMPLETED].find('*.acq'))
        return names

    def listAquisitionHisory(self):
        file=self.verbosity.log.logFileName
        return file.read()

    def clearAllStagedAcquisitions(self):
        names=self.listStagedAcquisitions()
        for name in names:
            self.datamanager[self.globals.DATAKEY_STAGED].remove(name)


    def saveConfiguration(self,name):
        configuration=self.devices.configuration
        self.datamanager[self.globals.DATAKEY_COREDATA].save(name,configuration)

    def loadConfiguration(self,key):
        configuration=self.datamanager[self.globals.DATAKEY_COREDATA].load(key)
        self.devices.loadConfiguration(configuration)

    def listConfigurations(self):
        configurations=self.datamanager[self.globals.DATAKEY_COREDATA].find('*.cfg')
        return configurations

    def moveFailedAcqusition(self,filename):
        name,extension=os.path.splitext(filename)
        acq=self.datamanager[self.globals.DATAKEY_STAGED].load(filename)
        names=self.listFailedAcquisitions()
        isNameUnique=False
        index=0
        while not isNameUnique:
            proposalName=name+"_"+str(index)+".acq"
            if proposalName not in names:
                newfilename=proposalName
                break
            else:
                index=index+1
        self.datamanager[self.globals.DATAKEY_ERROR].save(newfilename,acq)
        self.datamanager[self.globals.DATAKEY_STAGED].remove(filename)


    def listFailedAcquisitions(self):
        names=self.datamanager[self.globals.DATAKEY_ERROR].find('*.cfg')
        return names

    def saveAcquisitionOutput(self,name):
        if not isinstance(name,str):
            raise TypeError
        splitName,extension=os.path.splitext(name)
        if extension==str():
            name=name+'.acq'
        self.datamanager[self.globals.DATAKEY_OUTPUT].save(name,self.acquisition.output)

    def listOutputs(self):
        names=self.datamanager[self.globals.DATAKEY_OUTPUT].find('*.acq')
        return names

    def loadOutput(self,filename):
        output=self.datamanager[self.globals.DATAKEY_OUTPUT].load(filename)
        return output

    def clearCache(self):
        self.datamanager[self.globals.DATAKEY_USERDATA].clearCache()
        self.datamanager[self.globals.DATAKEY_COREDATA].clearCache()
        self.datamanager[self.globals.DATAKEY_STAGED].clearCache()
        self.datamanager[self.globals.DATAKEY_ACQUISITIONDATA].clearCache()
        self.datamanager[self.globals.DATAKEY_COMPLETED].clearCache()
        self.datamanager[self.globals.DATAKEY_SCRIPTS].clearCache()
        self.datamanager[self.globals.DATAKEY_ERROR].clearCache()
        self.datamanager[self.globals.DATAKEY_OUTPUT].clearCache()

    def scheduleCurrentAcquisitionAs(self,filename):
        names=self.listStagedAcquisitions()
        name,extension=os.path.splitext(filename)
        isUniqueName = False  # assume the name is not unique in order to get into loop
        index=0
        while not isUniqueName:
            proposalName = name + "_" + str(index) + ".acq"
            if proposalName not in names:
                isUniqueName = True
            else:
                index = index + 1
        properties = self.acquisition.properties
        self.datamanager[self.globals.DATAKEY_STAGED].save(filename, properties)

    def addHookFunctionality(self,key,*args,**kwargs):
        if not isinstance(key,str):
            raise TypeError
        lib=HookSetLibrary()
        hooks=lib.get(key,*args,**kwargs)
        self.acquisition.hooks.link(hooks)


class Environment:
    interface=None
    backend=None
    def __init__(self,config):
        self.interface=i.HumanInterfaceFactoryHeadless()
        self.backend=Backend(config)

    def menu(self):
        response=self.interface.menu()
        response=int(response)
        if response==1:
            self.login()
        elif response==2:
            self.newUser()
        elif response == 3:
            return

    def login(self):
        try:
            (username,password)=self.interface.menuLogin()
            if username==str(): #empty username
                self.menu()
            self.backend.setUser(username,password)
        except PermissionError:
            self.interface.menuLoginFailed()
            self.login()
        self.selection()

    def newUser(self):
        (username,password)=self.interface.menuNewUser()
        if username not in self.backend.listUsers():
            self.backend.newUser(username,password)
        self.backend.setUser(username,password)
        self.selection()

    def selection(self):
        response=self.interface.menuSelection()
        response=int(response)
        if response==1:
            self.editHardware()
        elif response==2:
            self.editAcquisitionEvents()
        elif response==3:
            self.editAcquisitionHooks()
        elif response==4:
            self.editAcquisitionSettings()
        elif response==5:
            self.loadAcquisition()
        elif response==6:
            self.saveAcquisition()
        elif response==7:
            self.stageAcqusition()
        elif response==8:
            self.acquire()
        elif response==9:
            self.acquisitionLoop()
        elif response==10:
            return None
        self.selection()

    def editHardware(self):
        response=self.interface.menuEditHardwareSettings()
        response=int(response)
        if response==1:
            self.listDevicesAvailable()
        if response==2:
            self.listDeviceInterfaces()
        if response==3:
            self.listDeviceHardware()
        if response==4:
            self.addDevice()
        if response==5:
            self.removeDevice()
        if response==6:
            self.selection()
        self.editHardware()

    def editAcquisitionEvents(self):
        properties=self.backend.acquisition.events.properties
        self.interface.menuEditAcquisitionEvents(properties)

    def editAcquisitionHooks(self):
        lib=a.AcquisitionHookLibrary()
        names=lib.list()
        self.interface.menuEditAcquisitionHooks(names)

    def editAcquitisionSettings(self):
        properties = self.backend.acquisition.events.properties
        self.interface.menuEditAcquisitionSettings(properties)

    def listDevicesAvailable(self):
        list = self.backend.listDevicesAvailable()
        self.interface.menuListDevicesAvailable(list)


    def listDeviceInterfaces(self):
        list = self.backend.listDeviceInterfaces()
        self.interface.menuListDeviceInterfaces(list)

    def listDeviceHardware(self):
        list = self.backend.listDeviceHardware()
        self.interface.menuListDeviceHardware(list)

    def editAcquisitionSettings(self):
        # OPtions [change acquisition settings, load acquisition, save acquisition]
        settings=self.backend.acquisition.properties
        response=self.interface.menuEditAcquisitionSettings(settings)
        response=int(response)
        if response==1:
            self.changeAcquisitionSettingsKeyValue()
        if response==2:
            self.loadAcquisition()
        if response==3:
            self.saveAcquisition()
        self.editAcquisitionSettings()

    def acquire(self):
        self.backend.acquire()

    def loadAcquisition(self):
        lib = a.AcquisitionPluginLibrary()
        names=lib.list()
        names.extend(self.backend.datamanager[self.backend.globals.DATAKEY_SCRIPTS].find('*.acq'))
        indexChosen=self.interface.menuLoadAcquisition(names)
        chosenName=names[indexChosen-1]
        self.backend.loadAcquisition(chosenName)

    def saveAcquisition(self):
        saveName=self.interface.menuSaveAcquisition()
        name,extension=os.path.splitext(saveName)
        if not ((extension=='.acq') or (extension=='')):
            raise KeyError
        if extension=='':
            name=name+'.acq'
        self.backend.saveAcquisition(name)

    def changeAcquisitionSettingsKeyValue(self):
        (key,value)=self.interface.menuEditAcquisitionSettings()
        self.backend.acquisition.set(key,value)

    def addDevice(self):
        listDevices=self.backend.listDevicesAvailable()
        listPorts=self.backend.listPortsAvailable()
        (deviceName,portName)=self.interface.menuAddDevice(listDevices,listPorts)
        self.backend.addDevice(deviceName,portName)

    def saveAcquisitionSettings(self):
        filename=self.interface.menuSaveAcquisitionSettings()
        self.backend.saveAcquisition(filename)

    def stageAcqusition(self):
        acquisitions=self.backend.listAvailableAcquisitions()
        chosenFilename=self.interface.menuStageAcquisition(acquisitions)
        self.backend.stageAcquisition(chosenFilename)

    def acquisitionLoop(self,maxIter=None):
        self.interface.menuAcquisitionLoopReminder()
        if maxIter==None:
            maxIterations=10000
        else:
            maxIterations=maxIter
        numLoopTimes=0
        while numLoopTimes<maxIterations:
            time.sleep(2)
            names = self.backend.listStagedAcquisitions()
            names=sorted(names)
            #print("[{0}] {1} acqusitions were found and scheduled".format(datetime.now(), len(names)))
            for name in names:
                self.backend.connectDevices()
                time.sleep(1)
                try:
                    self.backend.completeStagedAcquisition(name)
                    self.interface.menuCompleteStagedAcquisition(name)
                except RuntimeError as e:
                    self.interface.menuMoveFailedAcqusition(name)
                    #print(e)
                    self.backend.moveFailedAcqusition(name)
                self.backend.disconnectDevices()
                time.sleep(1)
            numLoopTimes=numLoopTimes+1
            if maxIter==None:
                numLoopTimes=0

    def acquisitionLoopWithBreak(self,maxIter=None):
        self.interface.menuAcquisitionLoopReminder()
        globals=g.Globals()
        globals.ACQUISITION_IS_IN_LOOP=True
        if maxIter==None:
            maxIterations=10000
        else:
            maxIterations=maxIter
        numLoopTimes=0
        while (numLoopTimes<maxIterations):
            time.sleep(2)
            names = self.backend.listStagedAcquisitions()
            names=sorted(names)
            if "stop.acq" in names:
                break
            #print("[{0}] {1} acqusitions were found and scheduled".format(datetime.now(), len(names)))
            for name in names:
                self.backend.connectDevices()
                time.sleep(1)
                try:
                    self.backend.completeStagedAcquisition(name)
                    self.interface.menuCompleteStagedAcquisition(name)
                    isComplete=True
                except RuntimeError as e:
                    self.interface.menuMoveFailedAcqusition(name)
                    #print(e)
                    self.backend.moveFailedAcqusition(name)
                self.backend.disconnectDevices()
                time.sleep(1)

            numLoopTimes=numLoopTimes+1
            if maxIter==None:
                numLoopTimes=0

    def stopAllLoops(self):
        globals = g.Globals()
        globals.ACQUISITION_IS_IN_LOOP = False

    def loadConfiguration(self,configFileName=None):
        if configFileName:
            self.backend.loadConfiguration(configFileName)
        else:
            names=self.backend.listConfigurations()
            chosenConfiguration=self.interface.menuLoadConfiguration(names)
            self.backend.loadConfiguration(chosenConfiguration)

    def loadImageData(self,name):
        if not isinstance(name,str):
            raise TypeError
        self.backend.loadImageData(name)



class EnvironmentBuilder:
    '''This class build different kinds of main scrips. Initialization is always the same.'''
    environment=None
    interface=None
    def __init__(self):
        self.environment=Environment(config='config.txt')
        if 'default' not in self.environment.backend.authentication.listUsers():
            self.environment.backend.authentication.newUser('default', '')
        self.environment.backend.setUser('default','')

    def setRootDataPath(self, path):
        self.environment.backend.globals.ROOT_DATA_PATH=path

    def setInterface(self, key):
        if not isinstance(key,str):
            raise TypeError
        guiKeys=['gui','GUI','Gui','g']
        headlessKeys=['headless','Headless','HEADLESS','head-less','Head-Less','HEAD-LESS','Head-less',
                      'nogui','no-gui','Nogui','NoGui','No-Gui','No-gui']
        if key in guiKeys:
            self.environment.interface=i.HumanInterfaceFactoryGui()
        elif key in headlessKeys:
            self.environment.interface=i.HumanInterfaceFactoryHeadless()
        else:
            raise KeyError

    def setAuthentication(self,key):
        globals=g.Globals()
        if not isinstance(key,str):
            raise TypeError
        if key in ['local','Local','LOCAL','l','L']:
            self.authentication=auth.Authentication()
            self.authentication.validator=auth.ValidatorLocal(globals.PASS_LOCAL_FILE,globals.NAMES_LOCAL_FILE)
        elif key in ['nopass','NoPass','NOPASS','nopassword','NoPassword','NOPASSWORD','N','n']:
            self.authentication = auth.Authentication()
            self.authentication.validator = auth.ValidatorNoPassword()
        else:
            raise KeyError

    def getEnvironment(self):
        return self.environment

    def setUser(self,user,passwd):
        self.environment.backend.setUser(user,passwd)

    def setConfiguration(self,configFileName):
        self.environment.loadConfiguration(configFileName=configFileName)
    def clearAcquisitionCache(self):
        self.environment.backend.clearCache()
        self.environment.backend.clearAllStagedAcquisitions()


class StageBoundaries:
    boundary=[None,None,None]
    def bound(self,positionList):
        if not isinstance(positionList,list):
            raise TypeError

        for position in positionList:
            for index in range(len(position)):
                if self.boundary[index] is not None:
                    boundary=self.boundary[index]
                    if position[index]<boundary[0]:
                        self.boundary=boundary[0]
                    if position[index]>boundary[1]:
                        self.boundary=boundary[1]
    def checkIsBounded(self,positionList):
        isBounded=True
        for position in positionList:
            for index in range(len(position)):
                if self.boundary[index] is not None:
                    boundary=self.boundary[index]
                    if position[index]<boundary[0]:
                        isBounded=False
                    if position[index]>boundary[1]:
                        isBounded=False
        return isBounded
    def setXboundary(self,bounds):
        if not isinstance(bounds,(list,tuple)):
            raise TypeError
        if not len(bounds)==2:
            raise ValueError
        self.boundary[0]=bounds
    def setYboundary(self,bounds):
        if not isinstance(bounds,(list,tuple)):
            raise TypeError
        if not len(bounds)==2:
            raise ValueError
        self.boundary[1]=bounds
    def setZboundary(self,bounds):
        if not isinstance(bounds,(list,tuple)):
            raise TypeError
        if not len(bounds)==2:
            raise ValueError
        self.boundary[2]=bounds

def BackendAsynchronousAPI(Backend):
    pass