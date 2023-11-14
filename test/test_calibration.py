import unittest
import os
from source.calibration import *
from source.data_manager import *

from source.data_manager import DataManager
class TestMatrixCalibration(unittest.TestCase):
    def testDomain(self):
        calibration=MatrixCalibration()
        calibration.setMatrix(2*np.identity(2))
        calibration.setZero(np.array([0.,0.]).T)
        transformedValue= calibration.map(np.array([2.,1.]).T)
        self.assertEqual(transformedValue[0], 4.)
        self.assertEqual(transformedValue[1], 2.)

        dManager=DataManager()
        dManager.storage.folder=os.path.join('data','test')
        dManager.save('test.cal',calibration)
        calibration=dManager.load('test.cal')
        transformedValue = calibration.map(np.array([2., 1.]).T)
        self.assertEqual(transformedValue[0], 4.)
        self.assertEqual(transformedValue[1], 2.)

    def testInterface(self):
        calibration = MatrixCalibration()
        self.assertRaises(TypeError, calibration.setMatrix,2)
        self.assertRaises(TypeError, calibration.setMatrix, 'hello')
        self.assertRaises(TypeError, calibration.setMatrix, [])
        self.assertRaises(TypeError, calibration.setZero, 2)
        self.assertRaises(TypeError, calibration.setZero, 'hello')
        self.assertRaises(TypeError, calibration.setZero, [])
        calibration.setMatrix(2 * np.identity(2))
        self.assertRaises(TypeError, calibration.calibrate, 2)
        self.assertRaises(TypeError, calibration.calibrate, '2')
        self.assertRaises(TypeError, calibration.calibrate, [])

class TestMatrixMultiCalibration(unittest.TestCase):

    def testDomain(self):
        multiCalibration=MatrixMultiCalibration()
        multiCalibration2=MatrixMultiCalibration()
        self.assertIs(multiCalibration,multiCalibration2)
        calibration=MatrixCalibration()
        calibration.setMatrix([[1,0],[0,1]])
        calibration.setZero([0,0])
        multiCalibration.addCalibration('Pixel', 'Galvo', 2, 60,calibration)
        self.assertRaises(TypeError,  multiCalibration.addCalibration, 0, 'Galvo', 2, 60, calibration)
        self.assertRaises(TypeError,  multiCalibration.addCalibration, 0., 'Galvo', 2, 60, calibration)
        self.assertRaises(TypeError,  multiCalibration.addCalibration, [], 'Galvo', 2, 60, calibration)
        self.assertRaises(TypeError,  multiCalibration.addCalibration, 'Pixel', 'Galvo', 'h', 60, calibration)
        self.assertRaises(TypeError,  multiCalibration.addCalibration, 'Pixel', 'Galvo', [], 60, calibration)
        self.assertRaises(TypeError,  multiCalibration.addCalibration, 'Pixel', 'Galvo', 2., 60, calibration)
        self.assertRaises(ValueError, multiCalibration.addCalibration,'WWNIASJBHKS', 'Galvo', 2, 60,calibration)
        self.assertRaises(ValueError, multiCalibration.addCalibration, 'Pixel', 'ASDNASLJKN', 2, 60, calibration)
        multiCalibration.addCalibration('View' , 'Galvo', 2, 60, calibration)
        multiCalibration.addCalibration('Pixel', 'View' , 2, 60, calibration)
        multiCalibration.setCalibration('Pixel', 'Galvo', 2, 60)
        multiCalibration.map([500,500])
        multiCalibration.setCalibration('View', 'Galvo', 2, 60)
        multiCalibration.map([500, 500])
        multiCalibration.listCalibrations()
        props=multiCalibration.properties
        multiCalibration2=MatrixMultiCalibration()
        multiCalibration2.load(props)
        multiCalibration2.setCalibration('View', 'Galvo', 2, 60)
        multiCalibration2.map([500, 500])
        self.assertListEqual(multiCalibration.listCalibrations(),multiCalibration2.listCalibrations())
        dManager=DataManager()
        dManager.storage.folder=os.path.join('data','test')
        dManager.save('test.mcal',multiCalibration)
        dManager.clearCache()
        multiCalibration3=dManager.load('test.mcal')
        #self.assertListEqual(multiCalibration.listCalibrations(), multiCalibration3.listCalibrations())
        #multiCalibration3.setCalibration('View', 'Galvo', 2, 60)
        #multiCalibration3.map([500, 500])
        #multiCalibration3.setCalibration('View', 'View', 2, 60)
        #multiCalibration3.map([500, 500])




    def testAcceptance(self):
        calibrator = MatrixMultiCalibration()
        # todo

class TestMatrixCalibrationBuilderFrom3Positions(unittest.TestCase):
    def testDomain(self):
        builder=MatrixCalibrationBuilderFrom3Positions()
        x=[[387,553],[587,553],[387,753]]
        y=[[512,512],[498,696],[328,501]]
        builder.setPositionMap(x,y)
        builder.setZero([387,553],[512,512])
        calibration1=builder.getForwardCalibration()
        calibration1.map(x[0])
        calibration1.map(x[1])
        calibration1.map(x[2])
        calibration2=builder.getReverseCalibration()
        calibration2.map(y[0])
        calibration2.map(y[1])
        calibration2.map(y[2])
        self.assertRaises(TypeError, builder.setPositionMap, (x,'hello'))
        self.assertRaises(TypeError, builder.setPositionMap, (x, []))
        self.assertRaises(TypeError, builder.setPositionMap, (x, 0))
        self.assertRaises(TypeError, builder.setPositionMap, (x, 0.))
        self.assertRaises(TypeError, builder.setPositionMap, (x, ()))
