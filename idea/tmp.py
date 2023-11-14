device code
MM
Michael May
Mon 5/2/2022 4:26 PM









To:Michael May
import time

import pymmcore
import os
import serial
import numpy as np
import pycromanager


class MicroManagerCore_NULL():
    def __init__(self,mm_dir="C:\\Program Files\\Micro-Manager-2.0gamma\\",config="ScopeWithPixelCalibration.cfg"):
        print("WARNING NULL CORE")
        pass

    def snap(self):
        pass

    def getImage(self):
        pass

    def getXY(self):
        pass

    def getZ(self):
        pass

    def moveZ(self, z):
        pass

    def moveXY(self, x,y):
        pass

    def waitforstage(self):
        pass

    def waitforcamera(self):
        pass

    def setExposure(self, time_ms):
        pass

    def getExposure(self, time_ms):
        pass

    def enableContinuousFocus(self,bool):
        pass


class MicroManagerStudio_NULL:
    def __init__(self,config="config"):
        pass
    def autofocusNow(self):
        pass


class MicroManagerCore_Pycromanager():
    def __init__(self,mm_dir="C:\\Program Files\\Micro-Manager-2.0gamma\\",config="ScopeWithPixelCalibration.cfg"):
        self.bridge=pycromanager.Bridge(convert_camel_case=False,debug=False)
        self.core=self.bridge.get_core()
        self.studio = self.bridge.get_studio()
        self.core.loadSystemConfiguration(os.path.join(mm_dir, config))
        self.stage=self.core.getXYStageDevice()
        self.camera = self.core.getCameraDevice()

    def snap(self):
        self.core.snapImage()

    def getImage(self):
        image=self.core.getImage()
        length=int(np.sqrt(image.shape))
        image=image.reshape(length,length)
        return image

    def getXY(self):
        return np.array([self.core.getXPosition(),self.core.getYPosition()])

    def getZ(self):
        return self.core.getPosition()

    def moveZ(self, z):
        self.core.setPosition(z)

    def moveXY(self, x,y):
        self.core.setXYPosition(x,y)
        self.waitforstage()

    def waitforstage(self):
        self.core.waitForDevice(self.stage)

    def waitforcamera(self):
        self.core.waitForDevice(self.camera)


    def setExposure(self, time_ms):
        self.core.setExposure(time_ms)

    def getExposure(self):
        self.core.getExposure()

    def enableContinuousFocus(self,boolean):
        self.core.enableContinuousFocus(boolean)

    def autoFocusNow(self,method="CRISP"):
        with pycromanager.Bridge(convert_camel_case=False, debug=False) as bridge:
            studio=bridge.get_studio()
            autofocuser = self.studio.getAutofocusManager()
            autofocuser.setAutofocusMethodByName(method)
            self.studio.autofocusNow()


class LaserDevice:
    def close(self):
        if not self.dummy:
            self.ser.close()

    def write_cmd(self, cmd):
        serialcmd = cmd + '\r\n'
        self.ser.write(serialcmd.encode())
        echo = self.ser.readline()
        response = self.ser.readline()

        if self.debug:
            print('write:', repr(serialcmd))
            print('echo:', echo)
            print('response:', response)
        if 'Error'.encode() in response:
            raise IOError('laser command error:' + repr(response))
        echo = echo.decode('utf-8')
        echo = echo.splitlines()[0]
        return echo

    def get_identification(self):
        pass

    def reset(self):
        pass

    def get_model(self):
        pass

    def get_wavelength(self):
        pass

    def get_power_rating(self):
        pass

    def get_minimum_power(self):
        pass

    def get_maximum_power(self):
        pass

    def set_laser_auto_start(self, cmd):
        pass

    def get_status(self):
        pass

    def get_faults(self):
        pass

    def get_temperature(self):
        pass

    def get_interlock_status(self):
        pass

    def select_operating_mode(self, cmd):
        pass

    def get_operating_mode(self):
        pass

    def set_laser_status(self, cmd):
        pass

    def get_laser_status(self):
        pass

    def set_laser_power(self, value):
        pass

    def get_laser_power(self):
        pass

    def present_output_power(self):
        pass


class LaserDevice_Coherent(object):

    def __init__(self, port, debug=False, dummy=False):  # change port according to device listing in windows.

        self.debug = debug
        self.dummy = dummy
        self.port = port

        if not self.dummy:
            self.ser = ser = serial.Serial(port=self.port, baudrate=921600,
                                           bytesize=8, parity='N',
                                           stopbits=1, xonxoff=False, timeout=.005,write_timeout=.005)
            ser.flush()

    def close(self):
        if not self.dummy:
            self.ser.close()

    def write_cmd(self, cmd):
        serialcmd = cmd + '\r\n'
        self.ser.write(serialcmd.encode())
        echo = self.ser.readline()
        response = self.ser.readline()

        if self.debug:
            print('write:', repr(serialcmd))
            print('echo:', echo)
            print('response:', response)
        if 'Error'.encode() in response:
            raise IOError('laser command error:' + repr(response))
        echo = echo.decode('utf-8')
        echo = echo.splitlines()[0]
        return echo

    def get_identification(self):
        """ Gets the laser's identification string """
        fullresp = self.write_cmd('*IDN?')
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
        fullresp = self.write_cmd('*RST')
        resp = fullresp
        return resp

    def get_model(self):
        """ Retrieves the model name of the laser """
        fullresp = self.write_cmd('SYSTem1:INFormation:MODel?')
        resp = fullresp
        return resp

    def get_wavelength(self):
        """ Retrieves the wavelength of the laser """
        fullresp = self.write_cmd('SYSTem:INFormation:WAVelength?')
        resp = fullresp
        return resp

    def get_power_rating(self):
        """ Retrieves the power (mW) rating of the laser """
        fullresp = self.write_cmd('SYSTem:INFormation:POWer?')
        resp = fullresp
        return float(resp) * 1000

    def get_minimum_power(self):
        """Returns the minimum CW laser output power in (mW)"""
        fullresp = self.write_cmd('SOURce:POWer:LIMit:LOW?')
        resp = fullresp
        return float(resp) * 1000

    def get_maximum_power(self):
        """Returns the maximum CW laser output power in (mW)"""
        fullresp = self.write_cmd('SOURce:POWer:LIMit:HIGH?')
        resp = fullresp
        return float(resp) * 1000

    def set_laser_auto_start(self, cmd):
        ''' Enables or disables the laser Auto Start feature. Setting is saved in persistent memory.
        The factory default is OFF. If the laser is connected to a OBIS Remote, this setting is overriden by the
        hardware switch of the min-controller '''

        fullresp = self.write_cmd('SYSTem1:AUTostart ' + cmd)  # cmd = ON|OFF
        resp = fullresp
        return resp

    def get_status(self):
        """ Queries the system status """
        fullresp = self.write_cmd('SYSTem:STATus?')
        resp = fullresp
        return resp

    def get_faults(self):
        """ Queries current system faults """
        fullresp = self.write_cmd('SYSTem:FAULt?')
        resp = fullresp
        return resp

    def get_temperature(self):
        """ Returns the present laser base plate temperature """
        fullresp = self.write_cmd('SOURce:TEMPerature:BASeplate?')
        resp = fullresp
        return resp

    def get_interlock_status(self):
        """ Returns the status of the system interlock """
        fullresp = self.write_cmd('SYSTem:LOCK?')
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

    def select_operating_mode(self, cmd):
        '''cmd = CWP|CWC :                         Sets the laser operating mode to internal CW and deselects external modulation. The default setting is CW with constant power or CWP.
           cmd = DIGital|ANALog|MIXed|DIGSO|MIXSO: Sets the laser operating mode to CW constant current modulated by one or more external sources. MIXED source combines both external digital and external analog modulation.
        The setting is saved in non-volatile memory '''
        if cmd == 'CWP' or cmd == 'CWC':
            fullresp = self.write_cmd('SOURce:AM:INTernal ' + cmd)
        else:
            fullresp = self.write_cmd('SOURce:AM:EXTernal ' + cmd)
        resp = fullresp
        return resp

    def get_operating_mode(self):
        ''' Queries the current operating mode of the laser.  '''
        fullresp = self.write_cmd('SOURce:AM:SOURce?')
        resp = fullresp
        return resp

    def set_laser_status(self, cmd):
        ''' Turns the laser ON or OFF. When turning the laser ON, actual laser
        emission may be delayed due to internal circuit stabilization logic and/or
        CDRH delays.   '''
        fullresp = self.write_cmd('SOURce:AM:STATe ' + cmd)  # cmd = ON|OFF
        resp = fullresp
        return resp

    def get_laser_status(self):
        ''' Queries the current laser emission status.  '''
        fullresp = self.write_cmd('SOURce:AM:STATe?')
        resp = fullresp
        return resp

    def set_laser_power(self, value):
        ''' Sets present laser power level (mW). Setting power level does not turn
        the laser on.    '''
        fullresp = self.write_cmd('SOURce:POWer:LEVel:IMMediate:AMPLitude ' + str(value / 1000))
        resp = fullresp
        return resp

    def get_laser_power(self):
        ''' Gets laser power setting level (mW)'''
        fullresp = self.write_cmd('SOURce:POWer:LEVel:IMMediate:AMPLitude?')
        resp = fullresp
        return float(resp) * 1000

    def present_output_power(self):
        """ Returns the present output power of the laser (mW)"""
        fullresp = self.write_cmd('SOURce:POWer:LEVel?')
        resp = fullresp
        return float(resp) * 1000


class LaserDevice_Vortran:
    def __init__(self, port, debug=False, dummy=False):  # change port according to device listing in windows.

        self.debug = debug
        self.dummy = dummy
        self.port = port

        if not self.dummy:
            self.ser = ser = serial.Serial(port=self.port, baudrate=921600,
                                           bytesize=8, parity='N',
                                           stopbits=1, xonxoff=False, timeout=.005,write_timeout=.005)
            ser.flush()

    def close(self):
        if not self.dummy:
            self.ser.close()

    def write_cmd(self, cmd):
        serialcmd = cmd + '\r\n'
        self.ser.write(serialcmd.encode())
        echo = self.ser.readline()
        response = self.ser.readline()

        if self.debug:
            print('write:', repr(serialcmd))
            print('echo:', echo)
            print('response:', response)
        if 'Error'.encode() in response:
            raise IOError('laser command error:' + repr(response))
        echo = echo.decode('utf-8')
        echo = echo.splitlines()[0]
        return echo

    def get_identification(self):
        resp = self.write_cmd('?SFV')
        return resp

    def reset(self):
        pass

    def get_model(self):
        resp = self.write_cmd('?SPV')
        return resp

    def get_wavelength(self):
        resp = self.write_cmd('?LW')
        return resp

    def get_power_rating(self):
        resp = self.write_cmd('?RP')
        return resp

    def get_minimum_power(self):
        return '0'

    def get_maximum_power(self):
        resp = self.write_cmd('?MAXP')
        return resp

    def set_laser_auto_start(self, cmd):
        pass

    def get_status(self):
        resp = self.write_cmd('?C')
        return resp

    def get_faults(self):
        resp = self.write_cmd('?FC')
        return resp

    def get_temperature(self):
        resp = self.write_cmd('?OBT')
        return resp

    def get_interlock_status(self):
        resp = self.write_cmd('?IL')
        return resp

    def select_operating_mode(self, value):
        resp = self.write_cmd('C ' + str(value))
        return resp

    def get_operating_mode(self):
        resp = self.write_cmd('?C')
        return resp

    def set_laser_status(self, value):
        resp = self.write_cmd('LE ' + str(value))
        return resp

    def get_laser_status(self):
        resp = self.write_cmd('?LE')
        return resp

    def set_laser_power(self, value):
        resp = self.write_cmd('LP '+ str(value))
        return resp

    def get_laser_power(self):
        resp = self.write_cmd('?LP')
        return resp

    def present_output_power(self):
        pass

    def help(self):
        resp = self.write_cmd('?H')
        return resp


class ControllerGalvo:
    #todo
    def __init__(self, port, debug=False, dummy=False):  # change port according to device listing in windows.

        self.debug = debug
        self.dummy = dummy
        self.port = port

        if not self.dummy:
            self.ser = ser = serial.Serial(port=self.port, baudrate=19200,
                                           bytesize=8, parity='N',
                                           stopbits=1, xonxoff=False, timeout=.005,write_timeout=.005)
            ser.flush()

    def close(self):
        if not self.dummy:
            self.ser.close()

    def write_cmd(self, cmd):
        serialcmd = cmd + '\r\n'
        self.ser.write(serialcmd.encode())
        response = self.ser.readline()

        if self.debug:
            print('write:', repr(serialcmd))
            print('response:', response)
        if 'Error'.encode() in response:
            raise IOError('laser command error:' + repr(response))
        return response

    def move(self,x,y):
        self.write_cmd("M "+str(x) +" "+str(y))

    def zap(self,x,y,t):
        self.write_cmd("Z "+str(x) +" "+str(y)+" "+str(t))

    def cut(self,x,y):
        self.write_cmd("C "+str(x) +" "+str(y))


class GalvoDevice:
    #todo
    laser=None
    controller=None

    def __init__(self,COM1,COM2):
        self.laser = None
        self.controller = ControllerGalvo(COM2)

    def move(self,x,y):
        self.controller.move(int(x),int(y))

    def zap(self,x,y,t):
        self.controller.zap(int(x),int(y),t)

    def cut(self,x,y):
        self.controller.cut(int(x),int(y))

    def set_laser_power(self,value):
        self.laser.set_laser_power(value)


class GalvoDevice_NULL:
    #todo
    laser=None
    controller=None

    def __init__(self):
        pass

    def move(self, x, y):
        print('warning null device used')
        pass

    def zap(self, x, y, t):
        print('warning null device used')
        pass

    def cut(self, x, y):
        print('warning null device used')
        pass

    def set_laser_power(self, value):
        print('warning null device used')
        pass


class Lasers:
    lasers=None

    def __init__(self):
        self.lasers = [LaserDevice_Coherent('COM21'), LaserDevice_Coherent('COM22'), LaserDevice_Coherent('COM23')]
        pass


class ArduinoStateControl:
    _colorMode=None
    def __init__(self, port, debug=False, dummy=False):  # change port according to device listing in windows.

        self.debug = debug
        self.dummy = dummy
        self.port = port

        if not self.dummy:
            self.ser = ser = serial.Serial(port=self.port, baudrate=19200,
                                           bytesize=8, parity='N',
                                           stopbits=1, xonxoff=False, timeout=.005,write_timeout=.005)
            ser.flush()
            time.sleep(5)
        self._setColorModeFromBool([0,0,0])
    def close(self):
        if not self.dummy:
            self.ser.close()

    def write_cmd(self, cmd):
        serialcmd = cmd + '\r\n'
        self.ser.write(serialcmd.encode())
        response = self.ser.readline()

        if self.debug:
            print('write:', repr(serialcmd))
            print('response:', response)
        if 'Error'.encode() in response:
            raise IOError('laser command error:' + repr(response))
        return response

    def setColorMode(self,*args):
        lazer_onoff_bools=[0,0,0]
        boolmap=dict.fromkeys(['r','red','Red','RED','637'],2)
        boolmap.update(dict.fromkeys(['g','green','Green','GREEN','561'],1))
        boolmap.update(dict.fromkeys(['b', 'blue','Blue', 'BLUE', '488'], 0))
        for arg in args[0]:
            lazer_onoff_bools[boolmap[arg]]=1
        self._setColorModeFromBool(lazer_onoff_bools)

    def _setColorModeFromBool(self,bools):
        message='M'
        for i in range(len(bools)):
            message=message+' '+str(bools[i])
        print(self.port)
        self.write_cmd(message)
        self._colorMode = bools

    def getColorMode(self):
        colorMode=[]
        for i in range(len(self._colorMode)):
            if (self._colorMode[i] ==1):
                if i==0:
                    colorMode.append('637')
                if i==1:
                    colorMode.append('561')
                if i==2:
                    colorMode.append('488')
        return colorMode



class Microscope:
    mm=None
    galvo=None
    def __init__(self,config):
        self.mm = MicroManagerCore_Pycromanager(config=config)
        self.galvo=GalvoDevice_NULL()
    def snap(self):
        self.mm.snap()

    def getImage(self):
        return self.mm.getImage()

    def getXY(self):
        return self.mm.getXY()

    def getZ(self):
        return self.mm.getZ()

    def getXYZ(self):
        xyPosition=self.getXY()
        zPosition=self.getZ()
        return [xyPosition[0],xyPosition[1],zPosition]

    def moveZ(self, z):
        self.mm.moveZ(z)

    def moveXY(self, x,y):
        self.mm.moveXY(x,y)

    def moveGalvo(self, x,y):
        self.mm.move(x,y)

    def zap(self, x,y,t):
        self.galvo.zap(x,y,t)

    def cut(self, x,y):
        self.galvo.cut(x,y)

    def waitforstage(self):
        self.mm.waitforstage()

    def waitforcamera(self):
        self.mm.waitforcamera()

    def setExposure(self,time_ms):
        self.mm.setExposure(time_ms)

    def getExposure(self,time_ms):
        self.mm.getExposure(time_ms)

    def autofocusNow(self):
        self.mm.studio.autofocusNow()

    def enableContinuousFocus(self,bool):
        self.mm.enableContinuousFocus(bool)

    def getImageWidth(self):
        return self.mm.core.getImageWidth()

    def getImageHeight(self):
        return self.mm.core.getImageHeight()
