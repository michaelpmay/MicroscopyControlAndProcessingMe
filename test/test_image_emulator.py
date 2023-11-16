import os
from unittest import TestCase

import pandas as pd

from source.image_emulator import *
from os import path
import numpy as np
import matplotlib.pyplot as plt
class TestImageEmulatorFromArray(TestCase):
    def setUp(self) -> None:
        self.object=ImageEmulatorFromArray()
        self.object.image=[[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]]
    def test_setImageFromArray_ndarray_changesImage(self):
        array=np.array([[0]])
        self.object.setImageFromArray(array)
        self.assertIs(array, self.object.image)

    def test_setImageFromArray_list_changesImage(self):
        array=[[0]]
        self.object.setImageFromArray(array)
        self.assertEqual(np.array(array),self.object.image)

    def test_setImageFromArray_tuple_raisesTypeError(self):
        self.assertRaises(TypeError,self.object.setImageFromArray,())

    def test_setImageFromArray_int_raisesTypeError(self):
        self.assertRaises(TypeError,self.object.setImageFromArray,0)

    def test_setImageFromArray_float_raisesTypeError(self):
        self.assertRaises(TypeError,self.object.setImageFromArray,2.3)

    def test_emulate_event_returnsImage(self):
        position=[0,0,5.]
        self.object.generate(position,n=2)

class TestImageEmulator2Channel(TestCase):
    def setUp(self) -> None:
        self.object=ImageEmulator2Channel()
    def test_loadImageFilePath_works(self):
        image_folder=pathlib.Path(path.join('data','core','cell_library'))
        self.object.loadImageFilePath(image_folder)
        self.assertIsInstance(self.object.list_library_cells,list)
        self.assertIsInstance(self.object.dataframe_cell_library, pd.DataFrame)
    def test_generate_image_returns(self):
        imagePixSizeXY=[512,512]
        numCellsSimulated=1
        image_folder = pathlib.Path(path.join('data', 'core', 'cell_library'))
        self.object.loadImageFilePath(image_folder)
        self.object.simulatePositions(imagePixSizeXY,numCellsSimulated)
    def test_generate_Pathpath_returns(self):
        image_folder = pathlib.Path(path.join('data', 'core', 'cell_library'))
        self.object.loadImageFilePath(image_folder)
    def test_generate_Strpath_returns(self):
        image_folder = 'data/core/cell_library'
        self.object.loadImageFilePath(image_folder)
    def test_generateSimulatedPositions_returnsNumpyArray(self):
        position=[0,0]
        imSize=[512,512]
        imagePixSizeXY = [1000,1000]
        numCellsSimulated = 3
        self.object.simulatePositions(imagePixSizeXY, numCellsSimulated)
        self.object.setXYImageSize(imSize)
        image=self.object.generate(position)

    def test_generateSimulatedPositions_returnsNumpyArraySize(self):
        imagePixSizeXY = [512*2, 512*2]
        numCellsSimulated = 1
        position=[0,0,0]
        imSize=[256,256]
        self.object.simulatePositions(imagePixSizeXY, numCellsSimulated)
        self.object.setXYImageSize(imSize)
        image_folder = 'data/core/cell_library'
        self.object.loadImageFilePath(image_folder)
        image=self.object.generate(position)
        self.assertIsInstance(image,np.ndarray)
        self.assertEqual(image.shape[0], imSize[0])
        self.assertEqual(image.shape[1], imSize[1])

    def test_generateSimulatedPositions_returnsNumpyArraySize2(self):
        imagePixSizeXY = [512*2, 512*2]
        numCellsSimulated = 5
        position=[0,0,0]
        imSize=[256,256]
        self.object.simulatePositions(imagePixSizeXY, numCellsSimulated)
        self.object.setXYImageSize(imSize)
        image_folder = 'data/core/cell_library'
        self.object.loadImageFilePath(image_folder)
        image=self.object.generate(position)
        self.assertIsInstance(image,np.ndarray)
        self.assertEqual(image.shape[0], imSize[0])
        self.assertEqual(image.shape[1], imSize[1])
        shown_image = Image.fromarray(image / np.max(image) * 500)


    def test_generateSimulatedPositions_returnsNumpyArraySize3(self):
        imagePixSizeXY = [512*2, 512*2]
        numCellsSimulated = 5
        position=[512,512,0]
        imSize=[256,256]
        self.object.simulatePositions(imagePixSizeXY, numCellsSimulated)
        self.object.setXYImageSize(imSize)
        self.object.setAlpha([1,-2,3])
        image_folder = 'data/core/cell_library'
        self.object.loadImageFilePath(image_folder)
        image=self.object.generate(position)
        self.assertIsInstance(image,np.ndarray)
        self.assertEqual(image.shape[0], imSize[0])
        self.assertEqual(image.shape[1], imSize[1])



'''
emulator=ImageEmulator()
emulator.setChannelType(0,'spots')
emulator.setChannelType(1,'nuceleus')
emulator.setChannelType(2,'zeros')
emulator.setChannelType(3,'zeros')
image=emulator.generator(position)
emulator.setChannelType(0,'spots')
emulator.setChannelType(1,'spots')
emulator.setChannelType(2,'zeros')
emulator.setChannelType(3,'nucleus')
'''