import numpy as np

from data_manager import *
from globals import *
from calibration import *
g=Globals()
dataManager=DataStorageLocal()
dataManager.initialize(g.DATA_FOLDER)

dataManager.save('calibration:Magnification10' ,MatrixCalibration(matrix=[[1000./130.,0],[0,1000./130.]],zero=[0,0]))
dataManager.save('calibration:Magnification20' ,MatrixCalibration(matrix=[[500./130.,0],[0,500./130.]],zero=[0,0]))
dataManager.save('calibration:Magnification100',MatrixCalibration(matrix=[[100./130.,0],[0,100./130.]],zero=[0,0]))

calibrations=dict()
calibrations['calibration:Magnification10']=MatrixCalibration(matrix=[[1000./130.,0],[0,1000./130.]],zero=[0,0])
calibrations['calibration:Magnification20']=MatrixCalibration(matrix=[[500./130.,0],[0,500./130.]],zero=[0,0])
calibrations['calibration:Magnification100']=MatrixCalibration(matrix=[[100./130.,0],[0,100./130.]],zero=[0,0])
dataManager.save('calibration:multicalibration',calibrations)

multiCalibrator=MatrixMultiCalibrator()
for gi in [g.COORDINATES_VIEW,g.COORDINATES_STAGE,g.COORDINATES_GALVO,g.COORDINATES_PIXEL]:
    for gj in [g.COORDINATES_VIEW, g.COORDINATES_STAGE, g.COORDINATES_GALVO, g.COORDINATES_PIXEL]:
        for b in [1,2,4,8]:
            for m in g.MAGNIFICATIONS:
                key = gi + '_' + gj + '_' + str(int(b)) + '_' + m
                multiCalibrator.calibrations[key]=MatrixCalibration()
                if (gi==g.COORDINATES_VIEW)&(gj==g.COORDINATES_VIEW):
                    multiCalibrator.calibrations[key].setMatrix(np.identity(2))
                    multiCalibrator.calibrations[key].setZero(np.array([0,0]).T)
                elif (gi==g.COORDINATES_VIEW)&(gj==g.COORDINATES_STAGE):
                    pass
                elif (gi==g.COORDINATES_VIEW)&(gj==g.COORDINATES_GALVO):
                    pass
                elif (gi==g.COORDINATES_VIEW)&(gj==g.COORDINATES_PIXEL):
                    pass
                elif (gi==g.COORDINATES_VIEW)&(gj==g.COORDINATES_VIEW):
                    pass
                elif (gi==g.COORDINATES_VIEW)&(gj==g.COORDINATES_STAGE):
                    pass
                elif (gi==g.COORDINATES_VIEW)&(gj==g.COORDINATES_GALVO):
                    pass
                elif (gi==g.COORDINATES_VIEW)&(gj==g.COORDINATES_PIXEL):
                    pass
                elif (gi==g.COORDINATES_VIEW)&(gj==g.COORDINATES_VIEW):
                    pass
                elif (gi==g.COORDINATES_VIEW)&(gj==g.COORDINATES_STAGE):
                    pass
                elif (gi==g.COORDINATES_VIEW)&(gj==g.COORDINATES_GALVO):
                    pass
                elif (gi==g.COORDINATES_VIEW)&(gj==g.COORDINATES_VIEW):
                    pass
                elif (gi==g.COORDINATES_VIEW)&(gj==g.COORDINATES_VIEW):
                    pass
                elif (gi==g.COORDINATES_VIEW)&(gj==g.COORDINATES_VIEW):
                    pass
                elif (gi==g.COORDINATES_VIEW)&(gj==g.COORDINATES_VIEW):
                    pass
                elif (gi==g.COORDINATES_VIEW)&(gj==g.COORDINATES_VIEW):
                    pass
                elif (gi==g.COORDINATES_VIEW)&(gj==g.COORDINATES_VIEW):
                    pass
dataManager.save('calibration:multiCalibration',key)