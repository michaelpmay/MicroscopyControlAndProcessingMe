from source.hooks import *
from unittest import TestCase

class TestHook(TestCase):
    def setUp(self) -> None:
        self.object=Hook()

    def test_run_event_returnsEvent(self):
        event = {'x':0,'y':0}
        bridge=[]
        stack=[]
        returnEvent=self.object.run(event,bridge)
        self.assertIs(returnEvent,event)

class TestHookChain(TestCase):
    def setUp(self) -> None:
        self.object=HookChain()
    def test_link_Hook_works(self):
        hook=Hook()
        self.object.link(hook)
    def test_link_array_raisesTypeError(self):
        hook=[]
        self.assertRaises(TypeError,self.object.link,hook)
    def test_link_tuple_raisesTypeError(self):
        hook=[]
        self.assertRaises(TypeError,self.object.link,hook)
    def test_link_int_raisesTypeError(self):
        hook=5
        self.assertRaises(TypeError,self.object.link,hook)
    def test_run_event_returnsEvent(self):
        hook = Hook()
        self.object.link(hook)
        self.object.link(hook)
        self.object.link(hook)
        event = {'x':0,'y':0}
        bridge=[]
        stack=[]
        returnEvent=self.object.run(event,bridge)
        self.assertIs(returnEvent,event)

class TestImageHook(TestCase):
    def setUp(self) -> None:
        self.object = ImageHook()
    def test_run_imagemetadata_returnsimagemetadta(self):
        image=[0]
        metadata={}
        bridge = []
        stack = []
        out=self.object.run(image,metadata)
        self.assertIsNotNone(out)

class TestImageHookChain(TestCase):
    def setUp(self) -> None:
        self.object = ImageHookChain()
    def test_run_imagemetadata_returnsimagemetadta(self):
        image=[0]
        metadata={}
        bridge = []
        stack = []
        hook=ImageHook()
        self.object.link(hook)
        out=self.object.run(image,metadata)
        self.assertIsNotNone(out)

class TestHookSet(TestCase):
    def setUp(self) -> None:
        self.object=HookSet()

    def test_link_hooks_works(self):
        hooks = AcquisitionHooks()
        hooks.link(self.object)
        hooks.link(self.object)



class TestHookSetLibrary(TestCase):
    def setUp(self) -> None:
        self.object=HookSetLibrary()
    def test_get_default_returnsHookSet(self):
        hooks=self.object.get('default')
        self.assertIsInstance(hooks,HookSet)
    def test_get_verbose__returnsHookSet(self):
        hooks = self.object.get('verbose')
        self.assertIsInstance(hooks, HookSet)
    def test_get_helloworld_returnsHookSet(self):
        hooks = self.object.get('hello_world')
        self.assertIsInstance(hooks, HookSet)
    def test_get_seedevents_returnsHookSet(self):
        events=[{},{},{}]
        hooks = self.object.get('seedevents',events)
        self.assertIsInstance(hooks, HookSet)
    def test_get_printhelloworld_returnsHookSet(self):
        hooks = self.object.get('print','hello_world')
        self.assertIsInstance(hooks, HookSet)
    def test_get_imageemulator_returnsHookSet(self):
        simulator=[]
        hooks = self.object.get('image_emulator',simulator)
        self.assertIsInstance(hooks, HookSet)

class TestAcquisitionHooks(TestCase):
    def setUp(self) -> None:
        self.object=AcquisitionHooks()

    def test_link_hookSet_works(self):
        lib = HookSetLibrary()
        vHooks = lib.get('null')
        self.object.link(vHooks)
        self.object.link(vHooks)
        self.object.link(vHooks)
        self.object.hookPreHardware({},[])

