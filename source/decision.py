from acquisition import AcquisitionPlugin
from image_process import CellDetectorCellMask
from model import Model
import numpy as np
from utility import ZPlaneEstimator,ZSearchXYPositionOptimizerFull,ZSearchXYPositionOptimizerGreedy

class iDecision:
    def propose(self,processed_data,acquisition):
        '''take old acquisition and processed data dictionary and propose a new experiment'''
        return


class Decision(iDecision):
    def __init__(self,function=None,acquisition=None):
        self.function=function
    def propose(self,processed_data,acquisition):
        return self.function(self,processed_data,acquisition)

class DecisionLibrary:
    def get(self,key,args,kwargs):
        return None

    def list(self):
        pass

    def null(self):
        def function(self, processed_data, acquisition):
            return None
        decision=Decision(function=function)
        return decision

    def repeat(self):
        def function(self, processed_data, acquisition):
            return acquisition
        decision = Decision(function=function)
        return decision

    def threshhold(self,key,value):
        def function(self, processed_data, acquisition):
            return None

        decision = Decision(function=function)
        return decision

    def pickSharpest(self):
        def function(self, processed_data, acquisition):
            for i in range(len(processed_data)):
                pass
            return None

        decision = Decision(function=function)
        return decision

    def pickROI(self,numCells=1):
        def function(processed_data, acquisition):
            return None

        decision = Decision(function=function)
        return decision


class DecisionIfThen(iDecision):
    def __init__(self):
        self.logic=lambda:None
        self.rule=lambda:None

    def propose(self,processed_data,acquisition):
        logicBool=self.logic(processed_data,acquisition)
        if logicBool:
            return self.rule(logicBool,processed_data,acquisition)

    def always(self):
        self.logic=True
        return self

    def never(self):
        self.logic=False
        return self

    def repeat(self):
        def function(data,acq):
            return acq
        self.rule=function

    def IfThreshHoldLessThan(self,key,value):
        return self

    def IfThreshHoldGreaterThan(self,key,value):
        return self

class DecisionNull(iDecision):
    def propose(self,processed_data,acquisition):
        return None


class DecisionThreshold(iDecision):
    def __init__(self,key,threshold):
        self.key=key
        self.threshold=threshold
    def propose(self,processed_data,acquisition):
        if not isinstance(processed_data,list):
            raise TypeError
        if not isinstance(acquisition,AcquisitionPlugin):
            raise TypeError
        return acquisition

class DecisionRepeatAcquisition(iDecision):
    def propose(self,processed_data,acquisition):
        if not isinstance(processed_data,list):
            raise TypeError
        if not isinstance(acquisition,AcquisitionPlugin):
            raise TypeError
        return acquisition

class DecisionAdjustLaserIntensity(iDecision):
    def __init__(self):
        self.targetMeanIntensity=0.2
    def propose(self,processed_data,acquisition):
        if not isinstance(processed_data,list):
            raise TypeError
        if not isinstance(acquisition,AcquisitionPlugin):
            raise TypeError
        # todo
        pass

class DecisionSelectOptimalZPlaneFromSharpness(iDecision):
    def propose(self,processed_data,acquisition):
        if not isinstance(processed_data,list):
            raise TypeError
        if not isinstance(acquisition,AcquisitionPlugin):
            raise TypeError
        # todo
        pass

class DecisionFisherOptimize(iDecision):
    def propose(self,processed_data,acquisition):
        if not isinstance(processed_data,list):
            raise TypeError
        if not isinstance(acquisition,AcquisitionPlugin):
            raise TypeError
        # todo
        pass

class DecisionFisherDeoptimize(iDecision):
    def __init__(self):
        self.model=Model()

    def propose(self,processed_data,acquisition):
        if not isinstance(processed_data,list):
            raise TypeError
        if not isinstance(acquisition,AcquisitionPlugin):
            raise TypeError
        # todo
        pass

class DecisionPickROIFromMask(iDecision):
    def __init__(self,numCellsThreshold=1):
        self.numCellsThreshold=numCellsThreshold
        self.xyPositionOptimizer=ZSearchXYPositionOptimizerFull()
    def propose(self, processed_data, acquisition,zRange=None,timeRange=None,channels=None,split_roi=False,maxNumCells=10000000):
        if not isinstance(processed_data,list):
            raise TypeError
        if not isinstance(acquisition,AcquisitionPlugin):
            raise TypeError
        m = np.sum(np.array(processed_data['cellDetectNumCellsInRoi']['numcells']))

        print('num detectedcells {}'.format(m))
        sequence=[]
        thresholds=[]
        for  i  in range(len(processed_data['cellDetectNumCellsInRoi']['numcells'])):
            #print(processed_data['cellDetectNumCellsInRoi']['numcells'][i])
            #print(self.numCellsThreshold)
            if processed_data['cellDetectNumCellsInRoi']['numcells'][i]>=self.numCellsThreshold:
                index=processed_data['cellDetectNumCellsInRoi']['index'][i]
                #print(index)
                sequence.append(acquisition.events.xy_positions[index[0]])
                thresholds.append(processed_data['cellDetectNumCellsInRoi']['numcells'][i])
        sortedThresholds=np.sort(thresholds)
        sortedThresholdsIndex=np.argsort(thresholds)
        if len(sequence)==0:
            #print('No cells found')
            #print('NULL ACQUISION PROPOSED')
            sequence=[[0,0]]
        else:
            newSequence = []
            #print(len(sequence))
            #print(len(sortedThresholds))
            currentNumCells=0
            for i in range(len(sequence)-1, 0, -1):
                #print('currentNumCells={0}'.format(currentNumCells))
                if currentNumCells >= maxNumCells:
                    break
                currentBestIndex = sortedThresholdsIndex[i]
                #print('currentBestIndex:{0}'.format(currentBestIndex))
                newSequence.append(sequence[currentBestIndex])
                #print('currentBestSequence:{0}'.format(sequence))
                currentNumCells = currentNumCells + sortedThresholds[i]
            sequence = newSequence
            print('MaxFOVSequence={0}'.format(sequence))
        if zRange is not None:
            acquisition.events.z_start = zRange[0]
            acquisition.events.z_end = zRange[1]
            acquisition.events.z_step = zRange[2]
        if timeRange is not None:
            acquisition.events.num_time_points = timeRange[0]
            acquisition.events.time_interval_s = timeRange[1]
        if channels is not None:
            acquisition.events.channel_group = channels[0]
            acquisition.events.channels = channels[1]
            acquisition.events.channel_exposures_ms = channels[2]
        sequence=self.xyPositionOptimizer.optimize(sequence)
        acquisition.events.xy_positions=sequence
        print('sequence:{0}'.format(sequence))
        return acquisition

class DecisionPickROIFromXYSpotLocations(iDecision):
    def __init__(self,numCellsThreshold=1):
        self.numCellsThreshold=numCellsThreshold
        self.xyPositionOptimizer=ZSearchXYPositionOptimizerFull()
    def propose(self, processed_data, acquisition,zRange=None,timeRange=None,channels=None):
        if not isinstance(processed_data,list):
            raise TypeError
        if not isinstance(acquisition,AcquisitionPlugin):
            raise TypeError
        print(processed_data['cellDetectSpotLocationsInRoi']['spotLocationData'])
        m = len(processed_data['cellDetectSpotLocationsInRoi']['spotLocationData'])
        n=len(processed_data['cellDetectSpotLocationsInRoi']['spotLocationData'][0])
        o = len(processed_data['cellDetectSpotLocationsInRoi']['spotLocationData'][0][0])
        p=acquisition.events.xy_positions
        print('m: {}'.format(m))
        print('n: {}'.format(n))
        print('o: {}'.format(o))
        print('positions: {}'.format(p))
        sequence=[]
        for  i  in range(len(processed_data['cellDetectSpotLocationsInRoi']['spotLocationData'])):
            roiThresholds=processed_data['cellDetectSpotLocationsInRoi']['spotLocationData'][i][0]
            for j in range(len(roiThresholds['positions'])):
                sequence.append([acquisition.events.xy_positions[i][0]+roiThresholds['positions'][j][0],
                                 acquisition.events.xy_positions[i][1]+roiThresholds['positions'][j][1]])

        if len(sequence)==0:
            print('No cells found')
            print('NULL ACQUISION PROPOSED')
            sequence=[[0,0]]
        if zRange is not None:
            acquisition.events.z_start = zRange[0]
            acquisition.events.z_end = zRange[1]
            acquisition.events.z_step = zRange[2]
        if timeRange is not None:
            acquisition.events.num_time_points = timeRange[0]
            acquisition.events.time_interval_s = timeRange[1]
        if channels is not None:
            acquisition.events.channel_group = channels[0]
            acquisition.events.channels = channels[1]
            acquisition.events.channel_exposures_ms = channels[2]
        sequence=self.xyPositionOptimizer.optimize(sequence)
        acquisition.events.xy_positions=sequence
        print('sequence:{0}'.format(sequence))
        return acquisition

class DecisionSelectOptimalZPlaneFromEstimator:
    def __init__(self,estimator=None):
        self.estimator=estimator
    def propose(self, processed_data, acquisition,zRange=None,timeRange=None,channels=None):
        if not isinstance(processed_data, list):
            raise TypeError
        if not isinstance(acquisition, AcquisitionPlugin):
            raise TypeError
        if acquisition.events.xy_positions is not None:
            positions=acquisition.events.xy_positions
        elif acquisition.events.xyz_positions is not None:
            positions = acquisition.events.xyz_positions
        else:
            return acquisition
        new_positions=[]
        for p in positions:
            if len(p)==2:
                p.append(self.estimator.calculateZFromPoint(p[0],p[1]))
            else:
                z = self.estimator.calculateZFromPoint(p[0],p[1])
                p[2] = z
            new_positions.append(p)
        acquisition.events.xy_positions=None
        acquisition.events.xyz_positions=new_positions
        return acquisition

class DecisionSelectOptimalZPlaneFromSharpestZ:
    def __init__(self):
        self.estimator=ZPlaneEstimator()
    def propose(self, processed_data, acquisition,zRange=None,timeRange=None,channels=None):
        if not isinstance(processed_data, list):
            raise TypeError
        if not isinstance(acquisition, AcquisitionPlugin):
            raise TypeError
        if acquisition.events.xy_positions is not None:
            positions=acquisition.events.xy_positions
        elif acquisition.events.xyz_positions is not None:
            positions = acquisition.events.xyz_positions
        else:
            return acquisition
        if isinstance(positions,np.ndarray):
            positions=positions.tolist()
        self.estimator.fitFromDataset(processed_data,acquisition)
        new_positions=[]
        for p in positions:
            if len(p)==2:
                p.append(self.estimator.calculateZFromPoint(p[0],p[1]))
            else:
                z = self.estimator.calculateZFromPoint(p[0],p[1])
                p[2] = z
            new_positions.append(p)
        if zRange is not None:
            acquisition.events.z_start = zRange[0]
            acquisition.events.z_end = zRange[1]
            acquisition.events.z_step = zRange[2]
        if timeRange is not None:
            acquisition.events.num_time_points = timeRange[0]
            acquisition.events.time_interval_s = timeRange[1]
        if channels is not None:
            acquisition.events.channel_group = channels[0]
            acquisition.events.channels = channels[1]
            acquisition.events.channel_exposures_ms = channels[2]
        acquisition.events.xy_positions=None
        acquisition.events.xyz_positions=new_positions
        return acquisition


class DecisionPickXYROIFromDetectionBoolean(iDecision):
    def propose(self,processed_data,acquisition,zRange=None,timeRange=None,channels=None):
        if not isinstance(processed_data,list):
            raise TypeError
        if not isinstance(acquisition,AcquisitionPlugin):
            raise TypeError
        print(processed_data['detectionBoolean'])
        new_positions=[]
        for i in range(len(processed_data['detectionBoolean'])):
            if processed_data['detectionBoolean'][i]==True:
                new_positions.append(acquisition.events.xy_positions[i])
        if zRange is not None:
            acquisition.events.z_start = zRange[0]
            acquisition.events.z_end = zRange[1]
            acquisition.events.z_step = zRange[2]
        if timeRange is not None:
            acquisition.events.num_time_points = timeRange[0]
            acquisition.events.time_interval_s = timeRange[1]
        if channels is not None:
            acquisition.events.channel_group = channels[0]
            acquisition.events.channels = channels[1]
            acquisition.events.channel_exposures_ms = channels[2]
        acquisition.events.xy_positions = new_positions
        acquisition.events.xyz_positions = None
        return acquisition
