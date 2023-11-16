from source.apd import *
from unittest import TestCase

class TestAPDFunction(TestCase):
    def setUp(self) -> None:
        self.object=APDFunction()
    def test_run_empty_returnsNone(self):
        system=[]
        reply=self.object.run(system)
        self.assertIsNone(reply)

class TestAPDSystem(TestCase):
    def setUp(self) -> None:
        self.object=APDSystem()
        self.function=APDFunction()
    def test_runFunction_returnsValue(self):
        self.object.runFunction(self.function)

class TestAPDFunctionLibrary(TestCase):
    def setUp(self) -> None:
        self.object=APDFunctionLibrary()
        self.system=APDSystem()
    def test_get_null_returnsAPDPipeline(self):
        apd=self.object.get('null')
        self.assertIsInstance(apd,APDFunction)
    def test_get_null_returnsCallable(self):
        apd=self.object.get('null')
        apd.run(self.system)
    def test_list_returnsList(self):
        apdlist=self.object.list()
        self.assertIsInstance(apdlist,list)