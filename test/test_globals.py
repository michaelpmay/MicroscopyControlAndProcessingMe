from globals import *
import unittest
class TestGlobals(unittest.TestCase):
    def testDomain(self):
        g1=Globals('config.txt')
        g2=Globals('config.txt')
        g1.test=True
        self.assertIs(g1,g2) #globals is singleton
        self.assertEqual(g1.test,True) #changes to g1 affect g2
