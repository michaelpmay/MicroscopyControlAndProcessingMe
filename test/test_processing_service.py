from unittest import TestCase
from source.processing_service import *
from source.data_manager import DataManager
import cv2
import os
class TestImageProcessAPI(TestCase):
    def testDomain(self):
        dManager=DataManager()
        dManager.storage.folder=''
        image=dManager.load('data/core/MLDatasetMasked/images/image_126.jpg')
        request=ProcessRequest()
        request.image=image.tolist()
        request.name='mask'
        mask=process(request)
        1+1
