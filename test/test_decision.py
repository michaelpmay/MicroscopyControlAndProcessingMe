from unittest import TestCase
from decision import *
from acquisition import AcquisitionPlugin
from pycromanager import Dataset
class TestDecisionRepeatAcquisition(TestCase):
    def setUp(self) -> None:
        self.object=DecisionRepeatAcquisition()
    def test_propose_repeat_acquisition_returns_acquisitin(self):
        acquisition=AcquisitionPlugin()
        processed_data={}
        self.object.propose(processed_data,acquisition)


class TestDecicion(TestCase):
    def testDecision_always_returnsDecision(self):
        decision=Decision().always()
        self.assertIsInstance(decision,Decision)

    def testDecision_never_returnsDecision(self):
        decision = Decision().never()
        self.assertIsInstance(decision, Decision)

    def testDecision_repeat_returnsDecision(self):
        decision=Decision().repeat()
        self.assertIsInstance(decision,Decision)

    def testDecision_always_Repeat_returnsDecision(self):
        decision = Decision().always().repeat()
        self.assertIsInstance(decision, Decision)