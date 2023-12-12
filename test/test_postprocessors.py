from unittest import TestCase
from postprocessors import *
from ndtiff import NDTiffDataset

class TestProcessedData(TestCase):
    def setUp(self) -> None:
        self.object=ProcessedData()

    def test_domain(self):
        self.object[{'time':3,'position':0}]={'value1':4}
        value = self.object[{'time': 3, 'position': 0}]
        self.assertEqual(value,{'value1':4})
        self.object[{'time': 3, 'position': 0}] = {'value2':3}
        value = self.object[{'time': 3, 'position': 0}]
        self.assertEqual(value, {'value1':4,'value2':3})

    def test_set_notDict_raisesTypeError(self):
        items=[[],(),'h',7]
        for i in items:
            self.assertRaises(TypeError,self.object.__setitem__,{'t':0},i)


class TestPostProcessNode(TestCase):
    def setUp(self) -> None:
        self.object=PostProcessNode()
    def test_generate_returnsDictMap(self):
        data=NDTiffDataset(dataset_path='data/core/xyLooseGrid_1')
        acq=AcquisitionPlugin()
        def function(self,chunk,metadata):
            data={}
            data['null']=None
            return (chunk,data)
        self.object.function=function
        (value,output)=self.object.process(data,acq)
        self.assertIsInstance(value,NDTiffDataset)
        self.assertIsInstance(output, ProcessedData)
        data.close()

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

    def test_spotCount_returnsdata(self):
        node=self.object.get('spotCount')
        for image in self.images:
            data = node.process(image, self.acq)
            image.close()
'''
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
            '''


class TestPostProcessPipeline(TestCase):
    def setUp(self) -> None:
        self.images=self.images=[NDTiffDataset(dataset_path='data/core/xyLooseGrid_1'),
                     NDTiffDataset(dataset_path='data/core/xyLooseGrid_2'),
                     NDTiffDataset(dataset_path='data/core/xyLooseGrid_3'),
                     NDTiffDataset(dataset_path='data/core/xyLooseGrid_4'),
                     NDTiffDataset(dataset_path='data/core/xyLooseGrid_5')]
        self.object = PostProcessPipeline()

    def test_add_null_and_process_works(self):
        self.object.add('null')
        for image in self.images:
            d = self.object.process(image, AcquisitionPlugin())
            image.close()

    def test_add_many_process_works(self):
        self.object.add('null')
        self.object.add('mean')
        for image in self.images:
            d = self.object.process(image, AcquisitionPlugin())
            image.close()

    def test_processsource_returnsSource(self):
        self.object.add('source')
        for image in self.images:
            d = self.object.process(image, AcquisitionPlugin())
            image.close()

    def test_processmean_returnsMean(self):
        self.object.add('mean')
        for image in self.images:
            d = self.object.process(image, AcquisitionPlugin())
            image.close()

    def test_process_spotcount_returnsProrcessedData(self):
        self.object.add('spotCount')
        for image in self.images:
            d = self.object.process(image, AcquisitionPlugin())
            #self.assertEqual(d,ProcessedData)
            image.close()

    def test_processMask_squishaxes_returnsMask(self):
        self.object.add('mask')
        self.object.add('mask',squish_axes='channel',model_type='cyto')
        for i in range(len(self.images)): # only use image set 4 since it uses channels
            if i == 4:
                d = self.object.process(self.images[i], AcquisitionPlugin())
            self.images[i].close()

    def test_processmean_squishaxes_returnsMean(self):
        self.object.add('mean',squish_axes='channel')
        for i in range(len(self.images)): # only use image set 4 since it uses channels
            if i==4:
                d = self.object.process(self.images[i], AcquisitionPlugin())
            self.images[i].close()

    def test_process_spotCount_squishaxes_returnsMean(self):
        self.object.add('spotCount',squish_axes='channel')
        for i in range(len(self.images)): # only use image set 4 since it uses channels
            if i==4:
                d = self.object.process(self.images[i], AcquisitionPlugin())
            self.images[i].close()

    def test_processPipeline_returnsdict(self):
        self.object.add('fishPipeline')
        for image in self.images:
            #d = self.object.process(image, AcquisitionPlugin())
            image.close()




