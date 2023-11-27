from unittest import TestCase
from image_process import *
import numpy as np
import data_manager as d
import cv2
import os
from PIL import Image
class TestMicroscopyImage(TestCase):
    def setUp(self):
        self.object=MicroscopyImage()
    def test_setChannel_works(self):
        pixels=np.zeros([50, 50])
        self.object.setChannel(0,pixels)
        self.assertEqual(self.object.shape,(50,50,1))
        self.object.setChannel(1,pixels)
        self.assertEqual(self.object.shape, (50, 50, 2))
    def test_getChannel_works(self):
        pixels=np.zeros([50, 50])
        self.object.setChannel(0,pixels)
        self.object.getChannel(0)
    def test_setChannel_IntStr_RaisesTypeError(self):
        self.assertRaises(TypeError, self.object.setChannel, (0, 'hello'))
    def test_setChannel_tuple_RaisesTypeError(self):
        self.assertRaises(TypeError, self.object.setChannel, ())
    def test_setChannel_IntFloat_RaisesTypeError(self):
        self.assertRaises(TypeError, self.object.setChannel, (0,3.14159))
    def test_accept_process_works(self):
        process=MicroscopyImageProcess()
        self.object.setChannel(0,np.zeros([50, 50]))
        #self.object.acceptProcess(process)
    def testDomain(self):
        pixels = np.zeros([50, 50])
        self.object.setChannel(0, pixels)
        self.object.setChannel(1, pixels)
        self.object.setChannel(2, pixels)
        lib=MicroscopyImageProcessLibrary()
        process = lib.null()
        self.object.acceptProcess(process)
        process=lib.add(1)
        self.object.acceptProcess(process)


class TestMicroscopyImageStack(TestCase):
    def setUp(self) -> None:
        self.object=MicroscopyImageStack()
    def test_append_works(self):
        self.object.append(MicroscopyImage())
        self.assertEqual(len(self.object.stack),1)
    def test_append_items_raisesTypeError(self):
        with self.assertRaises(TypeError):
            self.object.append(1)
            self.object.append([])
            self.object.append('h')
    def test_accept_works(self):
        image=MicroscopyImage()
        image.setChannel(0,np.zeros([50,50]))
        self.object.append(image)
        process=MicroscopyImageProcessPipeline()
        self.object.acceptProcess(process)

    def testDomain(self):
        image = MicroscopyImage()
        pixels = np.zeros([50, 50])
        image.setChannel(0, pixels)
        image.setChannel(1, pixels)
        image.setChannel(2, pixels)
        imageStack=MicroscopyImageStack()
        for i in range(3):
            imageStack.append(image)
        lib = MicroscopyImageProcessLibrary
        process = lib.null()
        imageStack.acceptProcess(process)
        process = lib.add(1)
        imageStack.acceptProcess(process)


class TestMicroscopyImageProcessLibrary(TestCase):
    def setUp(self) -> None:
        self.object=MicroscopyImageProcessLibrary()
        self.image=MicroscopyImage()
        self.image_stack=MicroscopyImageStack()
        pixels = np.ones([5, 5])
        for i in range(4):
            self.image.setChannel(i, pixels)
        for i in range(3):
            self.image_stack.append(self.image)

    def test_null_image_works(self):
        process= self.object.null()
        self.image.acceptProcess(process)
        self.image_stack.acceptProcess(process)

    def test_add_image_works(self):
        process = self.object.add(3)
        self.image.acceptProcess(process)
        self.image_stack.acceptProcess(process)
        self.assertEqual(self.image.getChannel(0)[0, 0], 4)

    def test_add_items_raisesTypeError(self):
        items=[[],{},(),'h']
        with self.assertRaises(TypeError):
            for item in items:
                self.object.add(item)

    def test_subtract_image_works(self):
        process = self.object.subtract(1)
        self.image.acceptProcess(process)
        self.image_stack.acceptProcess(process)
        self.assertEqual(self.image.getChannel(0)[0, 0], 0)

    def test_subtract_items_raisesTypeError(self):
        items=[[],{},(),'h']
        with self.assertRaises(TypeError):
            for item in items:
                self.object.subtract(item)

    def test_multiply_image_works(self):
        process = self.object.multiply(2)
        self.image.acceptProcess(process)
        self.image_stack.acceptProcess(process)
        self.assertEqual(self.image.getChannel(0)[0, 0], 2)

    def test_multiply_items_raisesTypeError(self):
        items=[[],{},(),'h']
        with self.assertRaises(TypeError):
            for item in items:
                self.object.multiply(item)

    def test_addChannel_image_works(self):
        process = self.object.addChannel(3,0)
        self.image.acceptProcess(process)
        self.image_stack.acceptProcess(process)
        self.assertEqual(self.image.getChannel(0)[0, 0], 4)

    def test_addChannel_items_raisesTypeError(self):
        items=[[],{},(),'h']
        with self.assertRaises(TypeError):
            for item in items:
                self.object.addChannel(item)

    def test_subtractChannel_image_works(self):
        process = self.object.subtractChannel(1, 0)
        self.image.acceptProcess(process)
        self.image_stack.acceptProcess(process)
        self.assertEqual(self.image.getChannel(0)[0, 0], 0)

    def test_subtractChannel_items_raisesTypeError(self):
        items=[[],{},(),'h']
        with self.assertRaises(TypeError):
            for item in items:
                self.object.subtractChannel(item)

    def test_multiplyChannel_image_works(self):
        process = self.object.multiplyChannel(2, 0)
        self.image.acceptProcess(process)
        self.image_stack.acceptProcess(process)
        self.assertEqual(self.image.getChannel(0)[0, 0], 2)

    def test_multiplyChannel_items_raisesTypeError(self):
        items=[0,'h',3.4]
        with self.assertRaises(TypeError):
            for item in items:
                self.object.multiplyChannel(item)

    def test_crop_image_works(self):
        process = self.object.crop([0,2,0,2])
        self.image.acceptProcess(process)
        self.image_stack.acceptProcess(process)
        self.assertEqual(self.image.shape,(3,3,4))
    def test_crop_items_raisesTypeError(self):
        items=[0,'h',3.4]
        with self.assertRaises(TypeError):
            for item in items:
                self.object.crop(item)

class TestMicroscopyImageProcessModel(TestCase):
    def testInterface(self):
        #make test images and image stacks
        image = MicroscopyImage()
        for i in range(4):
            image.setChannel(i, np.ones([10, 10]))
        imageStack = MicroscopyImageStack()

        for i in range(3):
            image = MicroscopyImage()
            for j in range(4):
                image.setChannel(j, np.ones([10, 10]))
            imageStack.append(image)

        builder=MicrosopyImageProcessBuilder()
        lib = MicroscopyImageProcessLibrary
        builder.add(lib.crop([0,5,0,5]))
        builder.add(lib.add(5))
        builder.add(lib.multiply(6))
        pipeline=builder.getPipeline()
        image.acceptProcess(pipeline)
        imageStack.acceptProcess(pipeline)

class TestPycromanagerImagePipeline(TestCase):
    def testInterface(self):
        pixels = np.ones([50, 50])
        pipeline=PycromanagerImageProcessPipeline()
        lib=MicroscopyImageProcessLibrary
        pipeline.append(lib.add(4.))
        pipeline.append(lib.multiply(4.))
        pipeline.append(lib.subtract(4.))
        pipeline(pixels,None,None,None)

    def testFailure(self):
        pixels = np.zeros([50, 50])
        pipeline = PycromanagerImageProcessPipeline()
        pipeline(pixels,None,None,None)

class TestCellDetectorCellMask(TestCase):
    def setUp(self) -> None:
        self.object=CellDetectorCellMask()
    def test1(self):
        image=cv2.imread('data/test/testimage.jpg')
        dimensions=(32,32)
        image=cv2.resize(image,dimensions)
        masks=self.object.process(image)


class TestSpotCountLocations(TestCase):
    def setUp(self) -> None:
        self.object=SpotCountLocations()
    def test_spotCount_returnsList(self):
        path=os.path.join('data','test','testimage.jpg')
        image=Image.open(path)
        positions=self.object.process(image)


class TestSpotCountLocationsDoughnut(TestCase):
    def setUp(self) -> None:
        self.object=SpotCountLocationsDoughnut()
    def test_spotCount_returnsList(self):
        path=os.path.join('data','test','testimage.jpg')
        image=Image.open(path)
        positions=self.object.process(image)


class TestSpotDetectImagesBooleanDoughnut(TestCase):
    def setUp(self) -> None:
                self.object = SpotDetectImagesBooleanDoughnut()

    def test_spotCount_returnsList(self):
        path = os.path.join('data', 'test', 'testimage.jpg')
        image = Image.open(path)
        positions = self.object.process(image)


class TestSpotCountCellFrequency(TestCase):
    def setUp(self) -> None:
        self.object = SpotCountCellFrequency()

    def test_spotCount_returnsList(self):
        path = os.path.join('data', 'test', 'testimage.jpg')
        image = Image.open(path)
        image=np.array(image)
        frequency = self.object.process(image[:, :, 0].squeeze())


class TestSpotCounter(TestCase):
    def setUp(self) -> None:
        self.object=SpotCounter()
    def test_spotCount_returnsList(self):
        path=os.path.join('data','test','testimage.jpg')
        image=np.array(Image.open(path))
        numSpots=self.object.process(image)


class TestImageCalculateFishPipeline(TestCase):
    def setUp(self) -> None:
        self.object=ImageCalculateFishPipeline()
    def test_spotCount_returnsList(self):
        path=os.path.join('data','test','testimage.jpg')
        image=np.array(Image.open(path))
        #numSpots=self.object.process(image)
