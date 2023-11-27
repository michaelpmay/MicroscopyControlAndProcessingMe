import sqlite3.dbapi2
import unittest
from automation import *

class TestBlock(unittest.TestCase):
    def TestInterface(self):
        lib=BlockLibrary
        block=Block()


class TestAutomationBlockLibrary(unittest.TestCase):
    # todo
    def testInterface(self):
        lib=BlockLibrary
        block0 = lib.value(3)
        block0.execute()
        block1 = lib.value(2)
        block1.execute()
        blocks=[lib.add(),lib.subtract(),lib.multiply(),lib.divide()]
        output=[]
        for block in blocks:
            block.input = [block0.output[0], block1.output[0]]
            block.execute()
            output.append(block.output[0])
        self.assertEqual(output,[5,1,6,1.5])

    def test_link(self):
        lib = BlockLibrary
        value1 = lib.value(3)
        value2 = lib.value(2)
        add=lib.add()
        sub=lib.subtract()
        mul=lib.multiply()
        div=lib.divide()
        add.input=[value1.output,value2.output]
        mul.input=[add.output,value1.output]
        div.input=[mul.output,value2.output]
        sub.input=[div.output,add.output]

    def testTimers(self):
        lib=BlockLibrary
        blocks=[lib.timeMilliSeconds(),lib.timeSeconds(),lib.timeMinutes(),lib.timeHours()]
        for block in blocks:
            block.start()

    def testPulsers(self):
        lib = BlockLibrary
        blocks = [lib.pulseMilliSeconds(5),lib.pulseSeconds(.05)]
        for block in blocks:
            block.start()
            value=0
            while not value:
                value=block.output

class TestAutomationBlockModel(unittest.TestCase):
    def testInterface(self):
        automation=AutomationBlockModel('MyModel')
        lib=BlockLibrary
        automation.addBlock('b0',lib.value(5))
        automation.addBlock('b1',lib.value(3))
        automation.addBlock('b2',lib.add())
        automation.addBlock('b3',lib.multiply())
        automation.link('b2-0','b0-0')
        automation.link('b2-1','b1-0')
        automation.execute()
        self.assertEqual(automation.pool['b2'].output[0],8)