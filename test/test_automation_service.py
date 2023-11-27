from unittest import TestCase
from automation_service import *
class TestAutomationAPI(TestCase):
    def test0(self):
        list=listAvailableAcquisitions()

    def testDomain(self):
        listAcquisitionHistory()

        listStagedAcquisitions()
        listCompletedAcqusititions()
        listFailedAcquisitions()
        acq='default'
        stageAcquisition(acq)
        #tryCompleteAllStagedAcquisitions()
        #get_device_hardware()
        listImageData()
        #image=loadImageData('test_API_0')

