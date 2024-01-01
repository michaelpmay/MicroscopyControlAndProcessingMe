import scipy.signal
from acquisition import AcquisitionPlugin
from itertools import permutations
import numpy as np
from scipy.signal import convolve2d
from image_process import CellDetectorCellMask, SpotCountLocations, SpotCounter, SpotCountLocationsDoughnut,SpotDetectImagesBooleanDoughnut,ImageCalculateFishPipeline
from distributed_computing import Task,DistributedComputeDaskTask,DistributedComputeLocal
from ndtiff import NDTiffDataset
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
class iPostProcessorPipeline:
    def add(self,key,*args,**kwargs):
        '''add a process which will generate tasks'''
        pass
    def process(self):
        '''compute exisint tasks'''
        pass

class iPostProcessNode:
    def generate(self,dataset,acquisition):
        pass

class iPostProcessLibrary:
    def get(self,key,*args,**kwargs):
        'return process node form key, args kwrags'
        pass

'''
class ProcessedData(dict):
    pass
'''

class OutputMapper:
    def __init__(self):
        self.keys=[]
        self.values=[]

    def __str__(self):
        string=""
        for i in range(len(self.keys)):
            string=string + str(self.keys[i])+" maps to "+str(self.values[i]) + "\n"
        return string

    def __getitem__(self, key):
        if key not in self.keys:
            return KeyError("key not found")
        for i in range(len(self.keys)):
            if key == self.keys[i]:
                return self.values[i]

    def __setitem__(self, key, value):
        if not isinstance(value,dict):
            raise TypeError("value must be dict")
        if key not in self.keys:
            self.keys.append(key)
            self.values.append(value)
        else:
            for i in range(len(self.keys)):
                if key == self.keys[i]:
                    self.values[i].update(value)

    def __delitem__(self, key):
        if key not in self.keys:
            return KeyError("key not found")
        for i in range(len(self.keys)):
            if key == self.keys[i]:
                self.keys.remove(i)
                self.values.remove(i)

class PostProcessPipeline:
    def __init__(self):
        self.node=[]

    def add(self, key, *args, **kwargs):
        if not isinstance(key,str):
            raise TypeError
        lib = PostProcessLibrary()
        processor=lib.get(key, *args, **kwargs)
        self.node.append(processor)


    def addNode(self,node):
        if not isinstance(node,PostProcessNode):
            raise TypeError
        self.node.append(node)


    def process(self,data,acq):
        if not isinstance(acq,AcquisitionPlugin):
            raise TypeError
        outputs=[]
        for i in range(len(self.node)):
            (data,output)=self.node[i].process(data, acq)
            outputs.append(output)
        return outputs

class PostProcessNode(iPostProcessNode):
    def __init__(self,function=None,squish_axes=None,*args,**kwargs):
        self.function=function
        self.name=None
        self.args=args
        self.kwargs=kwargs
        self.axes=None
        self.squish_axes=squish_axes
        if 'computer' in kwargs.keys():
            self.computer=kwargs['computer']
        else:
            self.computer=DistributedComputeLocal()

    def process(self,dataset,acq,*args,**kwargs):
        if not isinstance(acq,AcquisitionPlugin):
            raise TypeError
        items = dataset.get_index_keys() #use a hashtable to project over keys. This section is a headache even if you know what ur doing. Uses a hashtable to squish axes
        if self.squish_axes:
            if self.squish_axes not in items[0].keys():
                raise KeyError('projection axes not found')
        hashed_items={}
        for i in range(len(items)):
            event_props=dict(items[i])
            if self.squish_axes in event_props.keys():
                event_props.pop(self.squish_axes)
            hash_key=frozenset(event_props.items())
            if hash_key not in hashed_items:
                hashed_items[hash_key]=[]
            hashed_items[hash_key].append(items[i])
            print(hashed_items)
        output = OutputMapper()
        for i in hashed_items:
            chunks=[]
            metadatas=[]
            for key in hashed_items[i]:
                chunk = dataset.read_image(**key)# **j will pass the dict as kwargs
                chunks.append(chunk)
                metadata = dataset.read_metadata(**key)
                metadatas.append(metadata)
            task = Task(self.function,self,chunks,metadatas,hashed_items[i])
            (chunk, chunk_output) = task()
            output[i]=chunk_output
        print(output)
        return (dataset,output)


class PostProcessLibrary():
    def __init__(self,computer=DistributedComputeLocal()):
        self.computer=computer
        #print("PLIBRARY:{0}".format(self.computer))

    def get(self, key, *args, **kwargs):
        if not isinstance(key, str):
            raise TypeError
        command = 'self.' + key + '(*args,**kwargs)'
        node = eval(command)
        node.name = key
        return node

    def null(self,squish_axes=None,computer=DistributedComputeLocal()):
        def function(self,chunks,metadatas,events,*args,**kwargs):
            chunks_output={'null':None}
            return (chunks,chunks_output)
        node=PostProcessNode(squish_axes=squish_axes,computer=computer)
        node.function=function
        return node

    def source(self,squish_axes=None,computer=DistributedComputeLocal()):
        def function(self,chunks,metadatas,events,*args,**kwargs):
            chunks_output={'source':chunks}
            return (chunks,chunks_output)
        node = PostProcessNode(squish_axes=squish_axes,computer=computer)
        node.function = function
        return node

    def mean(self,squish_axes=None,computer=DistributedComputeLocal()):
        def function(self,chunks,metadatas,events):
            #print(events)
            chunks_output={'mean':np.mean(chunks)}
            return (chunks,chunks_output)
        node = PostProcessNode(squish_axes=squish_axes,computer=computer)
        node.function = function
        return node

    def mask(self,squish_axes=None,computer=DistributedComputeLocal(),model_type='cyto'):
        def function(self,chunks,metadatas,events):
            #print(events)
            detector=CellDetectorCellMask(model_type=model_type)
            mask=detector.process(chunks)
            chunks_output={'mask':mask}
            return (chunks,chunks_output)
        node = PostProcessNode(squish_axes=squish_axes,computer=computer)
        node.function = function
        return node

    def spotCount(self,squish_axes=None,computer=DistributedComputeLocal(),model_type='cyto'):
        def function(self,chunks,metadatas,events):
            detector=SpotCountLocations()
            locations=detector.process(chunks)
            chunks_output={'spotCount':len(locations)}
            return (chunks,chunks_output)
        node = PostProcessNode(squish_axes=squish_axes,computer=computer)
        node.function = function
        return node

    def spotLocations(self,squish_axes=None,computer=DistributedComputeLocal(),model_type='cyto'):
        def function(self,chunks,metadatas,events):
            detector=SpotCountLocations()
            locations=detector.process(chunks)
            chunks_output={'spotLocations':locations}
            return (chunks,chunks_output)
        node = PostProcessNode(squish_axes=squish_axes,computer=computer)
        node.function = function
        return node

    def spotLocationsDoughnut(self,squish_axes=None,computer=DistributedComputeLocal(),model_type='cyto'):
        def function(self,chunks,metadatas,events):
            detector=SpotCountLocationsDoughnut()
            locations=detector.process(chunks)
            chunks_output={'spotLocationsDoughnut':locations}
            return (chunks,chunks_output)
        node = PostProcessNode(squish_axes=squish_axes,computer=computer)
        node.function = function
        return node

    def cellCount(self,squish_axes=None,computer=DistributedComputeLocal(),default_flow_threshold=.1,MINIMUM_CELL_AREA = 30,model_type= 'nuclei'):
        def function(self,chunks,metadatas,events):
            chunks_output = {}
            detector = CellDetectorCellMask(default_flow_threshold=default_flow_threshold,
                                            MINIMUM_CELL_AREA=MINIMUM_CELL_AREA, model_type=model_type)
            masks=detector.process(chunks)
            chunks_output['cellCount']=np.max(masks)
            return (chunks,chunks_output)
        node = PostProcessNode(squish_axes=squish_axes, computer=computer)
        node.function = function
        return node

    def sharpness(self,squish_axes=None,computer=DistributedComputeLocal()):
        def function(self,chunks,metadatas,events):
            chunks_output = {}
            kernel = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]]).astype('float')
            sharpness=[]
            for i in range(len(chunks)):
                sharpness.append(np.sum(np.abs(convolve2d(chunks[i], kernel))))
            chunks_output['sharpness']=np.sum(sharpness)
            return (chunks,chunks_output)
        node = PostProcessNode(squish_axes=squish_axes, computer=computer)
        node.function = function
        return node

    def sharpest(self,squish_axes=None,computer=DistributedComputeLocal()):
        def function(self,chunks,metadatas,events):
            chunks_output = {}
            kernel = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]]).astype('float')
            sharpness=[]
            for i in range(len(chunks)):
                sharpness.append(np.sum(np.abs(convolve2d(chunks[i], kernel))))
            chunks_output['sharpest_value'] = np.max(sharpness)
            chunks_output['sharpest_index'] = np.argmax(sharpness)
            return (chunks,chunks_output)
        node = PostProcessNode(squish_axes=squish_axes, computer=computer)
        node.function = function
        return node

    def fishPipeline(self,squish_axes=None,computer=DistributedComputeLocal()):
        def function(self,chunks,metadatas,events):
            chunks_output = {}
            return (chunks,chunks_output)
        node = PostProcessNode(squish_axes=squish_axes, computer=computer)
        node.function = function
        return node

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