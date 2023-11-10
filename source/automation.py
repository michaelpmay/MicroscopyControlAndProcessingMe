import time
from collections import OrderedDict
class iBlock:
    '''block is a node of an automation algorithm, it will execute a fucntion and then point to the next block.
    each block can have multiple next blocks. the next block can receive information from the previous block through an
    input parameter. BLocks also have thier own properties from a properties parameter'''
    def output(self):
        '''runs the function with the properties to do something. accepts the retun value of the previous'''
        pass
    pass
    def start(self):
        '''starts the block. not important for many blocks but important for timing blocks'''
        self.starter(self)
        pass


class iSignal:
    '''variable which may or may not change over time. Blocks and signals work together to create an automation pipline'''
    variable=None
    pass


class Block(iBlock):
    def __init__(self,function=None,input=None):
        self.function=function
        self.input=input
        self.output=None
        self.properties=dict()
        self.starter=lambda self: None

    def execute(self):
        self.output = self.function(self.input,self.properties)

    def start(self):
        self.starter(self)


class AutomationBlockModel:
    '''contains a pool of blocks which may or may not point to eachother. executing the automation starts at the head node and executes
    until it reaches the end.'''
    pool=None
    input=None
    output=None
    time=None
    def __init__(self,name):
        self.pool=OrderedDict()
        self.input = OrderedDict()
        self.output = OrderedDict()
        self.iomap=OrderedDict()
        self.name=name

    def execute(self):
        for key,block in self.pool.items():
            if len(block.input)==0:
                boolExecute=True
            else:
                boolExecute = True
                for input in block.input:
                    if input is None:
                        boolExecute = False
            if boolExecute:
                block.execute()
                for i in range(len(block.output)):
                    link_key=key+"-"+str(i)
                    self.update(link_key,block.output[i])

    def addBlock(self,key,block):
        if key in self.pool.keys():
            raise ValueError
        self.pool[key]=block
        for i in range(len(block.output)):
            link_key=key+"-"+str(i)
            self.iomap[link_key]= []
        for i in range(len(block.input)):
            link_key=key+"-"+str(i)
            self.input[link_key]= block.input[i]

    def link(self,input_key,output_key):
        if output_key not in self.iomap.keys():
            self.iomap[output_key]=[]
        if input_key not in self.iomap[output_key]:
            self.iomap[output_key].append(input_key)

    def update(self,key,value):
        subscribers=self.iomap[key]
        for subscriber in subscribers:
            [block_key,index]=self.parsekey(subscriber)
            self.pool[block_key].input[index]=value

    def parsekey(self,key):
        index=key.find('-')
        block_key=key[0:(index)]
        index_key=int(key[(index+1):])
        return [block_key,index_key]

    def unlink(self,targetBlock,nextBlock):
        # todo
        pass


class BlockLibrary:
    @staticmethod
    def null():
        def function(input,properties):
            pass
        block=Block()
        block.function=function
        block.input=[]
        block.output=[]
        pass

    @staticmethod
    def ifThen(condition):
        def function(input,properties):
            if condition():
                return [True,False]
            else:
                return [False, True]
            pass
        block=Block()
        block.function=function
        block.input=[None]
        block.output=[None,None]

    @staticmethod
    def add():
        def function(input,properties):
            return [input[0]+input[1]]
        block=Block()
        block.function=function
        block.input = [None,None]
        block.output = [None]
        return block

    @staticmethod
    def value(v):
        def function(input, properties):
            return [properties[0]]

        block = Block()
        block.function = function
        block.properties=[v]
        block.input = []
        block.output = [None]
        return block

    @staticmethod
    def subtract():
        def function(input, properties):
            return [input[0] - input[1]]

        block = Block()
        block.function = function
        block.input = [None, None]
        block.output = [None]
        return block

    @staticmethod
    def multiply():
        def function(input,properties):
            return [input[0]*input[1]]

        block = Block()
        block.function = function
        block.input = [None, None]
        block.output = [None]
        return block

    @staticmethod
    def divide():
        def function(input, properties):
            return [input[0] / input[1]]

        block = Block()
        block.function = function
        block.input = [None, None]
        block.output = [None]
        return block

    @staticmethod
    def timeMilliSeconds():
        block = Block()

        def starter(self):
            self.properties['start']=time.time()

        def function(input, properties):
            return (time.time() - properties['start'])

        block.starter = starter
        block.function = function
        block.input = []
        block.output = [None]
        return block

    @staticmethod
    def timeSeconds():
        block = Block()

        def starter(self):
            self.properties['start']=time.time()

        def function(input, properties):
            return (time.time() - properties['start'])

        block.starter = starter
        block.function = function
        block.input = []
        block.output = [None]
        return block

    @staticmethod
    def timeMinutes():
        block = Block()

        def starter(self):
            self.properties['start']=time.time()

        def function(input, properties):
            return (time.time() - properties['start'])/60

        block.starter = starter
        block.function = function
        block.input = []
        block.output = [None]
        return block

    @staticmethod
    def timeHours():
        block = Block()

        def starter(self):
            self.properties['start']=time.time()

        def function(input, properties):
            return (time.time() - properties['start'])/60/60

        block.starter = starter
        block.function = function
        block.input = []
        block.output = [None]
        return block

    @staticmethod
    def pulseMilliSeconds(period):
        block=Block()
        def starter(self):
            self.properties['startTime']=time.time()*1000 #universal time in MS
            self.properties['period'] = period#period in MS
            self.properties['loopedTime']=0 #previousLoopTime

        def function(input, properties):
            deltat=(time.time() * 1000 - properties['startTime'])
            loopTime = deltat % properties['period']
            if loopTime<properties['loopedTime']: #if new loop time went from high to 0
                properties['loopedTime'] = loopTime
                return 1
            else:
                properties['loopedTime'] = loopTime
                return 0
        block.starter = starter
        block.function = function
        block.input = []
        block.output = [None]
        return block

    @staticmethod
    def pulseSeconds(period):
        block = Block()

        def starter(self):
            self.properties['startTime'] = time.time()  # universal time in MS
            self.properties['period'] = period  # period in MS
            self.properties['loopedTime'] = 0  # previousLoopTime

        def function(input, properties):
            deltat = (time.time() - properties['startTime'])
            loopTime = deltat % properties['period']
            if loopTime < properties['loopedTime']:  # if new loop time went from high to 0
                properties['loopedTime'] = loopTime
                return 1
            else:
                properties['loopedTime'] = loopTime
                return 0

        block.starter = starter
        block.function = function
        block.input = []
        block.output = [None]
        return block

    @staticmethod
    def stateChange(self,key,value):
        def function(input,properties):
            pass
        pass

    @staticmethod
    def ifThen(self,conditional,trueBlock,falseBlock):
        # todo
        pass

    @staticmethod
    def whileThen(self,conditional,trueBlock,falseBlock):
        # todo
        pass

    @staticmethod
    def timedexecute(self,time):
        # todo
        pass

    @staticmethod
    def snapImageFromPulse(self,time):
        #todo
        pass

