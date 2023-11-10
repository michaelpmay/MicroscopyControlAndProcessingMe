from utility.Model import *
from utility.Data import *
from utility.preallocate import preallocate
import numpy as np
from scipy.integrate import odeint
from scipy.linalg  import expm

class SolverODE:
    model=Model()
    def __init__(self,model):
        try:
            self.model=model
        except:
            pass

    def run(self):
        equation=self.model.getRateEquation()
        time=self.getTime()
        state=odeint(equation,self.model.state,time)
        return Data(time,state)

    def getTime(self):
        if len(self.model.time)==2:
            return np.linspace(self.model.time[0],self.model.time[-1])
        else:
            return self.model.time

    def accept(self,visitor):
        return visitor.visit(self)

class IntegratorSSAParsed:
    verbose=False

    def run(self,model):
        return self.runTrajectory(model)

    def runTrajectory(self,model):
        (stateHistory,timeHistory)=self.getInitialHistory(model)
        finalTime=model.time[-1]
        time=timeHistory[0]
        state=stateHistory[::,0]
        timeStep=model.time[0]
        n=len(timeHistory)
        printTimes=np.linspace(model.time[0],model.time[-1],101)
        printIndex=0
        ind=0
        while time<finalTime:
            rate=self.getCumulativeRate(time,state,model)
            time=self.stepToNewTime(time,rate)
            while time >= timeStep:
                stateHistory[::,ind]=state
                if ind<=(n-2):
                    ind=ind+1
                    timeStep=timeHistory[ind]
                else:
                    break
            state=self.stepToNewState(state,rate,model)
            if self.verbose and time>printTimes[printIndex]:
                printIndex=printIndex+1
                #print(time)
                #print(state)
        return Data(timeHistory,stateHistory.T)
    def getInitialHistory(self,model):
        n=len(model.time)
        m=len(model.state)
        stateHistory=preallocate([m,n])
        stateHistory[::,0]=model.state
        time=model.time
        return (stateHistory,time)

    def getCumulativeRate(self,time,state,model):
        rate=model.evaluatePropensity(time,state)
        cumRate=np.cumsum(rate)
        return cumRate

    def stepToNewTime(self,time,rate):
        time=time-np.log(np.random.rand())/rate[-1]
        return time

    def stepToNewState(self,state,rate,model):
        event=np.argwhere(rate>(rate[-1]*np.random.rand())).min()
        state=state+model.stoichiometry[::,event]
        return state

class SolverSSA:
    model=Model()
    intgrator=IntegratorSSAParsed()
    def __init__(self,model):
        self.model=model

    def run(self):
        return self.intgrator.run(self.model)

class FSPGeneratorCore:
    model=Model()
    dims=None
    def __init__(self,model,dims,gBool):
        self.model=model
        self.dims=dims
        self.gBool=gBool
    def getInfGenerator(self,time):
        N=np.prod(self.dims)
        infGenerator=self.getInfGeneratorReshape(time)
        return infGenerator

    def getInfGeneratorReshape(self,time):
        N = np.prod(self.dims)
        if not self.gBool:
            infGenerator=self.getInfGenTensorWithoutError(time)
            infGenerator = np.reshape(infGenerator, [N, N])
            return infGenerator
        else:
            (partialInfGenerator,errorGenerator)= self.getInfGenTensorWithError(time)
            partialInfGenerator = np.reshape(partialInfGenerator, [N, N])
            infGenerator=np.zeros([N+1,N+1])
            infGenerator[:N,:N]=partialInfGenerator
            infGenerator[N,:N]=np.reshape(errorGenerator,np.prod(self.dims))
            return infGenerator

    def getInfGenTensorWithError(self,time):
        stateSpaceDims = np.concatenate((self.dims, self.dims))
        stateSpaceStoich = preallocate(stateSpaceDims)
        numReactions = self.model.stoichiometry.shape
        errorStoich = preallocate(self.dims)
        for i in range(numReactions[1]):
            (newStateSpaceStoich,newError)=self.makeSingleReactionInfGenSync( i, time)
            stateSpaceStoich = stateSpaceStoich + newStateSpaceStoich
            errorStoich  = errorStoich+newError
        return (stateSpaceStoich,errorStoich)

    def getInfGenTensorWithoutError(self,time):
        stateSpaceDims = np.concatenate((self.dims, self.dims))
        stateSpaceStoich = preallocate(stateSpaceDims)
        numReactions = self.model.stoichiometry.shape
        for i in range(numReactions[1]):
            stateSpaceStoich = stateSpaceStoich + self.makeSingleReactionInfGen( i, time)
        return stateSpaceStoich
    def makeSingleReactionInfGen(self,dims,i):
        #print('Error: Overwrite this function to complete functionality')

    def connectStates(self,fromState,toState,stateSpaceStoich,reactionIndex,time):
        propensity=self.model.evaluatePropensity(time,fromState)[reactionIndex]
        toIndex=np.concatenate((toState,fromState))
        fromIndex=np.concatenate((fromState,fromState))
        stateSpaceStoich[tuple(toIndex)]=propensity
        stateSpaceStoich[tuple(fromIndex)]=-propensity
        return stateSpaceStoich

    def connectSyncStates(self,fromState,toState,stateSpaceStoich,errorStoich,reactionIndex,time):
        propensity=self.model.evaluatePropensity(time,fromState)[reactionIndex]
        fromIndex=np.concatenate((fromState,fromState))
        errorStoich[tuple(fromState)]=propensity
        stateSpaceStoich[tuple(fromIndex)]=-propensity
        return (stateSpaceStoich,errorStoich)

    def isInStateSpace(self,state,dims):
        tfBool=True
        for i in range(len(state)):
            if (state[i]>=dims[i]) or (state[i]<0):
                tfBool=False
        return tfBool

    def isInSync(self,state,dims):
        tfBool = False
        for i in range(len(state)):
            if (state[i] >= dims[i]) and (state[i] > 0):
                tfBool = True
        return tfBool

class FSPGenerator:
    core=None

    def getInfGenerator(self,model,dims,gBool,time):
        core=self.getCore(model,dims,gBool)
        infGenerator=core.getInfGenerator(time)
        return infGenerator

    def getCore(self,model,dims,gBool):
        N=len(dims)
        if N==3:
            core=FSPGenerator3D(model,dims,gBool)
        elif N==2:
            core=FSPGenerator2D(model,dims,gBool)
        elif N==1:
            core=FSPGenerator1D(model,dims,gBool)
        else:
            #print('Error: Generator is only supported up for 1, 2 and 3 unique species')
        return core
class FSPGenerator1D(FSPGeneratorCore):
    def makeSingleReactionInfGen(self,reactionIndex,time):
        xMap=list(range(0,self.dims[0]))
        stateSpaceDims=np.concatenate((self.dims,self.dims))
        stateSpaceStoich=preallocate(stateSpaceDims)
        rxnVector=self.model.stoichiometry[::,reactionIndex]
        for i in range(len(xMap)):
            state=np.array([xMap[i]])
            if self.isInStateSpace(state+rxnVector,self.dims):
                stateSpaceStoich=self.connectStates(state,state+rxnVector,stateSpaceStoich,reactionIndex,time)
        return stateSpaceStoich

    def makeSingleReactionInfGenSync(self,reactionIndex,time):
        xMap=list(range(0,self.dims[0]))
        stateSpaceDims=np.concatenate((self.dims,self.dims))
        stateSpaceStoich=preallocate(stateSpaceDims)
        errorStoich = preallocate(self.dims)
        rxnVector=self.model.stoichiometry[::,reactionIndex]
        for i in range(len(xMap)):
            state=np.array([xMap[i]])
            if self.isInStateSpace(state+rxnVector,self.dims):
                stateSpaceStoich=self.connectStates(state,state+rxnVector,stateSpaceStoich,reactionIndex,time)
            elif self.isInSync(state+rxnVector,self.dims):
                stateSpaceStoich,errorStoich = self.connectSyncStates(state, state + rxnVector, stateSpaceStoich,errorStoich, reactionIndex,
                                                      time)
        return (stateSpaceStoich,errorStoich)

class FSPGenerator2D(FSPGeneratorCore):
    def makeSingleReactionInfGen(self,reactionIndex,time):
        xMap=list(range(0,self.dims[0]))
        yMap=list(range(0,self.dims[1]))
        stateSpaceDims = np.concatenate((self.dims, self.dims))
        stateSpaceStoich = preallocate(stateSpaceDims)
        rxnVector = self.model.stoichiometry[::, reactionIndex]
        for i in range(len(xMap)):
            for j in range(len(yMap)):
                state=np.array([xMap[i],yMap[j]])
                if self.isInStateSpace(state+rxnVector,self.dims):
                    stateSpaceStoich=self.connectStates(state,state+rxnVector,stateSpaceStoich,reactionIndex,time)
        return stateSpaceStoich

    def makeSingleReactionInfGenSync(self,reactionIndex,time):
        xMap=list(range(0,self.dims[0]))
        yMap = list(range(0, self.dims[1]))
        stateSpaceDims=np.concatenate((self.dims,self.dims))
        stateSpaceStoich=preallocate(stateSpaceDims)
        errorStoich = preallocate(self.dims)
        rxnVector=self.model.stoichiometry[::,reactionIndex]
        for i in range(len(xMap)):
            for j in range(len(yMap)):
                state=np.array([xMap[i],yMap[j]])
                if self.isInStateSpace(state+rxnVector,self.dims):
                    stateSpaceStoich=self.connectStates(state,state+rxnVector,stateSpaceStoich,reactionIndex,time)
                elif self.isInSync(state+rxnVector,self.dims):
                    stateSpaceStoich,errorStoich = self.connectSyncStates(state, state + rxnVector, stateSpaceStoich,errorStoich, reactionIndex,
                                                      time)
        return (stateSpaceStoich,errorStoich)

class FSPGenerator3D(FSPGeneratorCore):
    def makeSingleReactionInfGen(self,reactionIndex,time):
        pass



class SolverFSP:
    model=Model()
    generator=FSPGenerator()
    dims=np.array([])
    sink=False
    isTimeVarying=False
    def __init__(self,model,dims):
        self.model=model
        self.dims=dims

    def run(self):
        state=self.getState()
        maxInd=len(self.model.time)
        P=preallocate([len(state),maxInd])
        P[::,0]=state.flatten()
        infGen = self.getInfGenerator(self.model.time[0])
        for i in range(1,maxInd):
            deltaT=self.model.time[i]-self.model.time[i-1]
            if self.isTimeVarying:
                infGen=self.getInfGenerator(self.model.time[i])
            trajectory=odeint(lambda P,t: infGen @ P,state,[0, deltaT])
            state = trajectory[1,:]
            P[::,i]=state

        data=Data(self.model.time,np.array(P).T)
        return data

    def getInfGenerator(self,time):
        return self.generator.getInfGenerator(self.model,self.dims,self.sink,time)

    def getState(self):
        if len(self.model.state)==np.prod(self.dims):
            state=self.model.state
        else:
            state=np.zeros(self.dims)
            state[tuple(self.model.state)]=1
            state=np.reshape(state,np.prod(self.dims))
        if self.sink:
            state=np.concatenate((state,[0]))
        return state

def newModel(time,intialState,stoichiometry,propensity,parameters):
    model = Model()
    model.time = time
    model.state = intialState
    model.stoichiometry = stoichiometry
    model.propensity = propensity
    model.parameters = parameters
    return model

def solveODE(time,intialState,stoichiometry,propensity,parameters):
    model=newModel(time,intialState,stoichiometry,propensity,parameters)
    ode=SolverODE(model)
    data=ode.run()
    return data.time,data.state

def solveSSA(time,intialState,stoichiometry,propensity,parameters):
    model=newModel(time,intialState,stoichiometry,propensity,parameters)
    ssa = SolverSSA(model)
    data = ssa.run()
    return data.time, data.state

def solveFSP(time,intialState,stoichiometry,propensity,parameters,dimensions,isTimeVarying=False,sink=True):
    model=newModel(time,intialState,stoichiometry,propensity,parameters)
    fsp = SolverFSP(model,dimensions)
    fsp.isTimeVarying=isTimeVarying
    fsp.sink=sink
    data = fsp.run()
    return data.time, data.state

def makeInfGenerator(stoichiometry,propensity,parameters,dimensions,sink=True):
    model=Model()
    model.time=np.linspace(0,1)
    model.stoichiometry=stoichiometry
    model.propensity=propensity
    model.parameters=parameters
    fsp=SolverFSP(model,dimensions)
    return fsp.getInfGenerator(0)

import matplotlib.pyplot as plt
from  utility.ModelBuilder import *
def makeExplosionExtinctionSSAPlot():
    builder=ModelBuilder()
    model=builder.explosionExtinctionModel()
    ssa=SolverSSA(model)
    figure=plt.figure()
    for i in range(10):
        data=ssa.run()
        plt.plot(data.time,data.state)
