import os
import serial
import globals as g
from serial.tools import list_ports
from calibration import MatrixCalibration
import numpy as np
class iSerial:
    '''defines functions for connecting to serial port. Serials must also be singletons!'''
    def open(self):
        '''opens the port for serial communication'''
        pass

    def close(self):
        '''closes the port for serial communication'''
        pass

    def writeCmd(self,command):
        '''sends command, returns reply.'''
        pass

class iSerialCommandBuffer:
    def put(self,command):
        '''puts things into the command buffer'''
        pass
    def get(self):
        '''gets the oldest item in the buffer'''
        pass


class iCameraDevice(iSerial):
    '''defines camera interface'''
    def snap(self):
        '''acquires image'''
        pass
    def setMode(self,mode):
        '''sets the mode of the camera Free/TTL/ETC'''
        pass


class iFilterWheelDevice(iSerial):
    '''defines interface for a FilterWheel'''
    def swap(self,index):
        '''changes to filter wheel position index'''
        pass


class iLaserDevice(iSerial):
    '''extends devices to include laser interface'''
    def getIdentification(self):
        '''Identifies the device. Who are you? returns highly identifying string'''
        raise AttributeError
        pass
    def reset(self):
        '''resets the laser'''
        pass
    def getMode(self):
        '''gets the laser mode. Digital/Analog'''
        pass
    def getWavelength(self):
        '''Gets laser wavelength'''
        pass
    def getPowerRatingInWatts(self):
        '''gets the power usage in Watts'''
        pass
    def getMinimumPowerInWatts(self):
        '''returns minimum power possible'''
        pass
    def getMaximumPowerInWatts(self):
        '''returns maximum power possible'''
        pass
    def setLaserAutoStart(self,setting):
        '''Sets Laser autostart'''
        pass

    def getFaults(self):
        '''returns laser fault code'''
        pass
    def getTemperatureInC(self):
        '''returns laster temp in C'''
        pass
    def getInterlockStatus(self):
        '''is the metal thingy blocking the laser open'''
        pass
    def setOperatingMode(self,setting):
        '''set the operating mode'''
        pass
    def getOperatingMode(self):
        '''get operating mode'''
        pass
    def setLaserState(self,setting):
        '''set laster status'''
        pass
    def getLaserState(self):
        '''get laster status'''
        pass
    def setLaserPowerInWatts(self,setting):
        '''set laser power'''
        pass
    def getLaserPowerInWatts(self):
        '''get laser power'''
        pass
    def presentOutputPower(self):
        '''????????'''
        pass


class iGalvoDevice(iSerial):
    '''extends devices to include galvo interface'''
    def move(self,xy):
        '''moves the galvo position. xy is a list'''
        pass
    def zap(self,xy,time):
        '''zaps the galvo position for time t. xy is a list'''
        pass
    def cut(self,xy1,xy2):
        '''zaps the galvo position for time t. xy is a list'''
        pass

    def setLaserState(self,state):
        '''sets ON/OFF'''
        pass


class iStageDevice(iSerial):
    '''extends devices to include stage interface'''
    def setXY(self,x,y):
        '''moves the stage'''
        pass
    def getXY(self):
        '''returns the stage position'''
        pass


class iZStageDevice(iSerial):
    def setZ(self,z):
        '''moves the Z position'''
        pass
    def getZ(self):
        '''returns the Z position'''
        pass


class iPiezoStageDevice(iSerial):
    '''a piezo z stage'''
    def setF(self,f):
        '''sets the peizo-z (f)'''
        pass
    def getF(self):
        '''returns f'''
        pass


class iStateDevice(iSerial):
    def setState(self,state):
        '''sets the state of the arduino'''
        pass

    def getState(self):
        '''gets the current State'''
        pass

    def listStates(self):
        '''lists possible states'''
        pass


class iExternalDeviceManager:
    '''a set of devices for outside-of-pycromanager control'''
    def addDevice(self,type,device):
        '''Adds a new device to the devices of type'''
        pass


class iDeviceLibrary:
    def get(self,key):
        '''returns (serial,device) tuple for a particular device key. If port is given, it will make it for that port.
        DeviceLibrary is also responsible for loading the correct port settings for a particular device. The keys are
        highly specific to an exact device than an arbitrary device'''
        pass

    def listCameraDevices(self):
        '''returns a list of keys related to all cameras'''
        pass

    def listLaserDevices(self):
        '''returns a list of keys related to all Lasers'''
        pass

    def listFilterWheelDevices(self):
        '''returns a list of keys related to all FilterWheels'''
        pass

    def listStageDevices(self):
        '''returns a list of keys related to all XYStages'''
        pass

    def listZStageDevices(self):
        '''returns a list of keys related to all ZStageDevices'''
        pass

    def listPiezoStageDevices(self):
        '''returns a list of keys related to all PiezoStageDevices'''
        pass

    def listStateDevices(self):
        '''returns a list of keys related to all Arduino Devices'''
        pass


class Serial(iSerial):
    port=None

    def __init__(self,port,baud=19200,bytesize=8,parity='N',stopbits=1, xonxoff=False,timeout=0.005,
                 write_timeout=0.005,isDebug=False,isDummy=False):
        self.isDebug=isDebug
        self.isDummy=isDummy
        self.port=port
        self.baud=baud
        self.bytesize=bytesize
        self.parity=parity
        self.stopbits=stopbits
        self.xonxoff=xonxoff
        self.timeout=timeout
        self.write_timeout=write_timeout
        self.serial=None

    def open(self):
        if not self.isDummy:
            self.serial = serial.Serial(self.port, baudrate=self.baud, bytesize=self.bytesize, timeout=self.timeout,
                                        parity=self.parity,stopbits=self.stopbits, xonxoff=self.xonxoff,
                                        write_timeout=self.write_timeout)
            self.serial.flush()

    def close(self):
        if not self.isDummy:
            self.serial.close()

    def writeCmd(self,command):
        if not self.isDummy:
            serialCommand=command+os.linesep
            self.serial.write(serialCommand.encode())
            echo=self.serial.readline()
            echo = echo.decode('utf-8')
            return echo
        else:
            return


class LaserDevice_Coherent:
    serial=None
    def __init__(self,serial=None):
        self.serial=serial

    def open(self):
        if self.serial is not None:
            self.serial.open()

    def close(self):
        if self.serial is not None:
            self.serial.close()

    def writeCmd(self,command):
        if not isinstance(command,str):
            raise TypeError('must be a string')
        if self.serial is not None:
            self.serial.writeCmd(command)

    def getIdentification(self):
        """ Gets the laser's identification string """
        fullresp = self.writeCmd('*IDN?')
        # The SCPI protocol provides a method to communicate with multiple
        # virtual devices within an instrument.
        # SCPI channel selection is performed by appending a numeric suffix to the
        # base word in any command string. When the numeric suffix is left off or
        # has a value of zero, the command refers to the first connected device.
        # For example, *idn?* and *idn0? query strings both refer to the first
        # connected device.
        resp = fullresp
        return resp

    def reset(self):
        """ Causes a device to warm boot if implemented """
        fullresp = self.writeCmd('*RST')
        resp = fullresp
        return resp

    def getModel(self):
        """ Retrieves the model name of the laser """
        fullresp = self.writeCmd('SYSTem1:INFormation:MODel?')
        resp = fullresp
        return resp

    def getWavelength(self):
        """ Retrieves the wavelength of the laser """
        fullresp = self.writeCmd('SYSTem:INFormation:WAVelength?')
        resp = fullresp
        return resp

    def getPowerRatingInWatts(self):
        """ Retrieves the power (mW) rating of the laser """
        fullresp = self.writeCmd('SYSTem:INFormation:POWer?')
        resp = fullresp
        if resp is not None:
            return float(resp)

    def getMinimumPowerInWatts(self):
        """Returns the minimum CW laser output power in (mW)"""
        fullresp = self.writeCmd('SOURce:POWer:LIMit:LOW?')
        resp = fullresp
        if resp is not None:
            return float(resp)

    def getMaximumPowerInWatts(self):
        """Returns the maximum CW laser output power in (mW)"""
        fullresp = self.writeCmd('SOURce:POWer:LIMit:HIGH?')
        resp = fullresp
        if resp is not None:
            return float(resp)

    def setLaserAutoStart(self, cmd):
        ''' Enables or disables the laser Auto Start feature. Setting is saved in persistent memory.
        The factory default is OFF. If the laser is connected to a OBIS Remote, this setting is overriden by the
        hardware switch of the min-controller '''

        fullresp = self.writeCmd('SYSTem1:AUTostart ' + cmd)  # cmd = ON|OFF
        resp = fullresp
        return resp

    def getState(self):
        """ Queries the system status """
        fullresp = self.writeCmd('SYSTem:STATus?')
        resp = fullresp
        return resp

    def getFaults(self):
        """ Queries current system faults """
        fullresp = self.writeCmd('SYSTem:FAULt?')
        resp = fullresp
        return resp

    def getTemperatureInC(self):
        """ Returns the present laser base plate temperature """
        fullresp = self.writeCmd('SOURce:TEMPerature:BASeplate?')
        resp = fullresp
        return resp

    def getInterlockStatus(self):
        """ Returns the status of the system interlock """
        fullresp = self.writeCmd('SYSTem:LOCK?')
        resp = fullresp
        return resp

    # ===== Laser Operating Mode Selection =====
    # Seven mutually exclusive operating modes are available:
    # - CWP (continuous wave, constant power)
    # - CWC (continuous wave, constant current)
    # - DIGITAL (CW with external digital modulation)
    # - ANALOG (CW with external analog modulation)
    # - MIXED (CW with external digital + analog modulation)
    # - DIGSO (External digital modulation with power feedback) Note: This
    # operating mode is not supported in some device models.
    # - MIXSO (External mixed modulation with power feedback) Note: This
    # operating mode is not supported in some device models.
    # The exact meaning of the selected mode is device-dependent.

    def setOperatingMode(self, cmd):
        '''cmd = CWP|CWC :                         Sets the laser operating mode to internal CW and deselects external modulation. The default setting is CW with constant power or CWP.
           cmd = DIGital|ANALog|MIXed|DIGSO|MIXSO: Sets the laser operating mode to CW constant current modulated by one or more external sources. MIXED source combines both external digital and external analog modulation.
        The setting is saved in non-volatile memory '''
        if cmd == 'CWP' or cmd == 'CWC':
            fullresp = self.writeCmd('SOURce:AM:INTernal ' + cmd)
        else:
            fullresp = self.writeCmd('SOURce:AM:EXTernal ' + cmd)
        resp = fullresp
        return resp

    def getOperatingMode(self):
        ''' Queries the current operating mode of the laser.  '''
        fullresp = self.writeCmd('SOURce:AM:SOURce?')
        resp = fullresp
        return resp

    def setLaserState(self, state):
        ''' Turns the laser ON or OFF. When turning the laser ON, actual laser
        emission may be delayed due to internal circuit stabilization logic and/or
        CDRH delays.   '''
        ioMap=dict()
        if state in [1,'on','On','ON']:
            state='ON'
        elif state in [0,'off','Off','OFF']:
            state='OFF'
        fullresp = self.writeCmd('SOURce:AM:STATe ' + state)  # cmd = ON|OFF
        resp = fullresp
        return resp

    def getLaserState(self):
        ''' Queries the current laser emission status.  '''
        fullresp = self.writeCmd('SOURce:AM:STATe?')
        resp = fullresp
        return resp

    def setLaserPowerInWatts(self, value):
        ''' Sets present laser power level (mW). Setting power level does not turn
        the laser on.    '''
        fullresp = self.writeCmd('SOURce:POWer:LEVel:IMMediate:AMPLitude ' + str(value / 1000))
        resp = fullresp
        return resp

    def getLaserPowerInWatts(self):
        ''' Gets laser power setting level (mW)'''
        fullresp = self.writeCmd('SOURce:POWer:LEVel:IMMediate:AMPLitude?')
        resp = fullresp
        return resp

    def presentOutputPower(self):
        """ Returns the present output power of the laser (mW)"""
        fullresp = self.writeCmd('SOURce:POWer:LEVel?')
        resp = fullresp
        return resp


class LaserDevice_Vortran():
    '''implements interface of a laser using Vortran. Also has a help function'''
    def __init__(self,serial=None):
        self.serial=serial
    def open(self):
        self.serial.open()

    def close(self):
        self.serial.close()

    def writeCmd(self,command):
        self.serial.writeCmd(command)

    def getIdentification(self):
        resp = self.writeCmd('?SFV')
        return resp

    def reset(self):
        pass

    def getModel(self):
        resp = self.writeCmd('?SPV')
        return resp

    def getWavelength(self):
        resp = self.writeCmd('?LW')
        return resp

    def getPowerRatingInWatts(self):
        resp = self.writeCmd('?RP')
        return resp

    def getMinimumPowerInWatts(self):
        return '0'

    def getMaximumPowerInWatts(self):
        resp = self.writeCmd('?MAXP')
        return resp

    def setLaserAutoStart(self, cmd):
        # todo
        pass


    def getFaults(self):
        resp = self.writeCmd('?FC')
        return resp

    def getTemperatureInC(self):
        resp = self.writeCmd('?OBT')
        return resp

    def getInterlockStatus(self):
        '''is the interlock open'''
        resp = self.writeCmd('?IL')
        return resp

    def setOperatingMode(self, value):
        '''sets as Power control or current control (1=current control)'''
        possibleValues=[0, 1]
        if value in possibleValues:
            resp = self.writeCmd('C ' + str(value))
            return resp
        else:
            return TypeError

    def getOperatingMode(self):
        resp = self.writeCmd('?C')
        return resp

    def setLaserState(self, state):
        '''Laser emisssion On/off'''
        if state in [1,'on','On','ON']:
            state=1
        elif state in [0,'off','Off','OFF']:
            state=0
        else:
            raise KeyError
        resp = self.writeCmd('LE ' + str(state))
        return resp

    def getLaserState(self):
        resp = self.writeCmd('?LE')
        return resp

    def setLaserPowerInWatts(self, value):
        resp = self.writeCmd('LP '+ str(value))
        return resp

    def getLaserPowerInWatts(self):
        resp = self.writeCmd('?LP')
        return resp

    def presentOutputPower(self):
        pass

    def help(self):
        resp = self.writeCmd('?H')
        return resp



class DemoCamera(iCameraDevice):
    def __init__(self,serial=None):
        self.serial=serial
        self.mode='TTL'

    def getIdentification(self):
        return 'DemoCamera'
    def reset(self):
        pass
    def getMode(self):
        return self.mode


class DemoLaser(iLaserDevice):
    def __init__(self, serial=None):
        self.serial = serial
    def getIdentification(self):
        return 'DemoLaser'
    def getModel(self):
        return 'DemoLaser'

class DemoFilterWheel(iFilterWheelDevice):
    def __init__(self, serial=None):
        self.serial = serial

class DemoStage(iStageDevice):
    def __init__(self, serial=None):
        self.serial = serial
    def setXY(self,x,y):
        self.x=x
        self.y=y
    def getXY(self):
        return (self.x,self.y)

class DemoZStage(iZStageDevice):
    def __init__(self, serial=None):
        self.serial = serial
        self.z=0
    def setZ(self,z):
        self.z=z
    def getZ(self):
        return self.z

class DemoPiezoStage(iPiezoStageDevice):
    def __init__(self, serial=None):
        self.serial = serial
        self.f=0
    def setF(self,f):
        self.f=f
    def getF(self):
        return self.f

class DemoXYZFStage(iStageDevice,iZStageDevice,iPiezoStageDevice):
    def __init__(self):
        self.x = None
        self.y = None
        self.z = None
        self.f = None
    def setXY(self,x,y):
        self.x=x
        self.y=y
    def getXY(self):
        return (self.x,self.y)
    def setZ(self,z):
        self.z=z
    def getZ(self):
        return self.z
    def setF(self,f):
        self.f=f
    def getF(self):
        return self.f

class DemoStateDevice(iStateDevice):
    def __init__(self, serial=None):
        self.serial = serial
        self.state=[]

    def setState(self,state):
        self.state=state

    def getState(self):
        return self.state

class DemoArduino(iStateDevice):
    def __init__(self, serial=None):
        self.serial = serial

    def setState(self, state):
        self.state = state

    def getState(self):
        return self.state

class TSLabArduino(iStateDevice):
    def __init__(self, serial=None):
        self.serial = serial
        self.state=None

    def open(self):
        self.serial.open()
    def close(self):
        self.serial.close()
    def writeCmd(self,command):
        self.serial.writeCmd(command)

    def setState(self, state):
        if not isinstance(state,list):
            raise TypeError
        if len(state) !=4:
            raise ValueError

        cmd='M '+str(state[0])+' '+str(state[1])+' '+str(state[2])+' '+str(state[3])
        self.serial.writeCmd(cmd)
        self.state=state

    def getState(self):
        return self.state

class TSLabGalvo(iGalvoDevice):
    serial=None
    calibration=None
    def __init__(self,serial=None):
        self.serial = serial
        self.calibration=MatrixCalibration(matrix=np.array([[7.69,0],[0,7.69]]),zero=np.array([512/2,512/2]))
    def open(self):
        self.serial.open()
    def close(self):
        self.serial.close()
    def writeCmd(self,command):
        self.serial.writeCmd(command)

    def zap(self,xy,time_Ms):
        if len(xy)!=2:
            raise TypeError('xy should be a length 2 list/tuple of ints')
        if (not isinstance(xy[0],int)) or (not isinstance(xy[1],int)):
            raise TypeError('xy should be a length 2 list/tuple of ints')
        if not isinstance(time_Ms,(int,float)):
            raise TypeError('time should be an int or float')
        xy=self.calibration.map(np.array(xy))
        xy=np.round(xy)
        cmd='Z {:.0f} {:.0f} {:.0f}'.format(xy[0],xy[1],time_Ms)
        self.serial.writeCmd(cmd)
    def cut(self,xyStart,xyFinish,time_Ms):
        if len(xyStart)!=2:
            raise TypeError('xy should be a length 2 list/tuple of ints')
        if (not isinstance(xyStart[0],int)) or (not isinstance(xyStart[1],int)):
            raise TypeError('xy should be a length 2 list/tuple of ints')
        if len(xyFinish)!=2:
            raise TypeError('xy should be a length 2 list/tuple of ints')
        if (not isinstance(xyFinish[0],int)) or (not isinstance(xyFinish[1],int)):
            raise TypeError('xy should be a length 2 list/tuple of ints')
        if not isinstance(time_Ms,(int,float)):
            raise TypeError('time should be an int or float')
        xyStart = self.calibration.map(np.array(xyStart))
        xyStart=np.round(xyStart)
        xyFinish = self.calibration.map(np.array(xyFinish))
        xyFinish = np.round(xyFinish)
        cmd='C {:.0f} {:.0f} {:.0f} {:.0f} {:.0f}'.format(xyStart[0],xyStart[1],xyFinish[0],xyFinish[1],time_Ms)
        self.serial.writeCmd(cmd)
    def move(self,xy):
        if len(xy)!=2:
            raise TypeError('xy should be a length 2 list/tuple of ints')
        if (not isinstance(xy[0],int)) or (not isinstance(xy[1],int)):
            raise TypeError('xy should be a length 2 list/tuple of ints')
        xy = self.calibration.map(np.array(xy))
        xy = np.round(xy)
        cmd = 'M {:.0f} {:.0f}'.format(xy[0], xy[1])
        self.serial.writeCmd(cmd)

class DemoGalvoDevice(iGalvoDevice):
    def __init__(self,serial=None):
        self.serial=serial
    def zap(self,xy,time_Ms):
        if len(xy)!=2:
            raise TypeError('xy should be a length 2 list/tuple of ints')
        if (not isinstance(xy[0],int)) or (not isinstance(xy[1],int)):
            raise TypeError('xy should be a length 2 list/tuple of ints')
        if not isinstance(time_Ms,(int,float)):
            raise TypeError('time should be an int or float')
        pass
    def cut(self,xyStart,xyFinish,time_Ms):
        if len(xyStart)!=2:
            raise TypeError('xy should be a length 2 list/tuple of ints')
        if (not isinstance(xyStart[0],int)) or (not isinstance(xyStart[1],int)):
            raise TypeError('xy should be a length 2 list/tuple of ints')
        if len(xyFinish)!=2:
            raise TypeError('xy should be a length 2 list/tuple of ints')
        if (not isinstance(xyFinish[0],int)) or (not isinstance(xyFinish[1],int)):
            raise TypeError('xy should be a length 2 list/tuple of ints')
        if not isinstance(time_Ms,(int,float)):
            raise TypeError('time should be an int or float')
        pass
    def move(self,xy):
        if len(xy)!=2:
            raise TypeError('xy should be a length 2 list/tuple of ints')
        if (not isinstance(xy[0],int)) or (not isinstance(xy[1],int)):
            raise TypeError('xy should be a length 2 list/tuple of ints')
        pass

class DeviceLibrary(iDeviceLibrary):
    devices=None
    deviceMap=None
    def __init__(self):
        globals = g.Globals()
        self.devices=[]
        self.deviceMap=dict()
        self.devices.append('DemoCamera')
        self.deviceMap['DemoCamera']=[globals.KEY_DEVICE_CAMERAS]
        self.devices.append('DemoLaser')
        self.deviceMap['DemoLaser'] = [globals.KEY_DEVICE_LASERS]
        self.devices.append('DemoFilterWheel')
        self.deviceMap['DemoFilterWheel'] = [globals.KEY_DEVICE_FILTERS]
        self.devices.append('DemoStage')
        self.deviceMap['DemoStage'] = [globals.KEY_DEVICE_STAGES]
        self.devices.append('DemoZStage')
        self.deviceMap['DemoZStage'] = [globals.KEY_DEVICE_ZSTAGES]
        self.devices.append('DemoPiezoStage')
        self.deviceMap['DemoPiezoStage'] = [globals.KEY_DEVICE_PIEZOSTAGE]
        self.devices.append('DemoStateDevice')
        self.deviceMap['DemoStateDevice'] = [globals.KEY_DEVICE_STATES]
        self.devices.append('DemoArduino')
        self.deviceMap['DemoArduino'] = [globals.KEY_DEVICE_STATES]
        self.devices.append('DemoGalvo')
        self.deviceMap['DemoGalvo'] = [globals.KEY_DEVICE_GALVOS]
        self.devices.append('TSLabArduino')
        self.deviceMap['TSLabArduino'] = [globals.KEY_DEVICE_STATES]
        self.devices.append('TSLabGalvo')
        self.deviceMap['TSLabGalvo'] = [globals.KEY_DEVICE_GALVOS]
        self.devices.append('DemoXYZFStage')
        self.deviceMap['DemoXYZFStage'] = [globals.KEY_DEVICE_STAGES,globals.KEY_DEVICE_ZSTAGES,globals.KEY_DEVICE_PIEZOSTAGE]
        self.devices.append('LaserDevice_Coherent')
        self.deviceMap['LaserDevice_Coherent']=[globals.KEY_DEVICE_LASERS]
        self.devices.append('LaserDevice_Vortran')
        self.deviceMap['LaserDevice_Vortran'] = [globals.KEY_DEVICE_LASERS]


    def listDeviceType(self,type):
        globals=g.Globals()
        if type not in globals.KEY_DEVICES:
            raise KeyError
        list = []
        for device in self.devices:
            interfaces = self.deviceMap[device]
            if type in interfaces:
                list.append(device)
        return list

    def get(self,key):
        if key in self.devices:
            command='self.'+key+'()'
            device=eval(command)
            return device

        else:
            return KeyError

    def DemoCamera(self):
        serial=Serial('test',isDummy=True)
        device=DemoCamera(serial=None)
        device.serial=serial
        return device

    def DemoLaser(self):
        serial=Serial('test',isDummy=True)
        device = DemoLaser(serial=None)
        device.serial = serial
        return device

    def DemoStage(self):
        serial=Serial('test',isDummy=True)
        device = DemoStage(serial=serial)
        device.serial = serial
        return device

    def DemoZStage(self):
        serial=Serial('test',isDummy=True)
        device = DemoZStage(serial=serial)
        device.serial = serial
        return device

    def DemoPiezoStage(self):
        serial=Serial('test',isDummy=True)
        device = DemoPiezoStage(serial=serial)
        device.serial = serial
        return device

    def DemoFilterWheel(self):
        serial=Serial('test',isDummy=True)
        device = DemoFilterWheel(serial=serial)
        device.serial = serial
        return device

    def DemoStateDevice(self):
        serial=Serial('test',isDummy=True)
        device = DemoStateDevice(serial=serial)
        device.serial = serial
        return device

    def DemoArduino(self):
        serial=Serial('test',isDummy=True)
        device = DemoStateDevice(serial=serial)
        device.serial = serial
        return device

    def DemoGalvo(self):
        serial=Serial('test',isDummy=True)
        device = DemoGalvoDevice(serial=serial)
        device.serial = serial
        return device

    def LaserDevice_Coherent(self):
        serial=Serial('test')
        serial.baud=19200
        serial.bytesize=8
        serial.parity='N'
        serial.xonxoff=False
        device=LaserDevice_Coherent(serial=serial)
        device.serial = serial
        return device

    def LaserDevice_Vortran(self):
        serial = Serial('test')
        serial.baud = 19200
        serial.bytesize = 8
        serial.parity = 'N'
        serial.xonxoff = False
        device = LaserDevice_Vortran()
        device.serial = serial
        return device

    def TSLabArduino(self):
        serial = Serial('test')
        serial.baud = 115200
        serial.bytesize = 8
        serial.parity = 'N'
        serial.xonxoff = False
        device = TSLabArduino()
        device.serial = serial
        return device

    def DemoXYZFStage(self):
        serial = Serial('test')
        serial.baud = 19200
        serial.bytesize = 8
        serial.parity = 'N'
        serial.xonxoff = False
        device = DemoXYZFStage()
        device.serial = serial
        return device

    def TSLabGalvo(self):
        serial = Serial('test')
        serial.baud = 115200
        serial.bytesize = 8
        serial.parity = 'N'
        serial.xonxoff = False
        device = TSLabGalvo(serial=serial)
        device.serial = serial
        return device

class ExternalDeviceManager(iExternalDeviceManager):
    '''keeps track of devices and serials and maps them properly. Some intividual devices might implement multiple device interafaces.
    Therefore we need an object that makes a specific device look like many individual devices. Works with device libbrary to
    make devices related to particular keys, and the interfaces they are associated with.'''
    devices=None
    _instance = None
    def __init__(self):
        globals=g.Globals()
        self.devices=dict()
        for key in globals.KEY_DEVICES:
            self.devices[key]=[]
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ExternalDeviceManager, cls).__new__(
                cls, *args, **kwargs)
        return cls._instance



    def addDevice(self,deviceName,port):
        lib=DeviceLibrary()
        interfaces=lib.deviceMap[deviceName]
        device=lib.get(deviceName)
        device.serial.port=port
        for interface in interfaces:
            self.devices[interface].append(device)


    def open(self):
        for interface in self.devices:
            for device in self.devices[interface]:
                device.serial.open()

    def close(self):
        for interface in self.devices:
            for device in self.devices[interface]:
                device.close()

    def listDeviceInterfaces(self):
        list=[]
        globals=g.Globals()
        interfaces=globals.KEY_DEVICES
        for i in interfaces:
            devices=self.devices[i]
            for d in devices:
                list.append(i)
        return list

    def listDeviceHardware(self):
        list = []
        globals = g.Globals()
        interfaces = globals.KEY_DEVICES
        for i in interfaces:
            devices = self.devices[i]
            for d in devices:
                list.append(d)
        return list

    def listDevicesAvailable(self):
        lib=DeviceLibrary()
        return lib.deviceMap

    def __getitem__(self, item):
        return self.devices[item]

    @property
    def properties(self):
        globals=g.Globals()
        prop=dict()
        for key in globals.KEY_DEVICES:
            prop[key]=self.devices[key]
        return prop

    def listPortsAvailable(self):
        ports=[]
        portFinder=list_ports.comports()
        for port, desc,hwid in sorted(portFinder):
            ports.append([port, desc, hwid])
        ports.append(['dummy'])
        return ports

    @property
    def configuration(self):
        config=dict()
        hardware=self.listDeviceHardware()
        for i in range(len(hardware)):
            name=hardware[i].__class__.__name__
            port=hardware[i].serial.port
            config[port]=name
        return config

    def loadConfiguration(self,portDevice):
        for port in portDevice.keys():
            self.addDevice(portDevice[port],port)