from unittest import TestCase
from source.decision import *
from source.acquisition import AcquisitionPlugin
from pycromanager import Dataset
class TestDecisionRepeatAcquisition(TestCase):
    def setUp(self) -> None:
        self.object=DecisionRepeatAcquisition()
    def test_propose_repeat_acquisition_returns_acquisitin(self):
        acquisition=AcquisitionPlugin()
        processed_data={}
        self.object.propose(processed_data,acquisition)

