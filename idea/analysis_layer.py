from layers import AnalysisLayer
from image_emulator import *
from distributed_computing import *
from apd import *
import  matplotlib.pyplot as plt

class AnalysisLayerPythonAutomation(AnalysisLayer):
    def CheckEmulatorZImage(self):
        N = 2
        imagePixSizeXY = [512 * N, 512 * N]
        numCellsSimulated = 5
        ROIImSize = [512, 512]
        emulator = ImageEmulator2Channel()
        image_folder = 'data/core/cell_library'
        emulator.loadImageFilePath(image_folder)
        emulator.setXYImageSize(ROIImSize)
        emulator.generateSimulatedPositions(imagePixSizeXY, numCellsSimulated)
        emulator = ImageEmulatorWrapper(system=emulator, isCached=False)
        emulator.tryLoadCache()
        xROIRange = range(N - 1)
        yROIRange = range(N - 1)
        xyROIOrigin = [0, 0]
        fig, ax = plt.subplots(1, 1)
        for z in range(-14, 14, 2):
            image = emulator.generate([0, 0, z])
            print("Z: {0}".format(z))
            print("Red Max: {0}".format(np.max(image[:, :, 0, 0])))
            print("Green Max: {0}".format(np.max(image[:, :, 0, 1])))
            shown_image = np.zeros([512, 512, 3])
            shown_image[:, :, 0] = image[:, :, 0, 0].astype('float') / 5000
            shown_image[:, :, 1] = image[:, :, 0, 1].astype('float') / 5000
            ax.imshow(shown_image)
            1 + 2
    def GridSearch_Simulated(self):
        apd = APDSystem()
        lib = APDFunctionLibrary()
        numROIXYSteps = 3
        imagePixSizeXY = [512 * numROIXYSteps, 512 * numROIXYSteps]
        numCellsSimulated = numROIXYSteps * numROIXYSteps * 2
        ROIImSize = [512, 512]
        emulator = ImageEmulator2Channel()
        image_folder = 'data/core/cell_library'
        emulator.loadImageFilePath(image_folder)
        emulator.setXYImageSize(ROIImSize)
        emulator.setAlpha([-1., .001, -.002])
        emulator.simulatePositions(imagePixSizeXY, numCellsSimulated)
        # emulator=ImageEmulatorWrapper(system=emulator,isCached=False)
        # emulator.tryLoadCache()
        xROIRange = range(numROIXYSteps - 1)
        yROIRange = range(numROIXYSteps - 1)
        xyROIOrigin = [0, 0]

        compute = DistributedComputeDaskTask('129.19.46.78:8786')
        # compute=DistributedComputeLocal()
        # compute=DistributedComputeDaskTask('localhost:8786')

        apdFunction = lib.findCellsInGrid(xROIRange, yROIRange, xyROIOrigin, ROIImSize,
                                          channels=['Channel', ['Cy5', 'DAPI'], [100., 100.]],
                                          laserIntensityRGBV=[6., 1., 5., 0.], zRange=[-7, 7, 1], timeRange=None,
                                          emulator=emulator, compute=compute)

        data=apd.run(apdFunction)
        return data

layer=AnalysisLayerPythonAutomation()
layer.runAndSave('GridSearch_Simulated')