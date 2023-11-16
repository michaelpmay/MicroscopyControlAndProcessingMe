from unittest import TestCase
from source.postprocessors import *
import imageio
from ndtiff import NDTiffDataset
class TestPostProcessNode(TestCase):
    def setUp(self) -> None:
        self.object=PostProcessNode()
    def test_generate_returnsList(self):
        dataset={}
        acq=AcquisitionPlugin()
        def function(self,dataset,acq,*args,**kwargs):
            data={}
            data['null']=()
            return data
        self.object.function=function
        self.object.process(dataset,acq)

class TestPostProcessorNodeLibrary(TestCase):
    def setUp(self) -> None:
        self.images=[NDTiffDataset(dataset_path='data/core/xyLooseGrid_1'),
                     NDTiffDataset(dataset_path='data/core/xyLooseGrid_2'),
                     NDTiffDataset(dataset_path='data/core/xyLooseGrid_3'),
                     NDTiffDataset(dataset_path='data/core/xyLooseGrid_4'),
                     NDTiffDataset(dataset_path='data/core/xyLooseGrid_5')]
        self.acq=AcquisitionPlugin()
        self.object=PostProcessLibrary()

    def test_null_returnsNone(self):
        node=self.object.get('null')
        for image in self.images:
            data=node.process(image,self.acq)
            image.close()

    def test_source_returnsdata(self):
        node=self.object.get('source')
        for image in self.images:
            data = node.process(image, self.acq)
            image.close()

    def test_fovMeanIntensity_returnsdata(self):
        node=self.object.get('fovMeanIntensity')
        for image in self.images:
            data = node.process(image, self.acq)
            image.close()

    def test_cellDetectNumCellsInRoi_returnsdata(self):
        node=self.object.get('cellDetectNumCellsInRoi')
        for image in self.images:
            data = node.process(image, self.acq)
            image.close()

    def test_cellDetectSpotLocationsInRoi_returnsdata(self):
        node=self.object.get('cellDetectSpotLocationsInRoi')
        for image in self.images:
            data = node.process(image, self.acq)
            image.close()

    def test_cellDetectSpotLocationsInRoiDoughnut_returnsdata(self):
        node = self.object.get('cellDetectSpotLocationsInRoiDoughnut')
        for image in self.images:
            data = node.process(image, self.acq)
            image.close()


class TestPostProcessor(TestCase):
    def setUp(self) -> None:
        self.images=self.images=[NDTiffDataset(dataset_path='data/core/xyLooseGrid_1'),
                     NDTiffDataset(dataset_path='data/core/xyLooseGrid_2'),
                     NDTiffDataset(dataset_path='data/core/xyLooseGrid_3'),
                     NDTiffDataset(dataset_path='data/core/xyLooseGrid_4'),
                     NDTiffDataset(dataset_path='data/core/xyLooseGrid_5')]
        self.object = PostProcessor()
    def test_add_null_and_process_works(self):
        self.object.add('null')
        #d=self.object.compute()
    def test_add_many_process_works(self):
        self.object.add('null')
        self.object.add('null')
        for image in self.images:
            d = self.object.process(image, AcquisitionPlugin())
            image.close()
    def test_processsource_returnsSource(self):
        self.object.add('source')
        for image in self.images:
            d = self.object.process(image, AcquisitionPlugin())
            image.close()
    def test_processPipeline_returnsdict(self):
        self.object.add('fishPipeline')
        for image in self.images:
            #d = self.object.process(image, AcquisitionPlugin())
            image.close()




