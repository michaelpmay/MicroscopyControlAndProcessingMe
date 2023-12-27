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

class TestDecicionIfThen(TestCase):
    def testDecision_always_returnsDecision(self):
        decision=DecisionIfThen().always()
        self.assertIsInstance(decision,DecisionIfThen)

    def testDecision_never_returnsDecision(self):
        decision = DecisionIfThen().never()
        self.assertIsInstance(decision, DecisionIfThen)

    def testDecision_repeat_returnsDecision(self):
        decision=DecisionIfThen().repeat()
        self.assertIsInstance(decision,DecisionIfThen)

    def testDecision_always_Repeat_returnsDecision(self):
        decision = DecisionIfThen().always().repeat()
        self.assertIsInstance(decision, DecisionIfThen)


class TestDecisionFromCallback(TestCase):
    def setUp(self) -> None:
        self.object=DecisionFromCallback()

    def test_function_(self):
        pass