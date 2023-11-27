from acquisition import *
from globals import Globals as g
import unittest

class TestEventsBuilder(unittest.TestCase):
    def testDomain(self):
        events=EventsTicket()
        events.z_start=0.
        self.assertEqual(events.z_start,0.)
        events.z_start = None
        events.z_end=10.
        self.assertEqual(events.z_end, 10.)
        events.z_end = None
        events.z_step=.1
        self.assertEqual(events.z_step, 0.1)
        events.z_step = None
        events.num_time_points=10
        self.assertEqual(events.num_time_points, 10)
        events.num_time_points = None
        events.time_interval_s=10.
        self.assertEqual(events.time_interval_s, 10.)
        events.time_interval_s = None
        events.channel_group='Filters'
        self.assertEqual(events.channel_group, 'Filters')
        events.channel_group=None
        events.channels=['488','631','537']
        self.assertEqual(events.channels, ['488','631','537'])
        events.channels=None
        events.channel_exposure_ms = 513
        self.assertEqual(events.channel_exposure_ms, 513)
        events.channel_exposure_ms = None
        events.xy_positions = [[0.,0.],[0.,1.]]
        self.assertEqual(events.xy_positions, [[0.,0.],[0.,1.]])
        events.xy_positions = None
        events.xyz_positions = [[0., 0.,0.], [0., 1.,1.]]
        self.assertEqual(events.xyz_positions, [[0., 0.,0.], [0., 1.,1.]])
        events.xyz_positions = None


class TestAcquisitionPlugin(unittest.TestCase):
    def testInterface(self):
        plugin=AcquisitionPlugin()
        plugin.run
        plugin.properties
        plugin.load

    def testDomain(self):
        builder = AcquisitionBuilder()
        builder.addTimedEvents(10, 1.)
        builder.addZEvents(0., 10., 0.1)
        builder.addChannelEvents('Filter', ['488', '637', '531'], [400., 400., 400.])
        builder.addXYSequence([[0, 0], [0, 1], [1, 1]])
        builder.setHooks('default')
        self.assertEqual(builder.plugin.events.num_time_points, 10)
        self.assertEqual(builder.plugin.events.time_interval_s, 1.)
        self.assertEqual(builder.plugin.events.num_time_points, 10)
        self.assertEqual(builder.plugin.events.time_interval_s, 1)
        self.assertEqual(builder.plugin.events.z_start, 0.)
        self.assertEqual(builder.plugin.events.z_end, 10.)
        self.assertEqual(builder.plugin.events.z_step, 0.1)
        self.assertEqual(builder.plugin.events.channel_group, 'Filter')
        self.assertEqual(builder.plugin.events.channels, ['488', '637', '531'])
        self.assertEqual(builder.plugin.events.channel_exposures_ms, [400., 400., 400.])
        self.assertListEqual(builder.plugin.events.xy_positions, [[0, 0], [0, 1], [1, 1]])
        builder.getEvents()
        plugin = builder.getPlugin()
        properties=plugin.properties
        plugin.load(properties)
        self.assertEqual(plugin.events.num_time_points,10)
        self.assertEqual(plugin.events.time_interval_s, 1)
        self.assertEqual(plugin.events.z_start, 0.)
        self.assertEqual(plugin.events.z_end, 10.)
        self.assertEqual(plugin.events.z_step, 0.1)
        self.assertEqual(plugin.events.channel_group, 'Filter')
        self.assertEqual(plugin.events.channels, ['488', '637', '531'])
        self.assertEqual(plugin.events.channel_exposures_ms, [400., 400., 400.])
        self.assertListEqual(plugin.events.xy_positions, [[0, 0], [0, 1], [1, 1]])

        #plugin.run()


class TestAcquisitionBuilder(unittest.TestCase):
    def testDomain(self):
        builder=AcquisitionBuilder()
        builder.addTimedEvents(10,1.)
        builder.addZEvents(0.,10.,0.1)
        builder.addChannelEvents('Filter',['488','637','531'],[400.,400.,400.])
        builder.addXYZSequence([[0, 0,0], [0, 1,1], [1, 1,2]])
        builder.getEvents()
        builder.setHooks('default')
        plugin=builder.getPlugin()

    def testInterface(self):
        builder = AcquisitionBuilder()
        builder.getPlugin
        builder.addTimedEvents
        builder.addZEvents
        builder.addXYSequence
        builder.addXYZSequence
        builder.addGridEvents
        builder.addChannelEvents
        builder.getEvents
        builder.setSaveDirectory
        builder.setSaveName
        builder.setHooks
        builder.setIsMultiprocesing
        builder.setSavingQueueSize
        builder.setBridgeTimeoutMs
        builder.setIsDebug
        builder.setIsCoreLogDebug
        builder.setPort
        builder.setIsShowDisplay
        builder.setIsShutterOpenBetweenChannels
        builder.setIsShutterOpenBetweenZSteps
        builder.setEventsOrder

    def testAcceptance0(self):
        builder = AcquisitionBuilder()
        self.assertRaises(TypeError,builder.getEvents,())

    def testAcceptance1(self):
        builder = AcquisitionBuilder()
        builder.addTimedEvents(10, 1.)
        self.assertIsInstance(builder.getEvents(),list)

    def testAcceptance2(self):
        builder = AcquisitionBuilder()
        builder.addZEvents(0.,10.,0.1)
        self.assertIsInstance(builder.getEvents(),list)

    def testAcceptance4(self):
        builder = AcquisitionBuilder()
        builder.addChannelEvents('Filter', ['488', '637', '531'], [400., 400., 400.])
        self.assertIsInstance(builder.getEvents(),list)

    def testAcceptance5(self):
        builder = AcquisitionBuilder()
        builder.addXYSequence([[0, 0], [0, 1], [1, 1]])
        self.assertIsInstance(builder.getEvents(),list)

    def testAcceptance6(self):
        builder = AcquisitionBuilder()
        builder.addXYZSequence([[0, 0,0], [0, 1,1], [1, 1,2]])
        self.assertIsInstance(builder.getEvents(),list)


class TestPluginLibrary(unittest.TestCase):
    def testInterface(self):
        lib=AcquisitionPluginLibrary()
        lib.list
        lib.get

    def testDomain(self):
        lib=AcquisitionPluginLibrary()
        names = lib.list()
        lib.get('default')
        #lib.get('findzplane1color',[[0,0]],[0,1,0.5],'Channel',['DAPI'])
        return

    def testAcceptance(self):
        lib=AcquisitionPluginLibrary()
        names=lib.list()
        self.assertIn('default',names)
        self.assertNotIn('__class__',names)
        self.assertNotIn('__dict__', names)
        self.assertNotIn('__doc__', names)
        plugin=lib.get('default')
        self.assertRaises(KeyError,lib.get,'get')
        self.assertRaises(KeyError, lib.get, 'list')
        self.assertRaises(TypeError, lib.get, 0)
