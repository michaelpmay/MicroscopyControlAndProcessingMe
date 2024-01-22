from environment import *
from decision import *
from acquisition import AcquisitionPluginLibrary
from postprocessors import PostProcessPipeline
from calibration import NullCalibration
from distributed_computing import DistributedComputeLocal
from verbosity import Verbosity
class iAPDFunction:
    def run(self):
        pass
class iAPDSystem:
    pass
class iAPDSystemLibrary:
    def list(self):
        pass
    def get(self,key, *args, **kwargs):
        pass
class APDFunction:
    def __init__(self,*args,**kwargs):
        if len(args)==1:
            f=args[0]
        elif len(args)==0:
            f=lambda system:None
        elif len(args) >= 2:
            f = args[0]
            args=args[1:]
        else:
            raise ValueError
        self.f = f
        self.fargs = args
        self.fkwargs = kwargs
    def run(self,system):
        self.f(system,*self.fargs, **self.fkwargs)
    def setf(self,f):
        if not callable(f):
            raise TypeError
        self.f=f
class APDSystem:
    def __init__(self,configFileName='myConfig.cfg',rootDataFolder='',authentication='local',user='default'):
        self.initializeBackend(configFileName=configFileName,rootPath=rootDataFolder,authentication=authentication,user=user)
        self.apdfunction=APDFunction()
        self.distributed=DistributedComputeLocal()
        self.chain=[]
    def initializeBackend(self,configFileName='myConfig.cfg',rootPath='',authentication='local',user='default'):
        builder = EnvironmentBuilder()
        builder.setInterface('headless')  # headless or gui
        # before you go here mount the samba share and point to 'Z:\\Users\\Michael'
        # connect to \\munsky-nas.engr.colostate.edu\share and map as Z drive  before running this line
        # builder.setRootDataPath('Z:\\Users\\Michael') #sets the root folder for the held data use windows to mount the Z drive with nas!
        builder.setRootDataPath(rootPath)  # current directory
        builder.setAuthentication(authentication)  # local, or NoPassword
        builder.setUser(user, '')
        builder.setConfiguration(configFileName=configFileName)
        builder.clearAcquisitionCache()
        self.backend = builder.getEnvironment().backend


    def runFunction(self,function,*args,**kwargs):
        self.backend.connectDevices()
        dataset=function.run(self,*args,**kwargs)
        self.backend.disconnectDevices()
        return dataset

    def loadFunction(self,key):
        if isinstance(key,str):
            lib=APDFunctionLibrary()
            f=lib.get(key)
            self.apdfunction=f
        elif isinstance(key,APDFunction):
            self.apdfunction=key
        else:
            raise TypeError

    def linkAPD(self,acquisition,process,decision,saveInitialImages=None,saveDataset=None,saveFinalImages=None):
        if not isinstance(acquisition,AcquisitionPlugin):
            raise TypeError
        if not isinstance(process, PostProcessPipeline):
            raise TypeError
        if not isinstance(decision,iDecision):
            raise TypeError
        settings={'saveInitialImages':saveInitialImages,'saveDataset':saveDataset,'saveFinalImages':saveFinalImages}
        self.chain.append([acquisition,process,decision,settings])

    def run(self):
        for i in range(len(self.chain)):
            [acquisition, processor, decision,settings]=self.chain[i]
            images=self.acquire(acquisition)
            if settings['saveInitialImages']:
                self.backend.datamanager.put(images,settings['saveInitialImages'])
            dataset=processor.process(images,acquisition)
            print(dataset)
            if settings['saveDataset']:
                self.backend.datamanager.put(dataset,settings['saveDataset'])
            new_acquisition=decision.propose(dataset,acquisition)
            if new_acquisition:
                self.acquire(new_acquisition)
                if settings['saveFinalImages']:
                    self.backend.datamanager.put(images, settings['saveFinalImages'])

    def acquire(self,acquisition):
        dataset = self.backend.acquire(acquisition)
        return dataset
class APDFunctionLzbrary(iAPDSystemLibrary):
    def list(self):
        apdList = [attribute for attribute in dir(self)
                      if callable(getattr(self, attribute))
                      and attribute.startswith('__') is False]
        return apdList


    def get(self,key,*args,**kwargs):
        if not isinstance(key,str):
            raise TypeError
        command='self.'+key+"(*args,**kwargs)"

        process=eval(command)
        return process


    def null(self):
        pipeline=APDFunction()
        def f(self):
            pass
        pipeline.f=f
        return pipeline

    def hello_world(self):
        pipeline = APDFunction()
        def f(self):
            #print('helloworld')
            pass
        pipeline.f = f
        return pipeline

    def print(self,string):
        pipeline = APDFunction()
        def f(self):
            #print(self.args[0])
            pass
        pipeline.f = f
        pipeline.fargs=(string)
        return pipeline

    def findNCells(self, N):
        #todo
        pass

    def findNCellsAndTimeSeriesImage(self, N):
        #todo
        pass

    def findNCellsAndSnapshotImage(self, N):
        #todo
        pass

    def findCellsInGrid(self,xRangeROI,yRangeROI,xyOriginROI,ROIImSize,channels=None,zRange=None,timeRange=None,laserIntensityRGBV=None,emulator=None,calibration=NullCalibration(),model_type='cyto',compute=DistributedComputeLocal(),show_display=True,split_roi=False):
        pipeline = APDFunction()

        def f(self):
            if emulator is not None:
                self.backend.loadAcquisition('image_emulator', emulator)
            else:
                self.backend.loadAcquisition('default')
            data={}
            if laserIntensityRGBV:
                try:
                    for i in range(laserIntensityRGBV):
                        self.backend.devices[g.KEY_DEVICE_LASERS].setLaserPowerInWatts(laserIntensityRGBV[i])
                except:
                    #print("Warning Setting Laser Failed")
                    pass
            lib=AcquisitionPluginLibrary()
            self.backend.acquisition=lib.xyLooseGrid(xRangeROI,yRangeROI,xyOriginROI,name='exampleMileStone1_Part1',calibration=calibration,show_display=show_display)
            dataset = self.backend.acquireAndReturnDataset()
            processor = PostProcessPipeline(data=dataset, acq=self.backend.acquisition,computer=compute)
            processor.add('fovMeanIntensity',isSorted=True)
            processor.add('cellDetectSpotLocationsInRoiDoughnut')
            processor.add('cellDetectNumCellsInRoi',default_flow_threshold = .1,MINIMUM_CELL_AREA = 30,model_type=model_type)
            processed_data = processor.get()
            data.update(processed_data)
            g=Globals()
            self.backend.datamanager[g.DATAKEY_USERDATA].save('milestone1processeddata1.pkl',processed_data)
            decision = DecisionPickROIFromMask(numCellsThreshold = 1)
            if split_roi:
                acquisitions=decision.propose(processed_data, self.backend.acquisition, zRange=zRange, timeRange=timeRange,channels=channels,split_roi=split_roi)
                #print("lenA={0}".format(len(acquisitions)))
                for i in range(len(acquisitions)):
                    self.backend.acquisition=acquisitions[i]
                    self.backend.acquisition.settings.name = 'exampleMileStone1_Part2_ROI'+str(i)
                    #print("AcqSeq".format(self.backend.acquisition.events.xy_positions))
                    dataset = self.backend.acquireAndReturnDataset()

            else:
                self.backend.acquisition = decision.propose(processed_data, self.backend.acquisition,zRange=zRange,timeRange=timeRange,channels=channels)
                self.backend.acquisition.settings.name='exampleMileStone1_Part2'
                dataset = self.backend.acquireAndReturnDataset()
            time.sleep(.1)
            processor = PostProcessPipeline(data=dataset, acq=self.backend.acquisition,computer=compute)
            processor.add('sharpestZ')
            processed_data = processor.get()
            #print(processed_data)
            self.backend.datamanager[g.DATAKEY_USERDATA].save('milestone1processeddata2.pkl', processed_data)
            decision=DecisionSelectOptimalZPlaneFromSharpestZ()
            self.backend.acquisition =decision.propose(processed_data, self.backend.acquisition)
            self.backend.acquisition.settings.name = 'exampleMileStone1_Part3'
            dataset = self.backend.acquire(self.backend.acquisition)
            return dataset

        pipeline.f = f
        return pipeline

    def findNCellsInGridNoZ(self,xRangeROI,yRangeROI,xyOriginROI,MaxNumCells=10,channels=None,zRange=None,timeRange=None,laserIntensityRGBV=None,emulator=None,calibration=NullCalibration(),model_type='cyto',compute=DistributedComputeLocal(),show_display=True,split_roi=True):
        pipeline = APDFunction()

        def f(self):
            g = Globals()
            if emulator is not None:
                self.backend.loadAcquisition('image_emulator', emulator)
            else:
                self.backend.loadAcquisition('default')
            data={}
            if laserIntensityRGBV:
                try:
                    for i in range(laserIntensityRGBV):
                        self.backend.devices[g.KEY_DEVICE_LASERS].setLaserPowerInWatts(laserIntensityRGBV[i])
                except:
                    #print("Warning Setting Laser Failed")
                    pass
            lib=AcquisitionPluginLibrary()
            self.backend.acquisition=lib.xyLooseGrid(xRangeROI,yRangeROI,xyOriginROI,name='findNCellsInGridNoZ_Part1',calibration=calibration,show_display=show_display)
            dataset = self.backend.acquire(self.backend.acquisition)
            processor = PostProcessPipeline(computer=compute)
            processor.add('fovMeanIntensity',isSorted=True)
            processor.add('cellDetectSpotLocationsInRoiDoughnut')
            processor.add('cellDetectNumCellsInRoi',default_flow_threshold = .1,MINIMUM_CELL_AREA = 30,model_type=model_type)
            processed_data = processor.process(dataset,self.backend.acquisition)
            data.update(processed_data)
            self.backend.datamanager[g.DATAKEY_USERDATA].save('findNCellsInGridNoZ.pkl',processed_data)
            decision = DecisionPickROIFromMask(numCellsThreshold = 1)
            self.backend.acquisition = decision.propose(processed_data, self.backend.acquisition,
                                                            zRange=zRange, timeRange=timeRange, channels=channels,
                                                            maxNumCells=MaxNumCells)
            currentTime = time.time()
            if split_roi:
                sequence=self.backend.acquisition.events.xy_positions
                for i in range(len(sequence)):
                    self.backend.acquisition.events.xy_positions=[sequence[i]]
                    self.backend.acquisition.settings.name = 'findNCellsInGridNoZ_'+str(i)
                    dataset = self.backend.acquire(self.backend.acquisition)
            else:
                self.backend.acquisition.settings.name = 'findNCellsInGridNoZ_Part2'
                dataset = self.backend.acquire(self.backend.acquisition)
            return dataset

        pipeline.f = f
        return pipeline

    def findTranscriptionSitesInGrid(self,xRangeROI,yRangeROI,xyOriginROI,ROIImSize,threshold=50,channels=None,zRange=None,timeRange=None,laserIntensityRGBV=None,emulator=None,calibration=NullCalibration(),model_type='cyto'):
        pipeline = APDFunction()

        def f(self):
            if emulator is not None:
                self.backend.loadAcquisition('image_emulator', emulator)
            else:
                self.backend.loadAcquisition('default')
            g=Globals()
            if laserIntensityRGBV:
                try:
                    for i in range(laserIntensityRGBV):
                        self.backend.devices[g.KEY_DEVICE_LASERS].setLaserPowerInWatts(laserIntensityRGBV[i])
                except:
                    print("Warning Setting Laser Failed")
            lib=AcquisitionPluginLibrary()
            self.backend.acquisition=lib.xyLooseGrid(xRangeROI,yRangeROI,xyOriginROI,name='exampleMileStone1_Part1',calibration=calibration)
            print(self.backend.acquisition.events.xy_positions)
            dataset = self.backend.acquire(self.backend.acquisition)
            processor = PostProcessPipeline()
            processor.add('cellDetectSpotLocationsInRoiDoughnut',sigma=[3,8])
            processor.add('cellDetectNumCellsInRoi',default_flow_threshold = .1,MINIMUM_CELL_AREA = 30,model_type=model_type)
            processor.process(dataset, self.backend.acquisition)
            processed_data = processor.get()

            self.backend.datamanager[g.DATAKEY_USERDATA].save('findTranscriptionSitesInGrid1.pkl',processed_data)
            decision = DecisionPickROIFromXYSpotLocations(numCellsThreshold = 1)
            self.backend.acquisition = decision.propose(processed_data, self.backend.acquisition,zRange=zRange,timeRange=timeRange,channels=channels)
            print(self.backend.acquisition.events.xy_positions)
            self.backend.acquisition.settings.name='findTranscriptionSitesInGrid2'
            dataset = self.backend.acquire(self.backend.acquisition)
            return dataset


        pipeline.f = f
        return pipeline

    def findNumCells(self,xRangeROI,yRangeROI,xyOriginROI,ROIImSize,channels=None,zRange=None,timeRange=None,laserIntensityRGBV=None,emulator=None,calibration=NullCalibration(),model_type='cyto',compute=DistributedComputeLocal(),show_display=True):
        pipeline = APDFunction()

        def f(self):
            if emulator is not None:
                self.backend.loadAcquisition('image_emulator', emulator)
            else:
                self.backend.loadAcquisition('default')
            g = Globals()
            if laserIntensityRGBV:
                try:
                    for i in range(laserIntensityRGBV):
                        self.backend.devices[g.KEY_DEVICE_LASERS].setLaserPowerInWatts(laserIntensityRGBV[i])
                except:
                    print("Warning Setting Laser Failed")
            lib=AcquisitionPluginLibrary()
            self.backend.acquisition=lib.xyLooseGrid(xRangeROI,yRangeROI,xyOriginROI,name='findNumCells_Part1',calibration=calibration,show_display=show_display)
            dataset = self.backend.acquireAndReturnDataset()
            processor = PostProcessPipeline(computer=compute)
            processor.add('cellDetectNumCellsInRoi',default_flow_threshold = .1,MINIMUM_CELL_AREA = 30,model_type=model_type)
            processed_data = processor.process(dataset,self.backend.acquisition)
            #print('DetectedNumCells={0}'.format(processed_data['cellDetectNumCellsInRoi']['numcells']))
            #print('DetectedIndex={0}'.format(processed_data['cellDetectNumCellsInRoi']['index']))
            return processed_data
        pipeline.f = f
        return pipeline

    def findNPunctaInGridNoZ(self, xRangeROI, yRangeROI, xyOriginROI, channels=None, zRange=None,
                            timeRange=None, laserIntensityRGBV=None, emulator=None, calibration=NullCalibration(),
                            threshold=50, compute=DistributedComputeLocal(), show_display=True, split_roi=True):
        pipeline = APDFunction()

        def f(self):
            if emulator is not None:
                self.backend.loadAcquisition('image_emulator', emulator)
            else:
                self.backend.loadAcquisition('default')
            data = {}
            if laserIntensityRGBV:
                try:
                    for i in range(laserIntensityRGBV):
                        self.backend.devices[g.KEY_DEVICE_LASERS].setLaserPowerInWatts(laserIntensityRGBV[i])
                except:
                    print("Warning Setting Laser Failed")
            lib = AcquisitionPluginLibrary()
            self.backend.acquisition = lib.xyLooseGrid(xRangeROI, yRangeROI, xyOriginROI,
                                                           name='findNPunctaInGridNoZ_Part1', calibration=calibration,
                                                           show_display=show_display)
            dataset = self.backend.acquire(self.backend.acquisition)
            processor = PostProcessPipeline(computer=compute)
            processor.add('fovMeanIntensity', isSorted=True)
            processor.add('SpotDetectImagesBooleanDoughnut',threshold=threshold)
            processed_data=processor.process(dataset, self.backend.acquisition)
            data.update(processed_data)
            g = Globals()
            self.backend.datamanager[g.DATAKEY_USERDATA].save('findNPunctaInGridNoZ.pkl', processed_data)
            decision = DecisionPickXYROIFromDetectionBoolean()
            self.backend.acquisition = decision.propose(processed_data, self.backend.acquisition,
                                                            zRange=zRange, timeRange=timeRange, channels=channels)
            if split_roi:
                sequence = self.backend.acquisition.events.xy_positions
                for i in range(len(sequence)):
                    self.backend.acquisition.events.xy_positions = [sequence[i]]
                    self.backend.acquisition.settings.name = 'findNPunctaInGridNoZ' + str(i)
                    dataset = self.backend.acquire(self.backend.acquisition)
            else:
                self.backend.acquisition.settings.name = 'findNPunctaInGridNoZ'
                dataset = self.backend.acquire(self.backend.acquisition)
                self.backend.acquisition.settings.name = 'findNPunctaInGridNoZ_Part2'
            return dataset

        pipeline.f = f
        return pipeline

    def findPunctaInGrid(self,xRangeROI,yRangeROI,xyOriginROI,ROIImSize,channels=None,zRange=None,timeRange=None,laserIntensityRGBV=None,emulator=None,calibration=NullCalibration(),model_type='cyto',compute=DistributedComputeLocal(),show_display=True,split_roi=False):
        pipeline = APDFunction()

        def f(self):
            if emulator is not None:
                self.backend.loadAcquisition('image_emulator', emulator)
            else:
                self.backend.loadAcquisition('default')
            data={}
            if laserIntensityRGBV:
                try:
                    for i in range(laserIntensityRGBV):
                        self.backend.devices[g.KEY_DEVICE_LASERS].setLaserPowerInWatts(laserIntensityRGBV[i])
                except:
                    print("Warning Setting Laser Failed")
            lib=AcquisitionPluginLibrary()
            self.backend.acquisition=lib.xyLooseGrid(xRangeROI,yRangeROI,xyOriginROI,name='findPunctaInGrid_Part1',calibration=calibration,show_display=show_display)
            dataset = self.backend.acquireAndReturnDataset()
            processor = PostProcessPipeline(computer=compute)
            processor.add('fovMeanIntensity',isSorted=True)
            processor.add('cellDetectSpotLocationsInRoiDoughnut')
            processed_data = processor.process(dataset, self.backend.acquisition)
            data.update(processed_data)
            g=Globals()
            self.backend.datamanager[g.DATAKEY_USERDATA].save('findPunctaInGrid.pkl',processed_data)
            decision = DecisionPickROIFromXYSpotLocations()
            if split_roi:
                acquisitions=decision.propose(processed_data, self.backend.acquisition, zRange=zRange, timeRange=timeRange,channels=channels,split_roi=split_roi)
                print("lenA={0}".format(len(acquisitions)))
                for i in range(len(acquisitions)):
                    self.backend.acquisition=acquisitions[i]
                    self.backend.acquisition.settings.name = 'findPunctaInGrid_Part2_ROI'+str(i)
                    print("AcqSeq".format(self.backend.acquisition.events.xy_positions))
                    dataset = self.backend.acquireAndReturnDataset()

            else:
                self.backend.acquisition = decision.propose(processed_data, self.backend.acquisition,zRange=zRange,timeRange=timeRange,channels=channels)
                self.backend.acquisition.settings.name='findPunctaInGrid_Part2'
                dataset = self.backend.acquireAndReturnDataset()
            time.sleep(.1)
            processor = PostProcessPipeline(computer=compute)
            processor.add('sharpestZ')
            processed_data = processor.get(dataset,self.backend.acquisition)
            self.backend.datamanager[g.DATAKEY_USERDATA].save('findPunctaInGrid2.pkl', processed_data)
            decision=DecisionSelectOptimalZPlaneFromSharpestZ()
            self.backend.acquisition =decision.propose(processed_data, self.backend.acquisition)
            self.backend.acquisition.settings.name = 'findPunctaInGrid_Part3'
            dataset = self.backend.acquire(self.backend.acquisition)
            return dataset

        pipeline.f = f
        return pipeline

    def acquireAndFishPipeline(self,xRangeROI,yRangeROI,xyOriginROI,ROIImSize,channels=None,zRange=None,timeRange=None,laserIntensityRGBV=None,emulator=None,calibration=NullCalibration(),model_type='cyto',compute=DistributedComputeLocal(),show_display=True,split_roi=False):
        pipeline = APDFunction()

        def f(self):
            if emulator is not None:
                self.backend.loadAcquisition('image_emulator', emulator)
            else:
                self.backend.loadAcquisition('default')
            data={}
            if laserIntensityRGBV:
                try:
                    for i in range(laserIntensityRGBV):
                        self.backend.devices[g.KEY_DEVICE_LASERS].setLaserPowerInWatts(laserIntensityRGBV[i])
                except:
                    print("Warning Setting Laser Failed")
            lib=AcquisitionPluginLibrary()
            self.backend.acquisition=lib.xyLooseGrid(xRangeROI,yRangeROI,xyOriginROI,name='exampleMileStone1_Part1',calibration=calibration,show_display=show_display)
            dataset = self.backend.acquireAndReturnDataset()
            processor = PostProcessPipeline(data=dataset, acq=self.backend.acquisition,computer=compute)
            processor.add('fovMeanIntensity',isSorted=True)
            processor.add('cellDetectSpotLocationsInRoiDoughnut')
            processor.add('cellDetectNumCellsInRoi',default_flow_threshold = .1,MINIMUM_CELL_AREA = 30,model_type=model_type)
            processed_data = processor.get()
            data.update(processed_data)
            g=Globals()
            self.backend.datamanager[g.DATAKEY_USERDATA].save('milestone1processeddata1.pkl',processed_data)
            decision = DecisionPickROIFromMask(numCellsThreshold = 1)
            if split_roi:
                acquisitions=decision.propose(processed_data, self.backend.acquisition, zRange=zRange, timeRange=timeRange,channels=channels,split_roi=split_roi)
                print("lenA={0}".format(len(acquisitions)))
                for i in range(len(acquisitions)):
                    self.backend.acquisition=acquisitions[i]
                    self.backend.acquisition.settings.name = 'exampleMileStone1_Part2_ROI'+str(i)
                    print("AcqSeq".format(self.backend.acquisition.events.xy_positions))
                    dataset = self.backend.acquireAndReturnDataset()

            else:
                self.backend.acquisition = decision.propose(processed_data, self.backend.acquisition,zRange=zRange,timeRange=timeRange,channels=channels)
                self.backend.acquisition.settings.name='exampleMileStone1_Part2'
                dataset = self.backend.acquireAndReturnDataset()
            time.sleep(.1)
            processor = PostProcessPipeline(data=dataset, acq=self.backend.acquisition,computer=compute)
            processor.add('fishPipeline')
            processed_data = processor.get()
            print(processed_data)
            self.backend.datamanager[g.DATAKEY_USERDATA].save('milestone1processeddata2.pkl', processed_data)
            decision=DecisionSelectOptimalZPlaneFromSharpestZ()
            self.backend.acquisition =decision.propose(processed_data, self.backend.acquisition)
            self.backend.acquisition.settings.name = 'exampleMileStone1_Part3'
            dataset = self.backend.acquireAndReturnDataset()
            return dataset

        pipeline.f = f
        return pipeline