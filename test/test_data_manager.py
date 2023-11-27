from data_manager import *
from authentication import *
from globals import Globals
import unittest
import os
from image_process import *
class TestIOManager(unittest.TestCase):
    def testDomain(self):
        io=IOManager()
        image1=io.load('data/test/testimage.jpg', classtype='ndarray')
        image2=io.load('data/test/testimage.jpg', classtype='MicroscopyImage')
        image1 = io.load('data/test/testimage.jpg')

        io.save('data/test/testimage2.tiff', image1)
        io.save('data/test/testimage2.png', image1)
        io.save('data/test/testimage2.jpg', image1)

        io.save('data/test/testimage2.tiff', image2)
        io.save('data/test/testimage2.png', image2)
        io.save('data/test/testimage2.jpg', image2)
        data=[0,[1,2,3,'h'],0.,'hello','h']
        for d in data:
            io.save('data/test/test.pkl',d)
            self.assertEqual(io.load('data/test/test.pkl'),d)
        myDict={"1":1,"2":2.,"3":'hello','dd':{'1':1},'d13123oii123o':{'3':1},
                "ddd":[123123123,12]}
        io.save('data/test/testdict.cfg',myDict)
        io.save('data/test/testdict2.acq', myDict)
        loadedDictionary=io.load('data/test/testdict.cfg')
        self.assertDictEqual(myDict,loadedDictionary)
        loadedDictionary = io.load('data/test/testdict2.acq')
        self.assertDictEqual(myDict, loadedDictionary)
    def testInterface(self):
        io=IOManager()
        io.load
        io.save

    def testAcceptance(self):
        #ALREADY DONE IN DOMAIN TEST
        pass

class TestDataManagerStorage(unittest.TestCase):
    def testDomain(self):
        dManager=DataManager()
        dManager.storage.folder=os.path.join('data','test')
        items=[1,1.,'h','h1llo']
        index=0
        for item in items:
            dManager.save(str(index)+'.pkl',item)
            index=index+1

class TestDataManagerLocal(unittest.TestCase):
    def testDomain(self):
        g=Globals('config.txt')
        datamanager = DataStorageLocal(g.DATA_CORE_PATH)
        key='test.pkl'
        values=[1,'hello',"123415",123432]
        for value in values:
            datamanager.save(key,value)
            loadedValue=datamanager.load(key)
            self.assertEqual(loadedValue,value)
        datamanager.find('*.pkl')
        datamanager.find('test.pkl')


'''
class TestDataManagerRemote(unittest.TestCase):
    def testDomain(self):
        datamanager = DataStorageRemoteSMB()
        datamanager.initialize('bitbio.org','mpmay','twinky1994','public','')
        key = 'test.pkl'
        values = [1, 'hello', "123415", 123432]
        for value in values:
            datamanager.save(key, value)
            loadedValue = datamanager.load(key)
            self.assertEqual(loadedValue, value)
        datamanager.close()
'''


class TestDataManagerCashe(unittest.TestCase):
    def testDomain(self):
        cache=DataManagerCache(size=2)
        values=[0,1.5,'hello']
        keys=['k1.pkl','k2.pkl','k3.pkl']
        for i in range(len(keys)):
            cache.save(keys[i],values[i])
        self.assertRaises(KeyError,cache.load,'k1')

class TestDataManager(unittest.TestCase):
    def testDomain(self):
        g=Globals('config.txt')
        dmanager=DataManager()
        dmanager.cache=DataManagerCache(size=50)
        dmanager.storage=DataStorageLocal(folder=g.DATA_CORE_PATH)
        dmanager.builder=DataBuilder()
        dmanager.load('test.pkl')
        dmanager.save('testval.pkl',{'hello':'world'})
        dmanager.storage.load('test.pkl') # check that the item is saved to storage after loading
        dmanager.cache.load('test.pkl')  # check that the item is saved to cache after loading

    def testAcceptance(self):
        g = Globals()
        dmanager = DataManager()
        dmanager.cache = DataManagerCache(size=50)
        dmanager.storage = DataStorageLocal(folder=g.DATA_CORE_PATH)
        dmanager.builder = DataBuilder()
        self.assertRaises(KeyError , dmanager.load,'badkey.pkl')
        self.assertRaises(TypeError, dmanager.load, 0)
        self.assertRaises(TypeError, dmanager.load, 0.)
        self.assertRaises(TypeError, dmanager.load, [])


class TestMultiDataManager(unittest.TestCase):
    def testDomain(self):
        mmanager=MultiDataManager()
        g = Globals()
        dmanager = DataManager()
        dmanager.cache = DataManagerCache(size=50)
        dmanager.storage = DataStorageLocal(folder=g.DATA_USER_PATH)
        dmanager.builder = DataBuilder()

        mmanager.addLocation(g.DATAKEY_USERDATA,dmanager)

        dmanager = DataManager()
        dmanager.cache = DataManagerCache(size=50)
        dmanager.storage = DataStorageLocal(folder=g.DATA_CORE_PATH)
        dmanager.builder = DataBuilder()
        mmanager.addLocation(g.DATAKEY_COREDATA,dmanager)
        mmanager.initialize()
        key='test.pkl'
        values=[1,2,3,[1,2,3],'hello',"hello",MicroscopyImage()]
        for value in values:
            mmanager[g.DATAKEY_USERDATA].save(key,value)
            mmanager[g.DATAKEY_COREDATA].save(key, value)

        dmanager.remote.clearcache()

    def testInterface(self):
        mmanager = MultiDataManager()
        mmanager.addLocation
        mmanager.initialize

    def testAcceptance(self):
        mmanager = MultiDataManager()
        g = Globals()
        dmanager = DataManager()
        dmanager.cache = DataManagerCache(size=50)
        dmanager.storage = DataStorageLocal(folder=g.DATA_USER_PATH)
        dmanager.builder = DataBuilder()

        mmanager.addLocation(g.DATAKEY_USERDATA, dmanager)
        mmanager.addLocation(g.DATAKEY_COREDATA, dmanager)
        self.assertRaises(KeyError, mmanager.addLocation,g.DATAKEY_USERDATA,dmanager)


class TestDataBuilder(unittest.TestCase):
    def testDomain(self):
        builder=DataBuilder()
        #builder.load('test')

    def testInterface(self):
        builder = DataBuilder()
        self.assertRaises(TypeError,builder.load,0)
        self.assertRaises(TypeError, builder.load, 0.)
        self.assertRaises(TypeError, builder.load,[])
        #self.assertEqual(builder.load('test'),'test')

class TestDataStorageRemote(unittest.TestCase):
    def setUp(self) -> None:
        self.object=DataStorageRemote()
    def test1(self):
        self.object.clearcache()
    def test2(self):
        self.object.load('data/core/MLDatasetMasked/images/image_0.jpg')
