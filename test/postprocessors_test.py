from unittest import TestCase
from source.postprocessors import *
import scipy.ndimage
class TestPostProcessNode(TestCase):
    def setUp(self) -> None:
        self.object=PostProcessNode()
    def test_generate_returnsList(self):
        dataset={}
        acq=[]
        def function(self,dataset,acq,*args,**kwargs):
            data={}
            data['null']=()
            return data
        self.object.function=function
        self.object.process(dataset,acq)


class TestPostProcessor(TestCase):
    def setUp(self) -> None:
        image=scipy.ndimage.imread('data/core/MLDatasetMasked/images/image_126.jpg')
        self.object = PostProcessor(data=image, acq=AcquisitionPlugin())
    def test_add_null_and_process_works(self):
        self.object.add('null')
        #d=self.object.compute()
    def test_add_many_process_works(self):
        self.object.add('null')
        self.object.add('null')
        d = self.object.get()
    def test_processsource_returnsSource(self):
        self.object.add('source')
        output=self.object.get()
        self.assertEqual(output['source'],self.object.data)
    def test_processPipeline_returnsdict(self):

        self.object.add('FishPipeline')
        output = self.object.get()



