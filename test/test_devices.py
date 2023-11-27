from devices import *
import unittest
class TestSerial(unittest.TestCase):
    def setUp(self) -> None:
        self.object=Serial('test',isDummy=True)
    def test_domain(self):
        # is this test dumb? is the interface an interface? yes!
        self.object=Serial('test',isDummy=True)
        self.object.open()
        self.object.writeCmd('test')
        self.object.close()


class TestDeviceLibrary(unittest.TestCase):
    def setUp(self):
        self.object=DeviceLibrary()

    def test_get_DemoCamera(self):
        self.object.get('DemoCamera')
    def test_get_DemoFilter(self):
        device=self.object.get('DemoFilter')
    def test_get_DemoStage(self):
        device=self.object.get('DemoStage')
    def test_get_DemoZStage(self):
        device=self.object.get('DemoZStage')
    def test_get_DemoPiezo(self):
        device=self.object.get('DemoPeizo')
    def test_get_DemState(self):
        device=self.object.get('DemoState')
    def test_camera_devices_works(self):
        globals = g.Globals()
        for key in self.object.listDeviceType(globals.KEY_DEVICE_CAMERAS):
            camera = self.object.get(key)
            camera.snap()
            camera.setMode('Free')
    def test_laser_devices_works(self):
        globals = g.Globals()
        for key in self.object.listDeviceType(globals.KEY_DEVICE_LASERS):
            laser=self.object.get(key)
            laser.serial=Serial('test',isDummy=True)
            laser.getIdentification()
            laser.reset()
            laser.getModel()
            laser.getWavelength()
            laser.getPowerRatingInWatts()
            laser.getMinimumPowerInWatts()
            laser.getMaximumPowerInWatts()
            laser.setLaserAutoStart('ON')
            laser.getFaults()
            laser.getTemperatureInC()
            laser.getInterlockStatus()
            laser.setOperatingMode('D')
            laser.getOperatingMode()
            laser.setLaserState(1)
            laser.setLaserState(0)
            laser.getLaserState()
            laser.setLaserPowerInWatts(0)
            laser.getLaserPowerInWatts()
            laser.presentOutputPower()
    def test_filter_device_works(self):
        globals = g.Globals()
        for key in self.object.listDeviceType(globals.KEY_DEVICE_FILTERS):
            filter=self.object.get(key)
            filter.swap(0)
    def test_stage_device_works_(self):
        globals = g.Globals()
        for key in self.object.listDeviceType(globals.KEY_DEVICE_STAGES):
            stage=self.object.get(key)
            stage.setXY(0.,0.)
            stage.getXY()
    def test_zstage_device_works(self):
        globals = g.Globals()
        for key in self.object.listDeviceType(globals.KEY_DEVICE_ZSTAGES):
            zstage = self.object.get(key)
            zstage.setZ(0.)
            zstage.getZ()
    def test_piezo_stage_device_works(self):
        globals = g.Globals()
        for key in self.object.listDeviceType(globals.KEY_DEVICE_PIEZOSTAGE):
            fstage = self.object.get(key)
            fstage.setF(0.)
            fstage.getF()
    def test_stat_device_works(self):
        globals = g.Globals()
        for key in self.object.listDeviceType(globals.KEY_DEVICE_STATES):
            device = self.object.get(key)
            device.serial=Serial('test',isDummy=True)
            device.setState([1,1,1,1])
            device.getState()

class TestExternalDeviceManager(unittest.TestCase):
    def testInterface(self):
        dManager=ExternalDeviceManager()
        dManager2 = ExternalDeviceManager()
        self.assertIs(dManager,dManager2)
        dManager.addDevice('DemoCamera',None)
        dManager.addDevice('DemoCamera', None)
        dManager.addDevice('DemoLaser', None)
        dManager.addDevice('DemoLaser', None)
        dManager.addDevice('DemoLaser', None)
        dManager.addDevice('DemoStage', None)
        dManager.addDevice('DemoZStage', None)
        dManager.addDevice('DemoPiezoStage', None)
        dManager.addDevice('DemoFilterWheel', None)
        dManager.addDevice('DemoArduino', None)
        dManager.addDevice('DemoArduino', None)
        dManager.addDevice('DemoGalvo',None)
        dManager.open()
        dManager.close()
        dManager['Camera'][0]
        dManager['Camera'][1]
        dManager['Stage'][0]
        dManager['Laser'][0]
        dManager['Laser'][2]
        dManager['ZStage'][0]
        dManager['PiezoStage'][0]
        dManager['StateDevice'][0]
        dManager['StateDevice'][1]
        dManager['Galvo'][0]
        dManager.listDeviceInterfaces()
        dManager.listDeviceHardware()
        dManager.listDevicesAvailable()

    def testMultiDeviceInterface(self):
        dManager = ExternalDeviceManager()
        dManager.addDevice('DemoXYZFStage', None)
        self.assertIs(dManager.devices['Stage'][0], dManager.devices['ZStage'][0])
        self.assertIs(dManager.devices['Stage'][0], dManager.devices['PiezoStage'][0])


class TestGalvoDevice(unittest.TestCase):
    def testDomain(self):
        dManager=ExternalDeviceManager()
        dManager.addDevice('DemoGalvo', None)
        dManager.addDevice('TSLabGalvo', None)
        for galvo in dManager['Galvo']:
            galvo.serial.isDummy=True
            galvo.zap([0,0],1)
            galvo.zap([-1,-1],1)
            self.assertRaises(TypeError,galvo.zap,([-1, -1,-1], 1))
            self.assertRaises(TypeError,galvo.zap,([None, None],1))
            self.assertRaises(TypeError,galvo.zap,(['h', 'weq'],1))
            self.assertRaises(TypeError,galvo.zap,([[], []], 1))
            self.assertRaises(TypeError,galvo.zap,([(), ()], 1))

            galvo.move([0, 0])
            galvo.move([-1, -1])
            self.assertRaises(TypeError,galvo.move,([-1, -1, -1]))
            self.assertRaises(TypeError,galvo.move,([0, 'h']))
            self.assertRaises(TypeError,galvo.move,(['h', 0]))
            self.assertRaises(TypeError,galvo.move,([None, None]))
            self.assertRaises(TypeError,galvo.move,(['h', 'weq']))
            self.assertRaises(TypeError,galvo.move,([[], []]))
            self.assertRaises(TypeError,galvo.move,([(), ()]))

            galvo.cut([0, 0],[0, 0],1)
            galvo.cut([0, 0], [-1, -1],1)
            self.assertRaises(TypeError,galvo.cut,([0, 0,1], [-1, -1,1],1))
            self.assertRaises(TypeError,galvo.cut,([0, 0,1], [-1, -1],1))
            self.assertRaises(TypeError,galvo.cut,([0, 0], [-1, -1,1],1))
            self.assertRaises(TypeError,galvo.cut,([None, None],[None, None],1))
            self.assertRaises(TypeError,galvo.cut,(['h', 'weq'],['h', 'weq'],1))
            self.assertRaises(TypeError,galvo.cut,([[], []],[[], []],1))
            self.assertRaises(TypeError,galvo.cut,([(), ()],[[], []],1))


class TestLaserDevice_Coherent(unittest.TestCase):
    def setUp(self) -> None:
        self.object=LaserDevice_Coherent()
    def test_open_works(self):
        self.object.open()
    def test_close_works(self):
        self.object.close()
    def test_writeCmd_string_works(self):
        self.object.writeCmd('hello')
    def test_writeCmd_int_raisesTypeError(self):
        self.assertRaises(TypeError,self.object.writeCmd,0)
    def test_writeCmd_float_raisesTypeError(self):
        self.assertRaises(TypeError,self.object.writeCmd,0.)
    def test_writeCmd_iter_raisesTypeError(self):
        self.assertRaises(TypeError,self.object.writeCmd,())
    def test_getIdentification_works(self):
        self.object.getIdentification()
    def test_reset_works(self):
        self.object.getIdentification()
    def test_model_works(self):
        self.object.getIdentification()
    def test_getPowerRatingInWatts_works(self):
        self.object.getIdentification()