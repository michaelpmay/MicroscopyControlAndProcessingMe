from unittest import TestCase
from verbosity import *
class TestReportFull(TestCase):
    def setUp(self) -> None:
        self.object=ReportFull()
    def testDomain(self):
        self.object.add("printing {0}\n",'Michael')
        self.object.add("printing {0} {1}\n", 'Michael','May')
        self.object.add("printing {0} {1} born in {2}\n", 'Michael','May',1994)
        self.object.print()
    def test0(self):
        self.assertRaises(TypeError,self.object.add,())
    def test1(self):
        self.assertRaises(TypeError,self.object.add,[])
    def test2(self):
        self.assertRaises(TypeError,self.object.add,0)

class TestResportSilent(TestCase):
    def setUp(self) -> None:
        self.object=ReportSilent()
    def testDomain(self):
        self.object.add("printing {0}\n",'Michael')
        self.object.add("printing {0} {1}\n", 'Michael','May')
        self.object.add("printing {0} {1} born in {2}\n", 'Michael','May',1994)
        #self.object.print() #hide the print so i can see the test oputputs eauser


class TestReportLog(TestCase):
    def setUp(self) -> None:
        self.object=ReportLog()
        self.object.setLogFile('report.log')
    def testDomain(self):
        self.object.add("printing {0}\n",'Test')
        self.object.add("printing {0} {1}\n", 'Test','Test')
        self.object.add("printing {0} {1} born in {2}\n", 'Test','Test',1994)
        self.object.print()
    def test0(self):
        self.assertRaises(TypeError,self.object.add,())
    def test1(self):
        self.assertRaises(TypeError,self.object.add,[])
    def test2(self):
        self.assertRaises(TypeError,self.object.add,0)

class TestVerbosity(TestCase):
    def setUp(self) -> None:
        self.object=Verbosity()
    def testDomain(self):
        self.object.add("printing {0}\n",'Test')
        self.object.add("printing {0} {1}\n", 'Test','Test')
        self.object.add("printing {0} {1} born in {2}\n", 'Test','Test',1994)
        self.object.print()

    def test0(self):
        self.assertRaises(TypeError,self.object.add,())
    def test1(self):
        self.assertRaises(TypeError,self.object.add,[])
    def test2(self):
        self.assertRaises(TypeError,self.object.add,0)