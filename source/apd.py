from source.environment import *
from source.decision import *
from source.acquisition import AcquisitionPluginLibrary
from source.postprocessors import PostProcessor
from source.calibration import NullCalibration
from source.distributed_computing import DistributedComputeLocal
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
    def __init__(self,configFileName='myConfig.cfg',rootPath='',authentication='local'):
        self.initializeEnvironment(configFileName=configFileName,rootPath=rootPath,authentication=authentication)
        self.apdfunction=APDFunction()
        self.distributed=DistributedComputeLocal()
    def initializeEnvironment(self,configFileName='myConfig.cfg',rootPath='',authentication='local'):
        builder = EnvironmentBuilder()
        builder.setInterface('headless')  # headless or gui
        # before you go here mount the samba share and point to 'Z:\\Users\\Michael'
        # connect to \\munsky-nas.engr.colostate.edu\share and map as Z drive  before running this line
        # builder.setRootDataPath('Z:\\Users\\Michael') #sets the root folder for the held data use windows to mount the Z drive with nas!
        builder.setRootDataPath(rootPath)  # current directory
        builder.setAuthentication(authentication)  # local, or NoPassword
        builder.setUser('default', '')
        builder.setConfiguration(configFileName=configFileName)
        builder.clearAcquisitionCache()
        self.env = builder.getEnvironment()

    def run(self,function,*args,**kwargs):
        self.env.backend.connectDevices()
        dataset=function.run(self,*args,**kwargs)
        self.env.backend.disconnectDevices()
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

class APDFunctionLibrary(iAPDSystemLibrary):
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
        pass

    def findNCellsAndTimeSeriesImage(self, N):
        pass

    def findNCellsAndSnapshotImage(self, N):
        pass

    def findCellsInGrid(self,xRangeROI,yRangeROI,xyOriginROI,ROIImSize,channels=None,zRange=None,timeRange=None,laserIntensityRGBV=None,emulator=None,calibration=NullCalibration(),model_type='cyto',compute=DistributedComputeLocal(),show_display=True,split_roi=False):
        pipeline = APDFunction()

        def f(self):
            if emulator is not None:
                self.env.backend.loadAcquisition('image_emulator', emulator)
            else:
                self.env.backend.loadAcquisition('default')
            data={}
            if laserIntensityRGBV:
                try:
                    for i in range(laserIntensityRGBV):
                        self.env.backend.devices[g.KEY_DEVICE_LASERS].setLaserPowerInWatts(laserIntensityRGBV[i])
                except:
                    #print("Warning Setting Laser Failed")
                    pass
            lib=AcquisitionPluginLibrary()
            self.env.backend.acquisition=lib.xyLooseGrid(xRangeROI,yRangeROI,xyOriginROI,name='exampleMileStone1_Part1',calibration=calibration,show_display=show_display)
            dataset = self.env.backend.acquireAndReturnDataset()
            processor = PostProcessor(data=dataset, acq=self.env.backend.acquisition,computer=compute)
            processor.add('fovMeanIntensity',isSorted=True)
            processor.add('cellDetectSpotLocationsInRoiDoughnut')
            processor.add('cellDetectNumCellsInRoi',default_flow_threshold = .1,MINIMUM_CELL_AREA = 30,model_type=model_type)
            processed_data = processor.get()
            data.update(processed_data)
            g=Globals()
            self.env.backend.datamanager[g.DATAKEY_USERDATA].save('milestone1processeddata1.pkl',processed_data)
            decision = DecisionPickROIFromMask(numCellsThreshold = 1)
            if split_roi:
                acquisitions=decision.propose(processed_data, self.env.backend.acquisition, zRange=zRange, timeRange=timeRange,channels=channels,split_roi=split_roi)
                #print("lenA={0}".format(len(acquisitions)))
                for i in range(len(acquisitions)):
                    self.env.backend.acquisition=acquisitions[i]
                    self.env.backend.acquisition.settings.name = 'exampleMileStone1_Part2_ROI'+str(i)
                    #print("AcqSeq".format(self.env.backend.acquisition.events.xy_positions))
                    dataset = self.env.backend.acquireAndReturnDataset()

            else:
                self.env.backend.acquisition = decision.propose(processed_data, self.env.backend.acquisition,zRange=zRange,timeRange=timeRange,channels=channels)
                self.env.backend.acquisition.settings.name='exampleMileStone1_Part2'
                dataset = self.env.backend.acquireAndReturnDataset()
            time.sleep(.1)
            processor = PostProcessor(data=dataset, acq=self.env.backend.acquisition,computer=compute)
            processor.add('sharpestZ')
            processed_data = processor.get()
            #print(processed_data)
            self.env.backend.datamanager[g.DATAKEY_USERDATA].save('milestone1processeddata2.pkl', processed_data)
            decision=DecisionSelectOptimalZPlaneFromSharpestZ()
            self.env.backend.acquisition =decision.propose(processed_data, self.env.backend.acquisition)
            self.env.backend.acquisition.settings.name = 'exampleMileStone1_Part3'
            dataset = self.env.backend.acquireAndReturnDataset()
            return dataset

        pipeline.f = f
        return pipeline

    def findNCellsInGridNoZ(self,xRangeROI,yRangeROI,xyOriginROI,MaxNumCells,channels=None,zRange=None,timeRange=None,laserIntensityRGBV=None,emulator=None,calibration=NullCalibration(),model_type='cyto',compute=DistributedComputeLocal(),show_display=True,split_roi=True):
        pipeline = APDFunction()

        def f(self):
            if emulator is not None:
                self.env.backend.loadAcquisition('image_emulator', emulator)
            else:
                self.env.backend.loadAcquisition('default')
            data={}
            if laserIntensityRGBV:
                try:
                    for i in range(laserIntensityRGBV):
                        self.env.backend.devices[g.KEY_DEVICE_LASERS].setLaserPowerInWatts(laserIntensityRGBV[i])
                except:
                    #print("Warning Setting Laser Failed")
                    pass
            lib=AcquisitionPluginLibrary()
            self.env.backend.acquisition=lib.xyLooseGrid(xRangeROI,yRangeROI,xyOriginROI,name='exampleMileStone1_Part1',calibration=calibration,show_display=show_display)
            currentTime=time.time()
            dataset = self.env.backend.acquireAndReturnDataset()
            #print('FindingTime={0}'.format(time.time()-currentTime))
            processor = PostProcessor(data=dataset, acq=self.env.backend.acquisition,computer=compute)
            currentTime = time.time()
            processor.add('fovMeanIntensity',isSorted=True)
            processor.add('cellDetectSpotLocationsInRoiDoughnut')
            processor.add('cellDetectNumCellsInRoi',default_flow_threshold = .1,MINIMUM_CELL_AREA = 30,model_type=model_type)
            processed_data = processor.get()
            #print('ProcessingTime={0}'.format(time.time() - currentTime))
            data.update(processed_data)
            g=Globals()
            self.env.backend.datamanager[g.DATAKEY_USERDATA].save('findCellsInGridNoZ1.pkl',processed_data)
            decision = DecisionPickROIFromMask(numCellsThreshold = 1)
            self.env.backend.acquisition = decision.propose(processed_data, self.env.backend.acquisition,
                                                            zRange=zRange, timeRange=timeRange, channels=channels,
                                                            maxNumCells=MaxNumCells)
            currentTime = time.time()
            if split_roi:
                sequence=self.env.backend.acquisition.events.xy_positions
                for i in range(len(sequence)):
                    self.env.backend.acquisition.events.xy_positions=[sequence[i]]
                    self.env.backend.acquisition.settings.name = 'findCellsInGridNoZ2ROI'+str(i)
                    dataset = self.env.backend.acquireAndReturnDataset()
                    print(self.env.backend.acquisition.events.xy_positions)
            else:
                self.env.backend.acquisition.settings.name = 'findCellsInGridNo2'
                dataset = self.env.backend.acquireAndReturnDataset()
                print(self.env.backend.acquisition.events.xy_positions)
                self.env.backend.acquisition.settings.name='exampleMileStone1_Part2'
            print('ImagingTime={0}'.format(time.time() - currentTime))
            return dataset

        pipeline.f = f
        return pipeline

    def findTranscriptionSitesInGrid(self,xRangeROI,yRangeROI,xyOriginROI,ROIImSize,threshold=50,channels=None,zRange=None,timeRange=None,laserIntensityRGBV=None,emulator=None,calibration=NullCalibration(),model_type='cyto'):
        pipeline = APDFunction()

        def f(self):
            if emulator is not None:
                self.env.backend.loadAcquisition('image_emulator', emulator)
            else:
                self.env.backend.loadAcquisition('default')
            g=Globals()
            if laserIntensityRGBV:
                try:
                    for i in range(laserIntensityRGBV):
                        self.env.backend.devices[g.KEY_DEVICE_LASERS].setLaserPowerInWatts(laserIntensityRGBV[i])
                except:
                    print("Warning Setting Laser Failed")
            lib=AcquisitionPluginLibrary()
            self.env.backend.acquisition=lib.xyLooseGrid(xRangeROI,yRangeROI,xyOriginROI,name='exampleMileStone1_Part1',calibration=calibration)
            print(self.env.backend.acquisition.events.xy_positions)
            dataset = self.env.backend.acquireAndReturnDataset()
            processor = PostProcessor(data=dataset, acq=self.env.backend.acquisition)
            processor.add('cellDetectSpotLocationsInRoiDoughnut',sigma=[3,8])
            processor.add('cellDetectNumCellsInRoi',default_flow_threshold = .1,MINIMUM_CELL_AREA = 30,model_type=model_type)
            processed_data = processor.get()

            self.env.backend.datamanager[g.DATAKEY_USERDATA].save('findTranscriptionSitesInGrid1.pkl',processed_data)
            decision = DecisionPickROIFromXYSpotLocations(numCellsThreshold = 1)
            self.env.backend.acquisition = decision.propose(processed_data, self.env.backend.acquisition,zRange=zRange,timeRange=timeRange,channels=channels)
            print(self.env.backend.acquisition.events.xy_positions)
            self.env.backend.acquisition.settings.name='findTranscriptionSitesInGrid2'
            dataset = self.env.backend.acquireAndReturnDataset()
            return dataset


        pipeline.f = f
        return pipeline

    def findNumCells(self,xRangeROI,yRangeROI,xyOriginROI,ROIImSize,channels=None,zRange=None,timeRange=None,laserIntensityRGBV=None,emulator=None,calibration=NullCalibration(),model_type='cyto',compute=DistributedComputeLocal(),show_display=True):
        pipeline = APDFunction()

        def f(self):
            if emulator is not None:
                self.env.backend.loadAcquisition('image_emulator', emulator)
            else:
                self.env.backend.loadAcquisition('default')
            g = Globals()
            if laserIntensityRGBV:
                try:
                    for i in range(laserIntensityRGBV):
                        self.env.backend.devices[g.KEY_DEVICE_LASERS].setLaserPowerInWatts(laserIntensityRGBV[i])
                except:
                    print("Warning Setting Laser Failed")
            lib=AcquisitionPluginLibrary()
            self.env.backend.acquisition=lib.xyLooseGrid(xRangeROI,yRangeROI,xyOriginROI,name='findNumCells_Part1',calibration=calibration,show_display=show_display)
            dataset = self.env.backend.acquireAndReturnDataset()
            processor = PostProcessor(data=dataset, acq=self.env.backend.acquisition,computer=compute)
            processor.add('cellDetectNumCellsInRoi',default_flow_threshold = .1,MINIMUM_CELL_AREA = 30,model_type=model_type)
            processed_data = processor.get()
            print('DetectedNumCells={0}'.format(processed_data['cellDetectNumCellsInRoi']['numcells']))
            print('DetectedIndex={0}'.format(processed_data['cellDetectNumCellsInRoi']['index']))
            return processed_data
        pipeline.f = f
        return pipeline

    def findNPunctaInGridNoZ(self, xRangeROI, yRangeROI, xyOriginROI, channels=None, zRange=None,
                            timeRange=None, laserIntensityRGBV=None, emulator=None, calibration=NullCalibration(),
                            threshold=50, compute=DistributedComputeLocal(), show_display=True, split_roi=True):
        pipeline = APDFunction()

        def f(self):
            if emulator is not None:
                self.env.backend.loadAcquisition('image_emulator', emulator)
            else:
                self.env.backend.loadAcquisition('default')
            data = {}
            if laserIntensityRGBV:
                try:
                    for i in range(laserIntensityRGBV):
                        self.env.backend.devices[g.KEY_DEVICE_LASERS].setLaserPowerInWatts(laserIntensityRGBV[i])
                except:
                    print("Warning Setting Laser Failed")
            lib = AcquisitionPluginLibrary()
            self.env.backend.acquisition = lib.xyLooseGrid(xRangeROI, yRangeROI, xyOriginROI,
                                                           name='exampleMileStone1_Part1', calibration=calibration,
                                                           show_display=show_display)
            currentTime = time.time()
            dataset = self.env.backend.acquireAndReturnDataset()
            print('FindingTime={0}'.format(time.time() - currentTime))
            processor = PostProcessor(data=dataset, acq=self.env.backend.acquisition, computer=compute)
            currentTime = time.time()
            processor.add('fovMeanIntensity', isSorted=True)
            processor.add('SpotDetectImagesBooleanDoughnut',threshold=threshold)
            processed_data = processor.get()
            print('ProcessingTime={0}'.format(time.time() - currentTime))
            data.update(processed_data)
            g = Globals()
            self.env.backend.datamanager[g.DATAKEY_USERDATA].save('findCellsInGridNoZ1.pkl', processed_data)
            decision = DecisionPickXYROIFromDetectionBoolean()
            self.env.backend.acquisition = decision.propose(processed_data, self.env.backend.acquisition,
                                                            zRange=zRange, timeRange=timeRange, channels=channels)
            currentTime = time.time()
            if split_roi:
                sequence = self.env.backend.acquisition.events.xy_positions
                for i in range(len(sequence)):
                    self.env.backend.acquisition.events.xy_positions = [sequence[i]]
                    self.env.backend.acquisition.settings.name = 'findCellsInGridNoZ2ROI' + str(i)
                    dataset = self.env.backend.acquireAndReturnDataset()
                    print(self.env.backend.acquisition.events.xy_positions)
            else:
                self.env.backend.acquisition.settings.name = 'findCellsInGridNo2'
                dataset = self.env.backend.acquireAndReturnDataset()
                print(self.env.backend.acquisition.events.xy_positions)
                self.env.backend.acquisition.settings.name = 'exampleMileStone1_Part2'
            print('ImagingTime={0}'.format(time.time() - currentTime))
            return dataset

        pipeline.f = f
        return pipeline

    def findPunctaInGrid(self,xRangeROI,yRangeROI,xyOriginROI,ROIImSize,channels=None,zRange=None,timeRange=None,laserIntensityRGBV=None,emulator=None,calibration=NullCalibration(),model_type='cyto',compute=DistributedComputeLocal(),show_display=True,split_roi=False):
        pipeline = APDFunction()

        def f(self):
            if emulator is not None:
                self.env.backend.loadAcquisition('image_emulator', emulator)
            else:
                self.env.backend.loadAcquisition('default')
            data={}
            if laserIntensityRGBV:
                try:
                    for i in range(laserIntensityRGBV):
                        self.env.backend.devices[g.KEY_DEVICE_LASERS].setLaserPowerInWatts(laserIntensityRGBV[i])
                except:
                    print("Warning Setting Laser Failed")
            lib=AcquisitionPluginLibrary()
            self.env.backend.acquisition=lib.xyLooseGrid(xRangeROI,yRangeROI,xyOriginROI,name='exampleMileStone1_Part1',calibration=calibration,show_display=show_display)
            dataset = self.env.backend.acquireAndReturnDataset()
            processor = PostProcessor(data=dataset, acq=self.env.backend.acquisition,computer=compute)
            processor.add('fovMeanIntensity',isSorted=True)
            processor.add('cellDetectSpotLocationsInRoiDoughnut')
            processed_data = processor.get()
            data.update(processed_data)
            g=Globals()
            self.env.backend.datamanager[g.DATAKEY_USERDATA].save('milestone1processeddata1.pkl',processed_data)
            decision = DecisionPickROIFromXYSpotLocations()
            if split_roi:
                acquisitions=decision.propose(processed_data, self.env.backend.acquisition, zRange=zRange, timeRange=timeRange,channels=channels,split_roi=split_roi)
                print("lenA={0}".format(len(acquisitions)))
                for i in range(len(acquisitions)):
                    self.env.backend.acquisition=acquisitions[i]
                    self.env.backend.acquisition.settings.name = 'exampleMileStone1_Part2_ROI'+str(i)
                    print("AcqSeq".format(self.env.backend.acquisition.events.xy_positions))
                    dataset = self.env.backend.acquireAndReturnDataset()

            else:
                self.env.backend.acquisition = decision.propose(processed_data, self.env.backend.acquisition,zRange=zRange,timeRange=timeRange,channels=channels)
                self.env.backend.acquisition.settings.name='exampleMileStone1_Part2'
                dataset = self.env.backend.acquireAndReturnDataset()
            time.sleep(.1)
            processor = PostProcessor(data=dataset, acq=self.env.backend.acquisition,computer=compute)
            processor.add('sharpestZ')
            processed_data = processor.get()
            print(processed_data)
            self.env.backend.datamanager[g.DATAKEY_USERDATA].save('milestone1processeddata2.pkl', processed_data)
            decision=DecisionSelectOptimalZPlaneFromSharpestZ()
            self.env.backend.acquisition =decision.propose(processed_data, self.env.backend.acquisition)
            self.env.backend.acquisition.settings.name = 'exampleMileStone1_Part3'
            dataset = self.env.backend.acquireAndReturnDataset()
            return dataset

        pipeline.f = f
        return pipeline

    def acquireAndFishPipeline(self,xRangeROI,yRangeROI,xyOriginROI,ROIImSize,channels=None,zRange=None,timeRange=None,laserIntensityRGBV=None,emulator=None,calibration=NullCalibration(),model_type='cyto',compute=DistributedComputeLocal(),show_display=True,split_roi=False):
        pipeline = APDFunction()

        def f(self):
            if emulator is not None:
                self.env.backend.loadAcquisition('image_emulator', emulator)
            else:
                self.env.backend.loadAcquisition('default')
            data={}
            if laserIntensityRGBV:
                try:
                    for i in range(laserIntensityRGBV):
                        self.env.backend.devices[g.KEY_DEVICE_LASERS].setLaserPowerInWatts(laserIntensityRGBV[i])
                except:
                    print("Warning Setting Laser Failed")
            lib=AcquisitionPluginLibrary()
            self.env.backend.acquisition=lib.xyLooseGrid(xRangeROI,yRangeROI,xyOriginROI,name='exampleMileStone1_Part1',calibration=calibration,show_display=show_display)
            dataset = self.env.backend.acquireAndReturnDataset()
            processor = PostProcessor(data=dataset, acq=self.env.backend.acquisition,computer=compute)
            processor.add('fovMeanIntensity',isSorted=True)
            processor.add('cellDetectSpotLocationsInRoiDoughnut')
            processor.add('cellDetectNumCellsInRoi',default_flow_threshold = .1,MINIMUM_CELL_AREA = 30,model_type=model_type)
            processed_data = processor.get()
            data.update(processed_data)
            g=Globals()
            self.env.backend.datamanager[g.DATAKEY_USERDATA].save('milestone1processeddata1.pkl',processed_data)
            decision = DecisionPickROIFromMask(numCellsThreshold = 1)
            if split_roi:
                acquisitions=decision.propose(processed_data, self.env.backend.acquisition, zRange=zRange, timeRange=timeRange,channels=channels,split_roi=split_roi)
                print("lenA={0}".format(len(acquisitions)))
                for i in range(len(acquisitions)):
                    self.env.backend.acquisition=acquisitions[i]
                    self.env.backend.acquisition.settings.name = 'exampleMileStone1_Part2_ROI'+str(i)
                    print("AcqSeq".format(self.env.backend.acquisition.events.xy_positions))
                    dataset = self.env.backend.acquireAndReturnDataset()

            else:
                self.env.backend.acquisition = decision.propose(processed_data, self.env.backend.acquisition,zRange=zRange,timeRange=timeRange,channels=channels)
                self.env.backend.acquisition.settings.name='exampleMileStone1_Part2'
                dataset = self.env.backend.acquireAndReturnDataset()
            time.sleep(.1)
            processor = PostProcessor(data=dataset, acq=self.env.backend.acquisition,computer=compute)
            processor.add('fishPipeline')
            processed_data = processor.get()
            print(processed_data)
            self.env.backend.datamanager[g.DATAKEY_USERDATA].save('milestone1processeddata2.pkl', processed_data)
            decision=DecisionSelectOptimalZPlaneFromSharpestZ()
            self.env.backend.acquisition =decision.propose(processed_data, self.env.backend.acquisition)
            self.env.backend.acquisition.settings.name = 'exampleMileStone1_Part3'
            dataset = self.env.backend.acquireAndReturnDataset()
            return dataset

        pipeline.f = f
        return pipeline