import warnings
from skimage.measure import regionprops
from image_process import *
from cellpose import models
from cv2 import resize
class iBooleanClassifier:
    def detect(self,image):
        '''returns T/F if cell exists in image or not'''
        pass

class iMaskClassifier:
    def detect(self,image):
        '''returns T/F mask where cells exist'''
        pass

class CellDetectorThreshold(iBooleanClassifier):
    def __init__(self,pixelThreshold=None):
        self.pixelThreshold=pixelThreshold
        self.probabilityThreshold=0.25
    def detect(self,image):
        if not isinstance(image,np.ndarray):
            raise TypeError
        counts,binrange = np.histogram(image.flatten(),bins=np.arange(255))
        probability=counts/np.sum(counts)
        if not self.pixelThreshold:
            self.pixelThreshold=binrange[64]
        indicationLevel=np.sum(probability[self.pixelThreshold:])
        if indicationLevel>self.probabilityThreshold:
            isCell=True
        else:
            isCell=False
        return isCell

    def _getHistogram(self,image):
        frequency=dict()
        for i in range(image.shape[0]):
            for j in range(image.shape[1]):
                frequency[image[i,j]]=frequency[image[i,j]]

class CellDetectHistogramThreshold(iBooleanClassifier):
    rgbDecayThreshold=[.10, .10, .10]
    def __init__(self,threshold=None):
        if threshold:
            self.threshold=threshold
    def detect(self,image):
        imageDecayThreshold=self._getImageHistogramHalfDecay(image)
        isCellBool=True
        for i in range(len(imageDecayThreshold)):
            if imageDecayThreshold[i]<self.rgbDecayThreshold[i]:
                isCellBool=False
        return isCellBool


    def _getImageHistogramHalfDecay(self,image):
        imageDecayThreshold=[]
        for i in range(image.shape[2]):
            normImage=image[:,:,i]/np.max(np.max(image[:,:,i]))
            normImage=normImage.flatten()
            histogram,bin_edges =  np.histogram(normImage,bins=256,density=True)
            probability = histogram * np.diff(bin_edges)
            cumulativeProbability = np.cumsum(probability)
            index = np.min(np.where(cumulativeProbability>0.25))
            imageDecayThreshold.append(normImage[index])
        return imageDecayThreshold

class CellMaskCellpose(iMaskClassifier):
    dims=None
    modelType=None
    diameter=None
    channels=None
    flow_thereshold=None
    do_3d=None
    def __init__(self,dims=None,modelType=None,diameter=None,channels=None,flow_threshold=None,do_3D=None):
        self.dims=dims
        self.modelType=modelType
        self.diameter=diameter
        self.channels=channels
        self.flow_threshold=flow_threshold
        self.do_3D=do_3D
    def detect(self,image):
        if self.dims:
            image=self._binImageToDimSize(image)
        model=models.Cellpose(gpu=True,model_type=self.modelType)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore",category=RuntimeWarning)
            masks,flows,styles,diamters=model.eval(image,diameter=self.diameter,channels=self.channels,flow_threshold=self.flow_threshold,do_3D=self.do_3D)
        return masks

    def _binImageToDimSize(self,image):
        return resize(image,self.dims)

class CellCentroidCellpose(CellMaskCellpose):
    def detect(self,image):
        if self.dims:
            image=self._binImageToDimSize(image)
        model=models.Cellpose(gpu=True,model_type=self.modelType)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore",category=RuntimeWarning)
            masks,flows,styles,diamters=model.eval(image,diameter=self.diameter,channels=self.channels,flow_threshold=self.flow_threshold,do_3D=self.do_3D)
            props = regionprops(masks)
            centroids = props[0]['centroid']
        return centroids


class CellDetectorCellpose(iMaskClassifier):
    dims = None
    modelType = None
    diameter = None
    channels = None
    flow_thereshold = None
    do_3d = None

    def __init__(self, dims=None, modelType=None, diameter=None, channels=None, flow_threshold=None, do_3D=None):
        self.dims = dims
        self.modelType = modelType
        self.diameter = diameter
        self.channels = channels
        self.flow_threshold = flow_threshold
        self.do_3D = do_3D

    def detect(self, image):
        if self.dims:
            image = self._binImageToDimSize(image)
        model = models.Cellpose(gpu=True, model_type=self.modelType)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore",category=RuntimeWarning)
            mask, flows, styles, diamters = model.eval(image, diameter=self.diameter, channels=self.channels,
                                                    flow_threshold=self.flow_threshold, do_3D=self.do_3D)
        if np.sum(np.sum(mask))>(np.prod(self.dims)):
            isCell=True
        else:
            isCell=False
        return isCell

    def _binImageToDimSize(self,image):
        return resize(image,self.dims)
