from apd import *
from calibration import *
from pycromanager import Core
apd=APDSystem()
lib=APDFunctionLibrary()
numROIXYSteps=9
imagePixSizeXY = [512*numROIXYSteps, 512*numROIXYSteps]
ROIImSize=[512,512]

xROIRange=range(numROIXYSteps-1)
yROIRange=range(numROIXYSteps-1)

xROIRange=[-10,-5,0,5,10]
yROIRange=[-10,-5,0,5,10]

xyROIOrigin=[0,0]
ViewToStageXYCalibrator=MatrixCalibration()
ViewToStageXYCalibrator.setMatrix([[.123,0],[0,.123]])
ViewToStageXYCalibrator.setZero([256,256])
zOrigin=-0
apdFunction=lib.findCellsInGrid(xROIRange,yROIRange,xyROIOrigin,ROIImSize,channels=['Filter',['Red', 'Green'],[100.,100.]],laserIntensityRGBV=[6.,1.,5.,0.],zRange=[-7.+zOrigin,7.+zOrigin,1.],timeRange=None,emulator=None,calibrator=ViewToStageXYCalibrator)

apd.run(apdFunction)
#emulator.saveCache()
