from source.environment import *
import os
import unittest
class TestBackend(unittest.TestCase):
    def testDomain(self):
        backend = Backend()
        self.assertRaises(PermissionError,backend.setUser,'ringobingoasDasdakjsdfka','123')
        if 'default' not in backend.listUsers():
            backend.newUser('defualt','')
        backend.setUser('default','')
        backend.addDevice('DemoCamera', 'test')
        backend.addDevice('DemoFilterWheel', 'test')
        backend.addDevice('DemoStage', 'test')
        backend.addDevice('DemoZStage', 'test')
        backend.addDevice('DemoZStage', 'test')
        backend.addDevice('DemoStateDevice', 'test')
        backend.addDevice('DemoCamera', 'test')
        backend.addDevice('DemoFilterWheel', 'test')
        backend.addDevice('DemoStage', 'test')
        backend.addDevice('DemoZStage', 'test')
        backend.addDevice('DemoStateDevice', 'test')
        builder=a.AcquisitionBuilder()
        builder.addTimedEvents(10,1.)
        builder.addXYSequence([[0,0],[0,1]])
        builder.addZEvents(0,3.,0.5)
        builder.setHooks('default')
        builder.setSaveName('acquisition')
        plugin=builder.getPlugin()
        backend.acquisition=plugin
        backend.listDevicesAvailable()
        backend.listDeviceInterfaces()
        backend.listDeviceHardware()
        backend.listUsers()
        backend.listUser()
        backend.connectDevices()
        backend.saveAcquisition('myModel.acq')
        backend.loadAcquisition('myModel.acq')
        backend.clearAllStagedAcquisitions()
        backend.stageAcquisition('myModel.acq')
        backend.stageAcquisition('default')
        backend.stageAcquisition('default')
        backend.stageAcquisition('default')
        positions=[[0,0]]
        z_range=[0,1,1]
        channel='Filter'
        channelMap=['DAPI','Cy5']
        channelExposure=[100,100]
        backend.stageAcquisition('findzplane3color',positions,z_range,channel,channelMap,channelExposure)
        backend.loadStagedAcquisition('default_0.acq')
        backend.loadStagedAcquisition('myModel_0.acq')
        names=backend.listAvailableAcquisitions()
        self.assertIn('default',names)
        self.assertIn('myModel.acq', names)
        names=backend.listStagedAcquisitions()
        self.assertIn('myModel_0.acq',names)
        self.assertIn('default_0.acq', names)
        self.assertIn('default_1.acq', names)
        self.assertIn('default_2.acq', names)
        names=backend.listCompletedAcqusititions()
        #self.assertIn('default_0_finished.acq',names)
        backend.devices.configuration
        backend.saveConfiguration('myConfig.cfg')
        names=backend.listConfigurations()
        self.assertIn('myConfig.cfg',names)
        backend.loadConfiguration('myConfig.cfg')

    def testAceeptance(self):
        self.assertRaises(TypeError,Backend,config=1)
        backend = Backend()
        self.assertRaises(KeyError,backend.addDevice,1,3)


class TestEnvironementBuilder(unittest.TestCase):
    def testDomain(self):
        builder = EnvironmentBuilder()
        #builder.setDataManager('local')
        builder.setInterface('headless')
        builder.setAuthentication('local')
        env = builder.getEnvironment()
    def testAcceptance(self):
        builder = EnvironmentBuilder()
        #self.assertRaises(KeyError,builder.setDataManager,'lolomomo')
        #self.assertRaises(TypeError, builder.setDataManager, [])
        builder.setInterface('headless')
        self.assertRaises(KeyError, builder.setInterface, 'lolomomo')
        self.assertRaises(TypeError, builder.setInterface, 0)
        self.assertRaises(TypeError, builder.setInterface, [])
        builder.setAuthentication('local')
        self.assertRaises(KeyError, builder.setAuthentication, 'lolomomo')
        self.assertRaises(TypeError, builder.setAuthentication, 0)
        self.assertRaises(TypeError, builder.setAuthentication, [])
        builder = builder.getEnvironment()

class TestEnvironment(unittest.TestCase):
    def testDomain(self):
        builder = EnvironmentBuilder()
        #builder.setDataManager('local')
        builder.setInterface('headless')
        builder.setAuthentication('local')
        env = builder.getEnvironment()
        env.backend.setUser('default', '')
        env.backend.addDevice('DemoCamera', 'test')
        env.backend.addDevice('DemoFilterWheel', 'test')
        env.backend.listDevicesAvailable()
        env.backend.listDeviceInterfaces()
        env.backend.listDeviceHardware()
        env.backend.listUsers()
        env.backend.loadAcquisition('default')
        env.backend.saveAcquisition('myModel.acq')
        env.backend.loadAcquisition('myModel.acq')
        self.assertEqual(env.backend.acquisition.hooks.name,'default')


    def testDomainGui(self):
        builder=EnvironmentBuilder()
        builder.setInterface('gui')
        env = builder.getEnvironment()

    def testDomainHeadless(self):
        builder=EnvironmentBuilder()
        builder.setInterface('headless')
        env = builder.getEnvironment()

    def testUserGlobals(self):
        builder = EnvironmentBuilder()
        builder.setInterface('headless')
        env = builder.getEnvironment()

    def testHumanInterface(self):
        builder = EnvironmentBuilder()
        builder.setInterface('headless')
        builder.setRootDataPath('')
        env = builder.getEnvironment()

class TestStageBoundaries(unittest.TestCase):
    def setUp(self) -> None:
        self.object=StageBoundaries()

    def test0(self):
        positions=[[1,2],[2,3],[4,5]]
        self.object.bound(positions)
    def test1(self):
        positions = [[1, 2], [2, 3], [4, 5]]
        self.object.setXboundary([0, 5])
        self.object.bound(positions)
    def test2(self):
        positions = [[1, 2], [2, 3], [4, 5]]
        self.object.setYboundary([0, 5])
        self.object.bound(positions)
    def test3(self):
        positions = [[1, 2], [2, 3], [4, 5]]
        self.object.setXboundary([0, 5])
        self.object.bound(positions)
    def test4(self):
        positions = [[1, 2], [2, 3], [4, 5]]
        self.object.setXboundary([0, 5])
        self.object.setYboundary([0, 5])
        self.object.setZboundary([0, 5])
        positions=self.object.bound(positions)








