import numpy as np

from data_manager import *
from calibration import *
from globals import *
import os
g=Globals()
datamanager=DataStorageLocal()
datamanager.initialize(g.DATA_FOLDER)
calibration=MatrixCalibration()
calibration.setMatrix(np.array([[1,0],[0,1]]))
calibration.setZero(np.array([0,0]).T)
magnifications=['Magnification10','Magnification20','Magnification100',]
conversions=['Pixel','Galvo','Stage','View']
if os.path.isdir('data/calibration/'):
    pass
else:
    os.mkdir('data/calibration/')
for mag in magnifications:
    if mag=='PixelMagnification10':
        M=np.array([[1000./1300.,0],[0,1000./1300.]])
        Z=np.array([0, 0]).T
    elif mag=='PixelMagnification20':
        M=np.array([[1000./1300.,0],[0,1000./1300.]])*2
        Z=np.array([0, 0]).T
    elif mag=='PixelMagnification100':
        M=np.array([[1000./1300.,0],[0,1000./1300.]])*10
        Z=np.array([0, 0]).T
    print(M)
    calibration.setMatrix(M)
    calibration.setZero(Z)
    key='calibration/'+mag+'_Stage'
    datamanager.save(key,calibration)
    cal=datamanager.load(key)
    cal.map(np.array([0,0]).T)

for bin in bins:
    M=np.array([[1.,0.],[0.,-1.]])
    if bin=='Binning1':
        Z=np.array([0, 512.]).T
    elif bin=='Binning2':
        Z=np.array([0, 256.]).T
    elif bin=='Binning4':
        Z=np.array([0, 128.]).T
    elif bin=='Binning8':
        Z=np.array([0, 64.]).T
    key = 'calibration/Pixel' +bin + '_View'
    calibration.setMatrix(M)
    calibration.setZero(Z)
    datamanager.save(key, calibration)
    cal = datamanager.load(key)
    cal.map(np.array([0, 0]).T)