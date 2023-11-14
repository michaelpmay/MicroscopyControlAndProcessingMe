from calibration import *
from data_manager import DataManager
import os
cBuilder=MatrixCalibrationBuilderFrom3Positions()
mCalibration=MatrixMultiCalibration()
#CALIBRATION EXPERIMENT FOR GALVO TO VIEW RESULTS BINNING N =[1,2,4,8]
nRange=[1,2,4,8]
for n in nRange:
    x=[[387,553],[587,553],[387,753]]
    y=[[512/n,512/n],[498/n,696/n],[328/n,501/n]]
    xZero=[387,553]
    yZero=[512/n,512/n]
    cBuilder.setPositionMap(x,y)
    cBuilder.isMovingObserver = False
    cBuilder.setZero(xZero,yZero)
    calibrationF=cBuilder.getForwardCalibration()
    mCalibration.addCalibration('View','Galvo',n,60,calibrationF)
    calibrationR=cBuilder.getReverseCalibration()
    mCalibration.addCalibration('Galvo','View',n,60,calibrationR)

#EXPERIMENT FOR VIEW TO STAGE RESULTS BINNING N =[1,2,4,8]
nRange=[1,2,4,8]
for n in nRange:
    x=[[0,0],[20,0],[0,20]]
    y=[[580/n,558/n],[576/n,706/n],[426/n,554/n]]
    xZero=[0,0]
    yZero=[0/n,0/n]
    cBuilder.setPositionMap(x,y)
    cBuilder.isMovingObserver=True
    cBuilder.setZero(xZero, yZero)
    calibrationF=cBuilder.getForwardCalibration()
    mCalibration.addCalibration('View','Stage',n,60,calibrationF)
    calibrationR=cBuilder.getReverseCalibration()
    mCalibration.addCalibration('Stage','View',n,60,calibrationR)

#EXPERIMENT FOR PIXEL to VIEW RESULTS BINNING N =[1,2,4,8]
nRange=[1,2,4,8]
for n in nRange:
    x=[[0/n,0/n],[1/n,0/n],[0/n,1/n]]
    y=[[0/n,0/n],[0/n,1/n],[-1/n,0/n]]
    xZero=[1024/n,1024/n]
    yZero=[0/n,0/n]
    cBuilder.setPositionMap(x,y)
    cBuilder.isMovingObserver = False
    cBuilder.setZero(xZero,yZero)
    calibrationF=cBuilder.getForwardCalibration()
    mCalibration.addCalibration('View','Pixel',n,60,calibrationF)
    calibrationR=cBuilder.getReverseCalibration()
    mCalibration.addCalibration('Pixel','View',n,60,calibrationR)

dManager=DataManager()
dManager.storage.folder=os.path.join('data','core')
dManager.save('calibration.mcal',mCalibration)