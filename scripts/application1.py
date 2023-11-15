from source.apd import *
from source.image_emulator import TestImageEmulator, ImageEmulator2Channel,ImageEmulatorWrapper
from source.calibration import  MatrixCalibration

## Terminator Scope Config with remote NAS
apd=APDSystem(configFileName='myConfig.cfg',rootDataFolder='Z:\\Users\\Michael')

calibration=MatrixCalibration()
calibration.setMatrix([[512,0],[0,512]])
calibration.setZero([0,0])

xROIRange=range(-1,1,1)
yROIRange=range(-1,1,1)
xyROIOrigin=[0,0]

lib=APDFunctionLibrary()
apdFunction=lib.findTranscriptionSitesInGrid(xROIRange,yROIRange,xyROIOrigin,threshold=200,channel=['Channel',['Cy5', 'DAPI'],[100.,100.]],
laserIntensityRGBV=[6.,1.,5.,0.],zRange=None,timeRange=[2,1.],emulator=None,calibration=calibration)
apd.run(apdFunction)
