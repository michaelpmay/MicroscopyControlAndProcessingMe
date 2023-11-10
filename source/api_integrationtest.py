import time
import unittest

from api import *
import time
import cv2
import numpy as np

class TestConnectedAPIFacade(unittest.TestCase):
    def setUp(self) -> None:
        self.object=ConnectedAPIFacade()
        self.object.connectAutomationService('localhost', 8000)
        self.object.connectProcessingService('localhost', 8001)
        #self.object.connectDecisionService('localhost', 8002)

    def testDomain1(self):
        request = AcquisitionRequest()
        request.name = "test_API"
        self.object.post_acquisition_and_acquire(request)
        images=self.object.get_image_data('test_API_0_1')
        images=cv2.resize(np.array(images).astype('float'),(512,512))
        images=images.astype('uint16').tolist()
        request= {'name':'null','image':images}
        for i in range(10):
            startTime=time.time()
            image=self.object.process('process',request)
            deltaTime=time.time()-startTime
            print(deltaTime)

    def testDomain2(self):
        request = AcquisitionRequest()
        request.name = "test_API"
        self.object.post_acquisition_and_acquire(request)
        images = self.object.get_image_data('test_API_0_1')
        images = cv2.resize(np.array(images).astype('float'), (1024, 1024))
        images = images.astype('uint16').tolist()
        imageSet=[]
        for i in range(100):
            imageSet.append(images)
        request = {'name': 'mask', 'image': imageSet}
        for i in range(100):
            startTime = time.time()
            image = self.object.process('process', request)
            deltaTime = time.time() - startTime
            print(deltaTime)

    def testDomain3(self):
        request = AcquisitionRequest()
        request.name = "test_API"
        self.object.post_acquisition_and_acquire(request)
        images = self.object.get_image_data('test_API_0_1')
        images = cv2.resize(np.array(images).astype('float'), (512, 512))
        images = images.astype('uint16').tolist()
        request = {'name': 'count', 'image': images}
        masks = self.object.process('process', request)
        print(masks)

    def test_get_acquisitions_avaiable_list_returnslist(self):
        items=self.object.get_acquisitions_avaiable_list()
        items=eval(items.decode('utf-8'))
        print(items)

    def test_get_scheduled_acquisition_list_returnslist(self):
        items=self.object.get_scheduled_acquisition_list()
        self.assertIsInstance(items, list)

    def test2(self):
        items=self.object.get_completed_acquisition_list()
        self.assertIsInstance(items, list)

    def test3(self):
        items=self.object.get_failed_acquisition_list()
        self.assertIsInstance(items, list)

    def test4(self):
        items=self.object.get_acquisition_history()
        self.assertIsInstance(items, list)