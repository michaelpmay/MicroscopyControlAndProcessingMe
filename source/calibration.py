import numpy as np
from globals import Globals
g=Globals('config.txt')
class iCalibration:
    def map(self,position):
        """defines forward mathemqtecal transform from one coordinate system to new"""
        pass


class iMatrixCalibration(iCalibration):
    '''MatrixCalibraiton is a type of map that assumes a matrix method'''
    def map(self,position):
        """defines forward mathemqtecal transform from one coordinate system to new"""
        return position

    def calibrate(self,inputs,output):
        """craeates zeros and matrices such that input output relationship is satisfied"""
        pass
    def setMatrix(self,matrix):
        """sets the forward and inverse matrix"""
        pass
    def setZero(self,zero):
        """sets the constant of calibration"""
        pass
    def getMatrix(self):
        """returns the matrix"""
        pass
    def getZero(self):
        """returns the zero. this function is somtimes monkey-patched to get the stage position and can be complex"""
        pass
    def proeprties(self):
        """returns the state of the calibration as a dictionary so that it can be saved in text"""
        pass
    def load(self,proprties):
        """changes self according to a dictionary of properties"""
        pass


class MatrixCalibration(iMatrixCalibration):
    matrix=None
    zero=None
    def __init__(self,matrix=None,zero=None):
        self.setMatrix(matrix)
        self.setZero(zero)
    def map(self,position):
        if not isinstance(position,(np.ndarray,list)):
            raise TypeError
        if isinstance(position,list):
            position=np.array(position)
        position = self.matrix @ (position ) + self.zero
        return position.tolist()

    def mapList(self,positions):
        if not isinstance(positions, list):
            raise TypeError('Positions must be a list of positions')
        mappedPositions=[]
        for p in positions:
            mappedPositions.append(self.map(p))
        return mappedPositions

    def setMatrix(self,matrix):
        if matrix is None:
            self.matrix = matrix
            return
        if isinstance(matrix,list):
            matrix=np.array(matrix)
        if not isinstance(matrix,np.ndarray):
            raise TypeError

        if matrix.size==0:
            raise TypeError
        self.matrix=matrix
    def setZero(self,zero):
        if zero is None:
            self.zero=zero
            return
        if isinstance(zero,list):
            zero=np.array(zero)
        if not isinstance(zero,np.ndarray):
            raise TypeError
        if zero.size==0:
            raise TypeError
        self.zero=zero


    def getZero(self):
        return self.zero1

    def getMatrix(self):
        return self.matrix

    @property
    def properties(self):
        props=dict()
        if isinstance(self.matrix,np.ndarray):
            props['Matrix [NbyN float]'] = self.matrix.tolist()
        else:
            props['Matrix [NbyN float]'] = self.matrix
        if isinstance(self.zero,np.ndarray):
            props['Zero [N float]']=self.zero.tolist()
        else:
            props['Zero [N float]'] =self.zero
        return props

    def load(self,props):
        self.matrix=props['Matrix [NbyN float]']
        self.zero=props['Zero [N float]']

class MatrixCalibrationBuilderFrom3Positions:
    calibration=None
    x=None
    y=None
    isMovingObserver=None
    def __init__(self):
        self.calibration=MatrixCalibration()
        self.x=None
        self.y=None
        self.isMovingObserver=False
    def setPositionMap(self,x,y):
        if not isinstance(x,list):
            raise TypeError('x must be a list')
        if not isinstance(y,list):
            raise TypeError('y must be a list')
        if (len(x)==0) or (len(y)==0):
            raise TypeError('length x and y must be greater than 0 and equal in length')
        if len(x) != len(y):
            raise TypeError('length x and y must be greater than 0 and equal in length')
        for i in range(len(x)):
            if len(x[i])==0:
                raise TypeError('length x and y must be greater than 0 and equal in length')
            if len(y[i])==0:
                raise TypeError('length x and y must be greater than 0 and equal in length')
        for i in range(len(x)):
            if len(x[i])!=len(x[0]):
                raise TypeError('length x and y elements must be equal')
            if len(y[i])!=len(y[0]):
                raise TypeError('length x and y elements must be equal')

        self.x=np.array(x)
        self.y=np.array(y)
    def setZero(self,x,y):
        if not isinstance(x,list):
            raise TypeError('x must be a list')
        if not isinstance(y,list):
            raise TypeError('y must be a list')
        if (len(x)==0) or (len(y)==0):
            raise TypeError('length x and y must be greater than 0 and equal in length')
        if len(x) != len(y):
            raise TypeError('length x and y must be greater than 0 and equal in length')
        self.xZero=np.array(x)
        self.yZero=np.array(y)
    def getReverseCalibration(self):
        if self.x is None:
            raise ValueError('setPositionMap before getting calibration')
        if self.y is None:
            raise ValueError('setPositionMap before getting calibration')
        X = np.zeros((len(self.x[0]), len(self.y[0])))
        Y = np.zeros((len(self.x[0]), len(self.y[0])))
        for k in range(1,len(self.x)):
            if not self.isMovingObserver:
                X[:,k-1] = self.x[k]-self.x[0]
                Y[:,k-1] = self.y[k]-self.y[0]
            else:
                X[:, k - 1] = self.x[0] - self.x[k]
                Y[:, k - 1] = self.y[0] - self.y[k]
        M=Y@np.linalg.pinv(X)
        Z=-M @ self.xZero+self.yZero
        calibration=MatrixCalibration()
        calibration.setMatrix(M)
        calibration.setZero(Z)
        return calibration
    def getForwardCalibration(self):
        if self.x is None:
            raise ValueError('setPositionMap before getting calibration')
        if self.y is None:
            raise ValueError('setPositionMap before getting calibration')
        X = np.zeros((len(self.x[0]), len(self.y[0])))
        Y = np.zeros((len(self.x[0]), len(self.y[0])))
        for k in range(1, len(self.x)):
            if not self.isMovingObserver:
                X[:, k - 1] = self.x[k] - self.x[0]
                Y[:, k - 1] = self.y[k] - self.y[0]
            else:
                X[:, k - 1] = self.x[0] - self.x[k]
                Y[:, k - 1] = self.y[0] - self.y[k]
        M = Y @ np.linalg.pinv(X)
        Z = -M @ self.x[0] + self.y[0]

        invM=np.linalg.inv(M)
        invZ = -invM @ self.yZero + self.xZero
        calibration = MatrixCalibration()
        calibration.setMatrix(invM)
        calibration.setZero(invZ)
        return calibration

class NullCalibration(iMatrixCalibration):
    '''Special instance of calibration that returns the position unchanged'''
    def map(self,position):
        return position

    def mapList(self,positionList):
        return positionList


class iMultiCalibrator:
    '''an object which utilizes mutltiple calibrations to quickly implement mutliple transformations. Chains of transformations are performed'''
    def calibrate(self,fromCoords,ToCoords,position):
        '''returns the position in  '''
        pass

class MatrixMultiCalibration(iMultiCalibrator):
    calibrations=None
    activeCalibration=None
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MatrixMultiCalibration, cls).__new__(
                cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.binning = 1
        self.magnification=None
        self.calibrations= {}

    def addCalibration(self,fromCoords,toCoords,binning,magnification,calibrationObject):
        coordinates = [g.COORDINATES_PIXEL, g.COORDINATES_GALVO, g.COORDINATES_STAGE, g.COORDINATES_VIEW]
        if not isinstance(fromCoords,str):
            raise TypeError
        if not isinstance(toCoords,str):
            raise TypeError
        if not isinstance(binning,int):
            raise TypeError
        if not isinstance(magnification,int):
            raise TypeError
        if fromCoords not in coordinates:
            raise ValueError('From coordintes key must be in the set of coordinates')
        if toCoords not in coordinates:
            raise ValueError('From coordintes key must be in the set of coordinates')
        if not isinstance(calibrationObject,MatrixCalibration):
            raise TypeError('calibration must be a calibration')
        key=self._createKey(fromCoords,toCoords,binning,magnification)
        self.calibrations[key]=calibrationObject


    def setCalibration(self,fromCoords,toCoords,binning,magnification):
        coordinates = [g.COORDINATES_PIXEL, g.COORDINATES_GALVO, g.COORDINATES_STAGE, g.COORDINATES_VIEW]
        if not isinstance(fromCoords,str):
            raise TypeError
        if not isinstance(toCoords,str):
            raise TypeError
        if fromCoords not in coordinates:
            raise ValueError('From coordintes key must be in the set of coordinates')
        if toCoords not in coordinates:
            raise ValueError('From coordintes key must be in the set of coordinates')
        if not isinstance(binning,int):
            raise ValueError('Binning must me int')
        if not isinstance(magnification,int):
            raise ValueError('Magnification must be int')
        if fromCoords==toCoords:
            self.activeCalibration=NullCalibration()
        else:
            key=self._createKey(fromCoords,toCoords,binning,magnification)
            self.activeCalibration=self.calibrations[key]

    def getCalibration(self,fromCoords,toCoords,binning,magnification):
        coordinates = [g.COORDINATES_PIXEL, g.COORDINATES_GALVO, g.COORDINATES_STAGE, g.COORDINATES_VIEW]
        if not isinstance(fromCoords,str):
            raise TypeError
        if not isinstance(toCoords,str):
            raise TypeError
        if fromCoords not in coordinates:
            raise ValueError('From coordintes key must be in the set of coordinates')
        if toCoords not in coordinates:
            raise ValueError('From coordintes key must be in the set of coordinates')
        if not isinstance(binning,int):
            raise ValueError('Binning must me int')
        if not isinstance(magnification,int):
            raise ValueError('Magnification must be int')
        key=self._createKey(fromCoords,toCoords,binning,magnification)
        return self.calibrations[key]

    def map(self,position):
        if not isinstance(position,list):
            raise TypeError('Position must be a list of integers or ints')
        calibrator=self.activeCalibration
        return calibrator.map(position)

    def mapList(self,positions):
        if not isinstance(positions, list):
            raise TypeError('Positions must be a list of positions')
        mappedPositions=[]
        for p in positions:
            mappedPositions.append(self.map(p))
        return mappedPositions

    def _createKey(self,fromCoords,toCoords,binning,magnification):
        key = fromCoords + '_' + toCoords + '_' + str(int(binning)) + '_' + str(magnification)
        return key

    def listCalibrations(self):
        calibrationPropertiesList=[]
        for key in self.calibrations.keys():
            properties=self._parseKey(key)
            calibrationPropertiesList.append(properties)
        return calibrationPropertiesList

    def _parseKey(self,key):
        key=key.split('_')
        fromCoords=key[0]
        toCoords=key[1]
        binning=key[2]
        magnification=key[3]
        return (fromCoords,toCoords,binning,magnification)

    @property
    def properties(self):
        props={}
        for key in self.calibrations.keys():
            calibrationProperties=self.calibrations[key].properties
            props[key]=calibrationProperties
        return props

    def load(self,props):
        if not isinstance(props,dict):
            raise TypeError("Load properties must be dict")
        for key in props.keys():
            calibration=MatrixCalibration()
            calibration.load(props[key])
            self.calibrations[key]=calibration
