from unittest import TestCase
from utility import *

class TestZSearchXYPositionOptimizerGreedy(TestCase):
    def setUp(self) -> None:
        self.object=ZSearchXYPositionOptimizerGreedy()
        self.positions=[[0,0],[0,456],[0,456],[1,756],[598,415],[983,563],[753,123],[997,972],[623,507],[328,706],[531,109]]
    def test_optimiz_works(self):
        positions=self.object.optimize(self.positions)
        self.assertIsInstance(positions,list)
    def test_optimize_shortList_works(self):
        positions = self.object.optimize(self.positions[0:3])
        self.assertEqual(len(positions),2)
    def test_optimizeDuplicateList_works(self):
        positions=[[0,456],[0,456]]
        positions=self.object.optimize(positions)
        self.assertEqual(len(positions),1)

class TestZSearchXYPositionOptimizerFull(TestCase):
    def setUp(self) -> None:
        self.object=ZSearchXYPositionOptimizerFull()
        self.positions=[[0,0],[0,456],[0,456],[1,756],[598,415],[983,563],[753,123],[997,972],[623,507],[328,706],[531,109]]
    def test_optimiz_works(self):
        positions=self.object.optimize(self.positions)
        self.assertIsInstance(positions,list)
    def test_optimize_shortList_works(self):
        positions = self.object.optimize(self.positions[0:3])
        self.assertEqual(len(positions),2)
    def test_optimizeDuplicateList_works(self):
        positions=[[0,456],[0,456]]
        positions=self.object.optimize(positions)
        self.assertEqual(len(positions),1)