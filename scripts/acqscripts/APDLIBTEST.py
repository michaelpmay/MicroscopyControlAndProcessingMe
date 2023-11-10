from apd import *
apd=APDSystem()
lib=APDFunctionLibrary()
minNumCells=100
image = np.array(Image.open('data/test/testimage.jpg'))
emulator=ImageEmulatorFromArray(image=image[:, :, 0],isGaussianZImageDistort=True)
apdFunction=lib.FindNCellsAndImage(minNumCells,channels=[['Filter'],['DAPI','Cy5','Rhodamine'],[100.,100.,100.]],laserIntensityRGBV=[6.,1.,5.,0.],ZRange=[-2.,1.,1.],TimeRange=[3,0.],emulator=emulator)
apd.run(apdFunction)