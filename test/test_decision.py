from unittest import TestCase
from decision import *
from acquisition import AcquisitionPlugin
from pycromanager import Dataset

class TestDecisionRepeatAcquisition(TestCase):
    def setUp(self) -> None:
        self.object=DecisionRepeatAcquisition()
    def test_propose_repeat_acquisition_returns_acquisitin(self):
        acquisition=AcquisitionPlugin()
        processed_data=[]
        self.object.propose(processed_data,acquisition)


class TestDecision(TestCase):
    def setUp(self) -> None:
        self.object=Decision()

    def test_function_(self):
        def function(self,processed_data,acquisition):
            return acquisition
        decision=Decision(function=function)
        processed_data = []
        acquisition = AcquisitionPlugin()
        returnValue=decision.propose(processed_data,acquisition)
        self.assertIsInstance(returnValue,AcquisitionPlugin)


class TestDecisionLibrary(TestCase):
    def setUp(self) -> None:
        self.object=DecisionLibrary()

    def test_null_returns_decision(self):
        decision=self.object.null()
        acq=decision.propose([],AcquisitionPlugin())
        self.assertIs(acq,None)

    def test_repeat_returns_decision(self):
        decision=self.object.repeat()
        acq=decision.propose([],AcquisitionPlugin())
        self.assertIsInstance(acq,AcquisitionPlugin)