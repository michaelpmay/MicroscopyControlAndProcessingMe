from source.acquisition import AcquisitionPlugin
from itertools import permutations
import numpy as np
from scipy.signal import convolve2d
from source.image_process import CellDetectorCellMask, SpotCountLocations, SpotCounter, SpotCountLocationsDoughnut,SpotDetectImagesBooleanDoughnut,ImageCalculateFishPipeline
from source.distributed_computing import Task,DistributedComputeDaskTask,DistributedComputeLocal
class iPostProcessor:
    def add(self,key,*args,**kwargs):
        '''add a process which will generate tasks'''
        pass
    def compute(self):
        '''compute exisint tasks'''
        pass

class iPostProcess:
    def generate(self,dataset,acquisition):
        pass

class iPostProcessLibrary:
    def get(self,key,*args,**kwargs):
        'return process node form key, args kwrags'
        pass

class PostProcessor:
    def __init__(self,data={},acq=AcquisitionPlugin(),computer=DistributedComputeDaskTask('localhost:8786')):
        self.tasks=[]
        self.data=data
        self.output={}
        self.acq=acq
        self.computer=computer
    def add(self, key, *args, **kwargs):
        lib = PostProcessLibrary(computer=self.computer)
        processor=lib.get(key, *args, **kwargs)
        data=processor.process(self.data,self.acq)
        self.output.update(data)

    def get(self):
        return self.output


class PostProcessNode(iPostProcess):
    def __init__(self,function=None,*args,**kwargs):
        self.function=function
        self.name=None
        self.args=args
        self.kwargs=kwargs
        if 'computer' in kwargs.keys():
            self.computer=kwargs['computer']
        else:
            self.computer=DistributedComputeLocal()

    def process(self,dataset,acq,*args,**kwargs):
        return self.function(self,dataset,acq,*args,**kwargs)

class PostProcessLibrary():
    def __init__(self,computer=DistributedComputeDaskTask('localhost:8786')):
        self.computer=computer
        #print("PLIBRARY:{0}".format(self.computer))
    def get(self, key, *args, **kwargs):
        if not isinstance(key, str):
            raise TypeError
        command = 'self.' + key + '(*args,**kwargs)'
        node = eval(command)
        node.name = key
        return node

    def null(self):
        def function(self,dataset,acq,*args,**kwargs):
            data={}
            data['null']=()
            return data
        node=PostProcessNode(computer=self.computer)
        node.process=function
        return node

    def source(self):
        def function(self,dataset,acq,*args,**kwargs):
            data={}
            data['source']=dataset
            return data
        node=PostProcessNode(computer=self.computer)
        node.process=function
        return node

    def fovMeanIntensity(self,isSorted=False):
        def function(self,dataset,acq,*args,isSorted=False):
            #print(type(self.computer))
            '''this code is so nasty im sorry future me: need to refactor this into dimensions libraries'''
            tasks=[]
            def function(image,index):
                return np.mean(image)
            darray=dataset.as_array()
            d = np.array(darray)
            acq_type_dims = dataset.axes.keys()
            acq_len_dims = d.shape[:-2]
            meanIntensity = np.zeros(acq_len_dims)
            if len(acq_len_dims) == 1:
                for i in range(acq_len_dims[0]):
                    task=Task(function,d[i, :, :],[i])
                    tasks.append(task)
            elif len(acq_len_dims) == 2:
                for i in range(acq_len_dims[0]):
                    for j in range(acq_len_dims[1]):
                        task = Task(function, d[i, j, :, :],[i,j])
                        task()
                        tasks.append(task)
                output = self.computer.run(tasks)
                ind = 0
                for i in range(acq_len_dims[0]):
                    for j in range(acq_len_dims[1]):
                        meanIntensity[i, j] = output[ind]
                        ind=ind+1
            elif len(acq_len_dims) == 3:
                for i in range(acq_len_dims[0]):
                    for j in range(acq_len_dims[1]):
                        for k in range(acq_len_dims[2]):
                            task = Task(function, d[i, j,k, :, :],[i,j,k])
                            tasks.append(task)
                output = self.computer.run(tasks)
                ind=0
                for i in range(acq_len_dims[0]):
                    for j in range(acq_len_dims[1]):
                        for k in range(acq_len_dims[2]):
                            meanIntensity[i, j, k] = output[ind]
                            ind=ind+1
            elif len(acq_len_dims) == 4:
                for i in range(acq_len_dims[0]):
                    for j in range(acq_len_dims[1]):
                        for k in range(acq_len_dims[2]):
                            for l in range(acq_len_dims[3]):
                                task = Task(np.mean, d[i, j, k, l,:, :],[i,j,k,l])
                                tasks.append(task)
                output = self.computer.run(tasks)
                ind = 0
                for i in range(acq_len_dims[0]):
                    for j in range(acq_len_dims[1]):
                        for k in range(acq_len_dims[2]):
                            for l in range(acq_len_dims[3]):
                                meanIntensity[i, j, k,l] = output[ind]
                                ind = ind + 1
            else:
                raise ValueError
            data = {}
            data['fovMeanIntensity'] = meanIntensity
            if isSorted:
                data['fovMeanIntensitySorted']['values'] = np.sort(meanIntensity)
                data['fovMeanIntensitySorted']['indexmap'] = np.argsort(meanIntensity)
            return data

        process = PostProcessNode(computer=self.computer)
        process.function = function
        process.isSorted=isSorted
        return process

    def cellDetectNumCellsInRoi(self,default_flow_threshold=.1,MINIMUM_CELL_AREA = 30,model_type= 'nuclei'):
        def function(self,dataset,acq,*args,default_flow_threshold=.1,MINIMUM_CELL_AREA = 30,model_type='nuclei'):
            #print(type(self.computer))
            detector=CellDetectorCellMask(default_flow_threshold=default_flow_threshold,MINIMUM_CELL_AREA =MINIMUM_CELL_AREA,model_type=model_type)
            d = dataset.as_array()
            acq_len_dims = d.shape[:-2]
            numCells = []
            index=[]
            tasks=[]
            def functionNumCellsInROI(chunk):
                mask = detector.process(chunk)
                numCellsInROI = np.max(mask)
                return numCellsInROI
            if len(acq_len_dims)==1:
                for i in range(d.numblocks[0]):
                    chunk = np.array(d.blocks[i, :, :]).squeeze()
                    task=Task(functionNumCellsInROI,chunk)
                    tasks.append(task)
                output=self.computer.run(tasks)
                ind=0
                for i in range(d.numblocks[0]):
                    numCells.append(output[ind])
                    index.append([i])
                    ind=ind+1
            elif len(acq_len_dims)==2:
                for i in range(d.numblocks[0]):
                    for j in range(d.numblocks[1]):
                        chunk = np.array(d.blocks[i,j, :, :]).squeeze()
                        task = Task(functionNumCellsInROI, chunk)
                        tasks.append(task)
                output = self.computer.run(tasks)
                ind = 0
                for i in range(d.numblocks[0]):
                    for j in range(d.numblocks[1]):
                        numCells.append(output[ind])
                        index.append([i,j])
                        ind = ind + 1
            elif len(acq_len_dims)==3:
                for i in range(d.numblocks[0]):
                    for j in range(d.numblocks[1]):
                        for k in range(d.numblocks[2]):
                            chunk = np.array(d.blocks[i, j,k, :, :]).squeeze()
                            task = Task(functionNumCellsInROI, chunk)
                            tasks.append(task)
                output = self.computer.run(tasks)
                ind = 0
                for i in range(d.numblocks[0]):
                    for j in range(d.numblocks[1]):
                        for k in range(d.numblocks[2]):
                            numCells.append(output[ind])
                            index.append([i, j,k])
                            ind = ind + 1
            elif len(acq_len_dims)==4:
                for i in range(d.numblocks[0]):
                    for j in range(d.numblocks[1]):
                        for k in range(d.numblocks[2]):
                            for l in range(d.numblocks[3]):
                                chunk = np.array(d.blocks[i, j,k,l, :, :]).squeeze()
                                task = Task(functionNumCellsInROI, chunk)
                                tasks.append(task)
                output = self.computer.run(tasks)
                ind = 0
                for i in range(d.numblocks[0]):
                    for j in range(d.numblocks[1]):
                        for k in range(d.numblocks[2]):
                            for l in range(d.numblocks[3]):
                                numCells.append(output[ind])
                                index.append([i, j,k,l])
                                ind = ind + 1
            #print("NumCellsFound:{0}".format(np.sum(numCells)))
            return {'cellDetectNumCellsInRoi': {'numcells':numCells,'index':index}}

        process = PostProcessNode(computer=self.computer)
        process.function = function
        process.kwargs['detector'] = CellDetectorCellMask(model_type=model_type)
        process.kwargs['default_flow_threshold'] = default_flow_threshold
        process.kwargs['MINIMUM_CELL_AREA'] = MINIMUM_CELL_AREA
        process.kwargs['model_type']=model_type
        return process

    def cellDetectSpotLocationsInRoi(self,threshold=20):
        def function(self,dataset,acq,*args,threshold=threshold):
            #print(type(self.computer))
            detector=SpotCountLocations()
            d = dataset.as_array()
            acq_len_dims = d.shape[:-2]
            spotLocationData = []
            index=[]
            tasks=[]
            #print('acq_len_dims:{0}'.format(acq_len_dims))
            if len(acq_len_dims)==1:
                for i in range(d.numblocks[0]):
                    chunk = np.array(d.blocks[i, :, :]).squeeze()
                    tasks.append(Task(detector.process, chunk - np.mean(chunk), threshold=threshold))
                output = self.computer.run(tasks)
                ind = 0
                for i in range(d.numblocks[0]):
                    spotLocationData.append(output[ind])
                    index.append([i])
                    ind = ind + 1
            elif len(acq_len_dims)==2:
                for i in range(d.numblocks[0]):
                    for j in range(d.numblocks[1]):
                        chunk = np.array(d.blocks[i, j,:, :]).squeeze()
                        tasks.append(Task(detector.process, chunk - np.mean(chunk),threshold=threshold))
                output=self.computer.run(tasks)
                ind=0
                for i in range(d.numblocks[0]):
                    for j in range(d.numblocks[1]):
                        spotLocationData.append(output[ind])
                        index.append([i,j])
                        ind=ind+1
            elif len(acq_len_dims)==3:
                for i in range(d.numblocks[0]):
                    for j in range(d.numblocks[1]):
                        for k in range(d.numblocks[2]):
                            chunk = np.array(d.blocks[i, j,k, :, :]).squeeze()
                            tasks.append(Task(detector.process, chunk - np.mean(chunk), threshold=threshold))
                output = self.computer.run(tasks)
                ind = 0
                for i in range(d.numblocks[0]):
                    for j in range(d.numblocks[1]):
                        for k in range(d.numblocks[2]):
                            spotLocationData.append(output[ind])
                            index.append([i, j,k])
                            ind = ind + 1
            elif len(acq_len_dims)==4:
                for i in range(d.numblocks[0]):
                    for j in range(d.numblocks[1]):
                        for k in range(d.numblocks[2]):
                            for l in range(d.numblocks[3]):
                                chunk = np.array(d.blocks[i, j, k,l, :, :]).squeeze()
                                tasks.append(Task(detector.process, chunk - np.mean(chunk), threshold=threshold))
                output = self.computer.run(tasks)
                ind = 0
                for i in range(d.numblocks[0]):
                    for j in range(d.numblocks[1]):
                        for k in range(d.numblocks[2]):
                            for l in range(d.numblocks[3]):
                                spotLocationData.append(output[ind])
                                index.append([i, j, k,l])
                                ind = ind + 1
            else:
                raise ValueError
            return {'cellDetectSpotLocationsInRoi': {'spotLocationData':spotLocationData,'index':index}}

        process = PostProcessNode(computer=self.computer)
        process.function = function
        return process

    def cellDetectSpotLocationsInRoiDoughnut(self,threshold=20):
        def function(self,dataset,acq,*args,threshold=threshold):
            #print(type(self.computer))
            detector=SpotCountLocationsDoughnut()
            d = dataset.as_array()
            acq_len_dims = d.shape[:-2]
            spotLocationData = []
            index=[]
            tasks=[]
            #print('acq_len_dims:{0}'.format(acq_len_dims))
            if len(acq_len_dims)==1:
                for i in range(d.numblocks[0]):
                    chunk = np.array(d.blocks[i, :, :]).squeeze()
                    tasks.append(Task(detector.process, chunk - np.mean(chunk), threshold=threshold))
                output = self.computer.run(tasks)
                ind = 0
                for i in range(d.numblocks[0]):
                    spotLocationData.append(output[ind])
                    index.append([i])
                    ind = ind + 1
            elif len(acq_len_dims)==2:
                for i in range(d.numblocks[0]):
                    for j in range(d.numblocks[1]):
                        chunk = np.array(d.blocks[i, j,:, :]).squeeze()
                        tasks.append(Task(detector.process, chunk - np.mean(chunk),threshold=threshold))
                output=self.computer.run(tasks)
                ind=0
                for i in range(d.numblocks[0]):
                    for j in range(d.numblocks[1]):
                        spotLocationData.append(output[ind])
                        index.append([i,j])
                        ind=ind+1
            elif len(acq_len_dims)==3:
                for i in range(d.numblocks[0]):
                    for j in range(d.numblocks[1]):
                        for k in range(d.numblocks[2]):
                            chunk = np.array(d.blocks[i, j,k, :, :]).squeeze()
                            tasks.append(Task(detector.process, chunk - np.mean(chunk), threshold=threshold))
                output = self.computer.run(tasks)
                ind = 0
                for i in range(d.numblocks[0]):
                    for j in range(d.numblocks[1]):
                        for k in range(d.numblocks[2]):
                            spotLocationData.append(output[ind])
                            index.append([i, j,k])
                            ind = ind + 1
            elif len(acq_len_dims)==4:
                for i in range(d.numblocks[0]):
                    for j in range(d.numblocks[1]):
                        for k in range(d.numblocks[2]):
                            for l in range(d.numblocks[3]):
                                chunk = np.array(d.blocks[i, j, k,l, :, :]).squeeze()
                                tasks.append(Task(detector.process, chunk - np.mean(chunk), threshold=threshold))
                output = self.computer.run(tasks)
                ind = 0
                for i in range(d.numblocks[0]):
                    for j in range(d.numblocks[1]):
                        for k in range(d.numblocks[2]):
                            for l in range(d.numblocks[3]):
                                spotLocationData.append(output[ind])
                                index.append([i, j, k,l])
                                ind = ind + 1
            else:
                raise ValueError
            return {'cellDetectSpotLocationsInRoi': {'spotLocationData':spotLocationData,'index':index}}

        process = PostProcessNode(computer=self.computer)
        process.function = function
        return process

    def fishPipelineData(self,threshold=20):
        def function(self,dataset,acq,*args,threshold=threshold):
            #print(type(self.computer))
            detector=ImageCalculateFishPipeline()
            d = dataset.as_array()
            acq_len_dims = d.shape[:-2]
            fishPipelineData = []
            index=[]
            tasks=[]
            #print('acq_len_dims:{0}'.format(acq_len_dims))
            if len(acq_len_dims)==1:
                for i in range(d.numblocks[0]):
                    chunk = np.array(d.blocks[i, :, :]).squeeze()
                    tasks.append(Task(detector.process, chunk))
                output = self.computer.run(tasks)
                ind = 0
                for i in range(d.numblocks[0]):
                    fishPipelineData.append(output[ind])
                    index.append([i])
                    ind = ind + 1
            elif len(acq_len_dims)==2:
                for i in range(d.numblocks[0]):
                    for j in range(d.numblocks[1]):
                        chunk = np.array(d.blocks[i, j,:, :]).squeeze()
                        tasks.append(Task(detector.process))
                output=self.computer.run(tasks)
                ind=0
                for i in range(d.numblocks[0]):
                    for j in range(d.numblocks[1]):
                        fishPipelineData.append(output[ind])
                        index.append([i,j])
                        ind=ind+1
            elif len(acq_len_dims)==3:
                for i in range(d.numblocks[0]):
                    for j in range(d.numblocks[1]):
                        for k in range(d.numblocks[2]):
                            chunk = np.array(d.blocks[i, j,k, :, :]).squeeze()
                            tasks.append(Task(detector.process, chunk))
                output = self.computer.run(tasks)
                ind = 0
                for i in range(d.numblocks[0]):
                    for j in range(d.numblocks[1]):
                        for k in range(d.numblocks[2]):
                            fishPipelineData.append(output[ind])
                            index.append([i, j,k])
                            ind = ind + 1
            elif len(acq_len_dims)==4:
                for i in range(d.numblocks[0]):
                    for j in range(d.numblocks[1]):
                        for k in range(d.numblocks[2]):
                            for l in range(d.numblocks[3]):
                                chunk = np.array(d.blocks[i, j, k,l, :, :]).squeeze()
                                tasks.append(Task(detector.process, chunk ))
                output = self.computer.run(tasks)
                ind = 0
                for i in range(d.numblocks[0]):
                    for j in range(d.numblocks[1]):
                        for k in range(d.numblocks[2]):
                            for l in range(d.numblocks[3]):
                                fishPipelineData.append(output[ind])
                                index.append([i, j, k,l])
                                ind = ind + 1
            else:
                raise ValueError
            return {'cellDetectSpotLocationsInRoi': {'fishPipelineData':fishPipelineData,'index':index}}

        process = PostProcessNode(computer=self.computer)
        process.function = function
        return process

    def SpotDetectImagesBooleanDoughnut(self,threshold=20):
        def function(self,dataset,acq,*args,threshold=threshold):
            #print(type(self.computer))
            detector=SpotDetectImagesBooleanDoughnut()
            d = dataset.as_array()
            acq_len_dims = d.shape[:-2]
            spotLocationData = []
            index=[]
            tasks=[]
            print('acq_len_dims:{0}'.format(acq_len_dims))
            if len(acq_len_dims)==1:
                for i in range(d.numblocks[0]):
                    chunk = np.array(d.blocks[i, :, :]).squeeze()
                    tasks.append(Task(detector.process, chunk - np.mean(chunk), threshold=threshold))
                output = self.computer.run(tasks)
                ind = 0
                for i in range(d.numblocks[0]):
                    spotLocationData.append(output[ind])
                    index.append([i])
                    ind = ind + 1
            elif len(acq_len_dims)==2:
                for i in range(d.numblocks[0]):
                    for j in range(d.numblocks[1]):
                        chunk = np.array(d.blocks[i, j,:, :]).squeeze()
                        tasks.append(Task(detector.process, chunk - np.mean(chunk),threshold=threshold))
                output=self.computer.run(tasks)
                ind=0
                for i in range(d.numblocks[0]):
                    for j in range(d.numblocks[1]):
                        spotLocationData.append(output[ind])
                        index.append([i,j])
                        ind=ind+1
            elif len(acq_len_dims)==3:
                for i in range(d.numblocks[0]):
                    for j in range(d.numblocks[1]):
                        for k in range(d.numblocks[2]):
                            chunk = np.array(d.blocks[i, j,k, :, :]).squeeze()
                            tasks.append(Task(detector.process, chunk - np.mean(chunk), threshold=threshold))
                output = self.computer.run(tasks)
                ind = 0
                for i in range(d.numblocks[0]):
                    for j in range(d.numblocks[1]):
                        for k in range(d.numblocks[2]):
                            spotLocationData.append(output[ind])
                            index.append([i, j,k])
                            ind = ind + 1
            elif len(acq_len_dims)==4:
                for i in range(d.numblocks[0]):
                    for j in range(d.numblocks[1]):
                        for k in range(d.numblocks[2]):
                            for l in range(d.numblocks[3]):
                                chunk = np.array(d.blocks[i, j, k,l, :, :]).squeeze()
                                tasks.append(Task(detector.process, chunk - np.mean(chunk), threshold=threshold))
                output = self.computer.run(tasks)
                ind = 0
                for i in range(d.numblocks[0]):
                    for j in range(d.numblocks[1]):
                        for k in range(d.numblocks[2]):
                            for l in range(d.numblocks[3]):
                                spotLocationData.append(output[ind])
                                index.append([i, j, k,l])
                                ind = ind + 1
            else:
                raise ValueError
            return {'detectionBoolean': spotLocationData}

        process = PostProcessNode(computer=self.computer)
        process.function = function
        return process


    def sharpestZ(self):
        def function(self,dataset, acq, *args):
            d = dataset.as_array()
            print('dataset axes')
            print(dataset.axes)
            print(dataset.axes_types)
            acq_len_dims = d.shape[:-2]
            print(acq_len_dims)
            sharpnessData = []
            index = []
            kernel = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]]).astype('float')
            if len(acq_len_dims) == 1:
                for i in range(d.numblocks[0]):
                    try:
                        chunk = np.array(d.blocks[i, :, :]).squeeze()
                        data = np.sum(np.abs(convolve2d(chunk.astype('float'), kernel)))
                        sharpnessData.append(data)
                    except:
                        pass
            elif len(acq_len_dims) == 2:
                for i in range(d.numblocks[0]):  # gota index wierd here, unfortunatly
                    maxSharpnessZ = 0
                    maxJ = 0
                    for j in range(d.numblocks[1]):
                        try:
                            chunk = np.array(d.blocks[i, j]).squeeze()
                            sharpness = np.sum(np.abs(convolve2d(chunk.astype('float'), kernel)))
                            if sharpness > maxSharpnessZ:
                                maxSharpnessZ = sharpness
                                maxJ = j
                        except:
                            pass
                        sharpnessData.append(maxSharpnessZ)
                        index.append([i, maxJ])
            elif len(acq_len_dims) == 3:
                for k in range(d.numblocks[2]):
                    for i in range(d.numblocks[0]):  # gota index wierd here, unfortunatly
                        maxSharpnessZ = 0
                        maxJ = 0
                        for j in range(d.numblocks[1]):
                            try:
                                chunk = np.array(d.blocks[i, j, k]).squeeze()
                                sharpness = np.sum(np.abs(convolve2d(chunk.astype('float'), kernel)))
                                if sharpness > maxSharpnessZ:
                                    maxSharpnessZ = sharpness
                                    maxJ = j
                            except:
                                pass
                            sharpnessData.append(maxSharpnessZ)
                            index.append([i, maxJ, k])
            elif len(acq_len_dims) == 4:
                print(d.numblocks)
                for k in range(d.numblocks[2]):  # xyposition
                    for i in range(d.numblocks[0]):  # channel
                        maxSharpnessZ = 0
                        maxJ = 0
                        for j in range(d.numblocks[1]):  # zposition
                            totalSharpnessAcrossChannels = 0
                            for l in range(d.numblocks[3]):
                                try:
                                    chunk = np.array(d.blocks[i, j, k, l]).squeeze()
                                    channel_sharpness = np.sum(np.abs(convolve2d(chunk.astype('float'), kernel)))
                                    totalSharpnessAcrossChannels = totalSharpnessAcrossChannels + channel_sharpness
                                    print([i, j, k, l, totalSharpnessAcrossChannels])
                                except:
                                    pass
                            # print([i, j, k, totalSharpnessAcrossChannels])

                            if totalSharpnessAcrossChannels > maxSharpnessZ:
                                maxSharpnessZ = totalSharpnessAcrossChannels
                                maxJ = j
                        if maxSharpnessZ > 0:
                            sharpnessData.append(maxSharpnessZ)
                            zRange = np.arange(acq.events.z_start, acq.events.z_end + .0001, acq.events.z_step)
                            print(zRange)
                            print('[k]:{0}'.format(k))
                            print('acq.events.xy_positions[k]:{0}'.format(acq.events.xy_positions[k]))
                            print(acq.events.xy_positions[k][0])
                            print(acq.events.xy_positions[k][1])
                            print(zRange)
                            print(maxJ)
                            print(zRange[maxJ])
                            index.append([acq.events.xy_positions[k][0], acq.events.xy_positions[k][1], zRange[maxJ]])
            elif len(acq_len_dims) == 5:
                print('5 dims')
                for m in range(d.numblocks[4]):
                    for l in range(d.numblocks[3]):
                        for k in range(d.numblocks[2]):
                            for i in range(d.numblocks[0]):  # gota index wierd here, unfortunatly
                                maxSharpnessZ = 0
                                maxJ = 0
                                for j in range(d.numblocks[1]):
                                    try:
                                        chunk = np.array(d.blocks[i, j, k, l, m]).squeeze()
                                        sharpness = np.sum(np.abs(convolve2d(chunk.astype('float'), kernel)))
                                        if sharpness > maxSharpnessZ:
                                            maxSharpnessZ = sharpness
                                            maxJ = j
                                    except:
                                        pass
                                sharpnessData.append(maxSharpnessZ)
                                index.append([i, maxJ, k, l, m])
            elif len(acq_len_dims) == 6:
                print('6 dims')
                for n in range(d.numblocks[5]):
                    for m in range(d.numblocks[4]):
                        for l in range(d.numblocks[3]):
                            for k in range(d.numblocks[2]):
                                for i in range(d.numblocks[0]):  # gota index wierd here, unfortunatly
                                    maxSharpnessZ = 0
                                    maxJ = 0
                                    for j in range(d.numblocks[1]):
                                        try:
                                            chunk = np.array(d.blocks[i, j, k, l, m, n]).squeeze()
                                            sharpness = np.sum(np.abs(convolve2d(chunk.astype('float'), kernel)))
                                            if sharpness > maxSharpnessZ:
                                                maxSharpnessZ = sharpness
                                                maxJ = j
                                                sharpnessData.append(sharpness)
                                        except:
                                            pass
                                    sharpnessData.append(maxSharpnessZ)
                                    index.append([i, maxJ, k, l, m, n])
            else:
                raise ValueError
            return {'sharpestZ': {'value': sharpnessData, 'index': index}}

        process = PostProcessNode(computer=self.computer)
        process.function = function
        return process

class ProcessNodeLibrary:
    def get(self,key,*args,**kwargs):
        if not isinstance(key,str):
            raise TypeError
        command='self.'+key+'(*args,**kwargs)'
        node=eval(command)
        node.name=key
        return node

    def null(self):
        def f(dataset,acq,*args,**kwargs):
            data={}
            data['null']=()
            return data
        node = ProcessNode(f)
        return node

    def source(self):
        def f(dataset,acq,*args,**kwargs):
            data={}
            data['source']=dataset
            return data
        node = ProcessNode(f)
        return node


    def fovMeanIntensity(self,isSorted=False):
        def f(dataset,acq,*args,isSorted=False):
            d = np.array(dataset.as_array())
            acq_type_dims = dataset.axes.keys()
            acq_len_dims = d.shape[:-2]
            meanIntensity = np.zeros(acq_len_dims)
            if len(acq_len_dims) == 1:
                for i in range(acq_len_dims[0]):
                    meanIntensity[i] = np.mean(d[i, :, :])
            elif len(acq_len_dims) == 2:
                for i in range(acq_len_dims[0]):
                    for j in range(acq_len_dims[1]):
                        meanIntensity[i, j] = np.mean(d[i, j, :, :])
            elif len(acq_len_dims) == 3:
                for i in range(acq_len_dims[0]):
                    for j in range(acq_len_dims[1]):
                        for k in range(acq_len_dims[2]):
                            meanIntensity[i, j, k] = np.mean(d[i, j, k,:, :])
            elif len(acq_len_dims) == 4:
                for i in range(acq_len_dims[0]):
                    for j in range(acq_len_dims[1]):
                        for k in range(acq_len_dims[2]):
                            for l in range(acq_len_dims[3]):
                                meanIntensity[i, j, k] = np.mean(d[i, j, k,l,:, :])
            else:
                raise ValueError
            data={}
            data['fovMeanIntensity']=meanIntensity
            if isSorted:
                data['fovMeanIntensitySorted']['values'] = np.sort(meanIntensity)
                data['fovMeanIntensitySorted']['indexmap'] = np.argsort(meanIntensity)
            return data
        node = ProcessNode(f)
        node.isSorted=isSorted
        return node

    def cellDetectNumCellsInRoi(self,default_flow_threshold=.1,MINIMUM_CELL_AREA = 30):
        def f(dataset, acq, *args,default_flow_threshold=.1,MINIMUM_CELL_AREA = 30):
            detector=CellDetectorCellMask(default_flow_threshold=default_flow_threshold,MINIMUM_CELL_AREA =MINIMUM_CELL_AREA)
            d = dataset.as_array()
            acq_len_dims = d.shape[:-2]
            numCells = []
            index=[]
            if len(acq_len_dims)==1:
                for i in range(d.numblocks[0]):
                    chunk = np.array(d.blocks[i, :, :]).squeeze()
                    mask = detector.process(chunk)
                    numCellsInROI = np.max(mask)
                    numCells.append(numCellsInROI)
                    index.append([i])
            if len(acq_len_dims)==2:
                for i in range(d.numblocks[0]):
                    for j in range(d.numblocks[1]):
                        chunk = np.array(d.blocks[i, j, :, :]).squeeze()
                        mask=detector.process(chunk)
                        numCellsInROI=np.max(mask)
                        numCells.append(numCellsInROI)
                        index.append([i,j])
            if len(acq_len_dims)==3:
                for i in range(d.numblocks[0]):
                    for j in range(d.numblocks[1]):
                        for k in range(d.numblocks[1]):
                            chunk = np.array(d.blocks[i, j,k, :, :]).squeeze()
                            mask=detector.process(chunk)
                            numCellsInROI=np.max(mask)
                            numCells.append(numCellsInROI)
                            index.append([i,j,k])
            return {'cellDetectNumCellsInRoi': {'numcells':numCells,'index':index}}

        node = ProcessNode(f)
        node.kwargs['detector']=CellDetectorCellMask()
        node.kwargs['default_flow_threshold']=default_flow_threshold
        node.kwargs['MINIMUM_CELL_AREA'] = MINIMUM_CELL_AREA
        return node

    def cellDetectNumSpotsInRoi(self,default_flow_threshold=.1,MINIMUM_CELL_AREA = 30):
        def f(dataset, acq, *args,default_flow_threshold=.1,MINIMUM_CELL_AREA = 30):
            detector=SpotCounter()
            d = dataset.as_array()
            acq_len_dims = d.shape[:-2]
            numSpots = []
            index=[]
            if len(acq_len_dims)==1:
                for i in range(d.numblocks[0]):
                    chunk = np.array(d.blocks[i, :, :]).squeeze()
                    numSpotsROI = detector.process(chunk)
                    numSpots.append(numSpotsROI)
                    index.append([i])
            if len(acq_len_dims)==2:
                for i in range(d.numblocks[0]):
                    for j in range(d.numblocks[1]):
                        chunk = np.array(d.blocks[i, j, :, :]).squeeze()
                        numSpotsROI=detector.process(chunk)
                        numSpots.append(numSpotsROI)
                        index.append([i,j])
            if len(acq_len_dims)==3:
                for i in range(d.numblocks[0]):
                    for j in range(d.numblocks[1]):
                        for k in range(d.numblocks[1]):
                            chunk = np.array(d.blocks[i, j,k, :, :]).squeeze()
                            numSpotsROI=detector.process(chunk)
                            numSpots.append(numSpotsROI)
                            index.append([i,j,k])
            return {'cellDetectNumSpotsInRoi': {'numSpots':numSpots,'index':index}}

        node = ProcessNode(f)
        node.kwargs['detector']=CellDetectorCellMask()
        node.kwargs['default_flow_threshold']=default_flow_threshold
        node.kwargs['MINIMUM_CELL_AREA'] = MINIMUM_CELL_AREA
        return node

    def cellDetectSpotLocationsInRoi(self,threshold=20):
        def f(dataset, acq, *args,threshold=threshold):
            detector=SpotCountLocations()
            d = dataset.as_array()
            acq_len_dims = d.shape
            spotLocationData = []
            index=[]
            if len(acq_len_dims)==1:
                for i in range(d.numblocks[0]):
                    try:
                        chunk = np.array(d.blocks[i, :, :]).squeeze()
                        data = detector.process(chunk-np.mean(chunk))
                        spotLocationData.append(data)
                        index.append([i])
                    except:
                        pass
            elif len(acq_len_dims)==2:
                for i in range(d.numblocks[0]):
                    for j in range(d.numblocks[1]):
                        try:
                            chunk = np.array(d.blocks[i, j, :, :]).squeeze()
                            data = detector.process(chunk-np.mean(chunk),threshold=threshold)
                            spotLocationData.append(data)
                            index.append([i,j])
                        except:
                            pass
            elif len(acq_len_dims)==3:
                for i in range(d.numblocks[0]):
                    for j in range(d.numblocks[1]):
                        for k in range(d.numblocks[2]):
                            try:
                                chunk = np.array(d.blocks[i, j,k]).squeeze()
                                data = detector.process(chunk-np.mean(chunk),threshold=threshold)
                                spotLocationData.append(data)
                                index.append([i,j,k])
                            except:
                                pass
            elif len(acq_len_dims)==4:
                for i in range(d.numblocks[0]):
                    for j in range(d.numblocks[1]):
                        for k in range(d.numblocks[2]):
                            for l in range(d.numblocks[3]):
                                try:
                                    chunk = np.array(d.blocks[i, j,k,l]).squeeze()
                                    data = detector.process(chunk-np.mean(chunk),threshold=threshold)
                                    spotLocationData.append(data)
                                    index.append([i,j,k,l])
                                except:
                                    pass
            elif len(acq_len_dims)==5:
                for i in range(d.numblocks[0]):
                    for j in range(d.numblocks[1]):
                        for k in range(d.numblocks[2]):
                            for l in range(d.numblocks[3]):
                                for m in range(d.numblocks[4]):
                                    try:
                                        chunk = np.array(d.blocks[i, j,k,l,m]).squeeze()
                                        data = detector.process(chunk-np.mean(chunk),threshold=threshold)
                                        spotLocationData.append(data)
                                        index.append([i,j,k,l,m])
                                    except:
                                        pass
            elif len(acq_len_dims) == 6:
                for i in range(d.numblocks[0]):
                    for j in range(d.numblocks[1]):
                        for k in range(d.numblocks[2]):
                            for l in range(d.numblocks[3]):
                                for m in range(d.numblocks[4]):
                                    for n in range(d.numblocks[5]):
                                        try:
                                            chunk = np.array(d.blocks[i, j, k, l,m,n]).squeeze()
                                            data = detector.process(chunk-np.mean(chunk),threshold=threshold)
                                            spotLocationData.append(data)
                                            index.append([i, j, k, l,m,n])
                                        except:
                                            pass
            else:
                raise ValueError
            return {'cellDetectSpotLocationsInRoi': {'spotLocationData':spotLocationData,'index':index}}

        node = ProcessNode(f)
        return node

    def sharpness(self):
        def f(dataset, acq, *args):
            d = dataset.as_array()
            acq_len_dims = d.shape[:-2]
            sharpnessData = []
            index = []
            kernel=np.array([[0,1,0],[1,-4,1],[0,1,0]]).astype('float')
            if len(acq_len_dims) == 1:
                for i in range(d.numblocks[0]):
                    try:
                        chunk = np.array(d.blocks[i, :, :]).squeeze()
                        data = np.sum(np.abs(convolve2d(chunk.astype('float'),kernel)))
                        sharpnessData.append(data)
                        index.append([i])
                    except:
                        pass
            elif len(acq_len_dims) == 2:
                for i in range(d.numblocks[0]):
                    for j in range(d.numblocks[1]):
                        try:
                            chunk = np.array(d.blocks[i, j, :, :]).squeeze()
                            data = np.sum(np.abs(convolve2d(chunk.astype('float'),kernel)))
                            sharpnessData.append(data)
                            index.append([i, j])
                        except:
                            pass
            elif len(acq_len_dims) == 3:
                for i in range(d.numblocks[0]):
                    for j in range(d.numblocks[1]):
                        for k in range(d.numblocks[2]):
                            try:
                                chunk = np.array(d.blocks[i, j, k]).squeeze()
                                data = np.sum(np.abs(convolve2d(chunk.astype('float'),kernel)))
                                sharpnessData.append(data)
                                index.append([i, j, k])
                            except:
                                pass
            elif len(acq_len_dims) == 4:
                for i in range(d.numblocks[0]):
                    for j in range(d.numblocks[1]):
                        for k in range(d.numblocks[2]):
                            for l in range(d.numblocks[3]):
                                try:
                                    chunk = np.array(d.blocks[i, j, k, l]).squeeze()
                                    data = np.sum(np.abs(convolve2d(chunk.astype('float'),kernel)))
                                    sharpnessData.append(data)
                                    index.append([i, j, k, l])
                                except:
                                    pass
            elif len(acq_len_dims) == 5:
                for i in range(d.numblocks[0]):
                    for j in range(d.numblocks[1]):
                        for k in range(d.numblocks[2]):
                            for l in range(d.numblocks[3]):
                                for m in range(d.numblocks[4]):
                                    try:
                                        chunk = np.array(d.blocks[i, j, k, l, m]).squeeze()
                                        data = np.sum(np.abs(convolve2d(chunk.astype('float'),kernel)))
                                        sharpnessData.append(data)
                                        index.append([i, j, k, l, m])
                                    except:
                                        pass
            elif len(acq_len_dims) == 6:
                for i in range(d.numblocks[0]):
                    for j in range(d.numblocks[1]):
                        for k in range(d.numblocks[2]):
                            for l in range(d.numblocks[3]):
                                for m in range(d.numblocks[4]):
                                    for n in range(d.numblocks[5]):
                                        try:
                                            chunk = np.array(d.blocks[i, j, k, l, m, n]).squeeze()
                                            data = np.sum(np.abs(convolve2d(chunk.astype('float'),kernel)))
                                            sharpnessData.append(data)
                                            index.append([i, j, k, l, m, n])
                                        except:
                                            pass
            else:
                raise ValueError
            return {'sharpness': {'value': sharpnessData,'index':index}}
        node = ProcessNode(f)
        return node

    def sharpestZ(self):
        def f(dataset, acq, *args):
            d = dataset.as_array()
            print('dataset axes')
            print(dataset.axes)
            print(dataset.axes_types)
            acq_len_dims = d.shape[:-2]
            print(acq_len_dims)
            sharpnessData = []
            index = []
            kernel = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]]).astype('float')
            if len(acq_len_dims) == 1:
                for i in range(d.numblocks[0]):
                    try:
                        chunk = np.array(d.blocks[i, :, :]).squeeze()
                        data = np.sum(np.abs(convolve2d(chunk.astype('float'), kernel)))
                        sharpnessData.append(data)
                    except:
                        pass
            elif len(acq_len_dims) == 2:
                for i in range(d.numblocks[0]):  # gota index wierd here, unfortunatly
                    maxSharpnessZ = 0
                    maxJ = 0
                    for j in range(d.numblocks[1]):
                        try:
                            chunk = np.array(d.blocks[i, j]).squeeze()
                            sharpness = np.sum(np.abs(convolve2d(chunk.astype('float'), kernel)))
                            if sharpness > maxSharpnessZ:
                                maxSharpnessZ = sharpness
                                maxJ = j
                        except:
                            pass
                        sharpnessData.append(maxSharpnessZ)
                        index.append([i, maxJ])
            elif len(acq_len_dims) == 3:
                for k in range(d.numblocks[2]):
                    for i in range(d.numblocks[0]):  # gota index wierd here, unfortunatly
                        maxSharpnessZ = 0
                        maxJ = 0
                        for j in range(d.numblocks[1]):
                            try:
                                chunk = np.array(d.blocks[i, j, k]).squeeze()
                                sharpness = np.sum(np.abs(convolve2d(chunk.astype('float'), kernel)))
                                if sharpness > maxSharpnessZ:
                                    maxSharpnessZ = sharpness
                                    maxJ = j
                            except:
                                pass
                            sharpnessData.append(maxSharpnessZ)
                            index.append([i, maxJ, k])
            elif len(acq_len_dims) == 4:
                print(d.numblocks)
                for k in range(d.numblocks[2]): #xyposition
                    for i in range(d.numblocks[0]): #channel
                        maxSharpnessZ = 0
                        maxJ = 0
                        for j in range(d.numblocks[1]):  # zposition
                            totalSharpnessAcrossChannels=0
                            for l in range(d.numblocks[3]):
                                try:
                                    chunk = np.array(d.blocks[i, j, k, l]).squeeze()
                                    channel_sharpness = np.sum(np.abs(convolve2d(chunk.astype('float'), kernel)))
                                    totalSharpnessAcrossChannels = totalSharpnessAcrossChannels +channel_sharpness
                                    print([i, j, k, l,totalSharpnessAcrossChannels])
                                except:
                                    pass
                            #print([i, j, k, totalSharpnessAcrossChannels])

                            if totalSharpnessAcrossChannels > maxSharpnessZ:
                                maxSharpnessZ = totalSharpnessAcrossChannels
                                maxJ = j
                        if maxSharpnessZ>0:
                            sharpnessData.append(maxSharpnessZ)
                            zRange=np.arange(acq.events.z_start,acq.events.z_end+.0001,acq.events.z_step)
                            print(zRange)
                            print('[k]:{0}'.format(k))
                            print('acq.events.xy_positions[k]:{0}'.format(acq.events.xy_positions[k]))
                            print(acq.events.xy_positions[k][0])
                            print(acq.events.xy_positions[k][1])
                            print(zRange)
                            print(maxJ)
                            print(zRange[maxJ])
                            index.append([acq.events.xy_positions[k][0],acq.events.xy_positions[k][1], zRange[maxJ]])
            elif len(acq_len_dims) == 5:
                print('5 dims')
                for m in range(d.numblocks[4]):
                    for l in range(d.numblocks[3]):
                        for k in range(d.numblocks[2]):
                            for i in range(d.numblocks[0]):  # gota index wierd here, unfortunatly
                                maxSharpnessZ = 0
                                maxJ = 0
                                for j in range(d.numblocks[1]):
                                    try:
                                        chunk = np.array(d.blocks[i, j, k, l, m]).squeeze()
                                        sharpness = np.sum(np.abs(convolve2d(chunk.astype('float'), kernel)))
                                        if sharpness > maxSharpnessZ:
                                            maxSharpnessZ = sharpness
                                            maxJ = j
                                    except:
                                        pass
                                sharpnessData.append(maxSharpnessZ)
                                index.append([i, maxJ, k, l,m])
            elif len(acq_len_dims) == 6:
                print('6 dims')
                for n in range(d.numblocks[5]):
                    for m in range(d.numblocks[4]):
                        for l in range(d.numblocks[3]):
                            for k in range(d.numblocks[2]):
                                for i in range(d.numblocks[0]): # gota index wierd here, unfortunatly
                                    maxSharpnessZ = 0
                                    maxJ=0
                                    for j in range(d.numblocks[1]):
                                        try:
                                            chunk = np.array(d.blocks[i, j, k, l, m, n]).squeeze()
                                            sharpness = np.sum(np.abs(convolve2d(chunk.astype('float'), kernel)))
                                            if sharpness>maxSharpnessZ:
                                                maxSharpnessZ=sharpness
                                                maxJ=j
                                                sharpnessData.append(sharpness)
                                        except:
                                            pass
                                    sharpnessData.append(maxSharpnessZ)
                                    index.append([i, maxJ, k, l,m,n])
            else:
                raise ValueError
            return {'sharpestZ': {'value': sharpnessData, 'index': index}}
        node = ProcessNode(f)
        return node



    def spotCountToMask(self):
        def f(dataset,acq,*args,**kwargs):
            return ()

        node = ProcessNode(f)
        return node

    def fromcallback(self,callback):
        def f(dataset,acq,*args,**kwargs):
            return ()

        node = ProcessNode(f)
        return node