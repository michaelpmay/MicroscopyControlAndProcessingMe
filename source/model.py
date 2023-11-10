import numpy as np
from scipy.integrate import odeint
class iModel:
    '''This class is a wad of functions and parameters that describes a model.
       Works closely with Solver Classes to create trajectories'''
    def setParamters(self,parameters):
        '''set parameters'''
        pass
    def getParameters(self):
        '''get parmeters'''
        pass
    def setPropensity(self,propensity):
        '''set propensity function'''
        pass
    def getPropensity(self,propensity):
        '''get propensity function'''
        pass
    def getdxdt(self):
        '''Returns rate(x,t)=S*W(x,t,p) which is a function that can be evaulated as rate(x,t)'''
        pass

class iTrajectory():
    '''this class defines the trajectory'''
    pass

class iTrajectories():
    '''this class defines many trajectories'''
    pass

class iModelParameters:
    def setBounds(self,bounder):
        '''set bounds by using a bounder object that trims bounds'''
        pass
    def setMap(self,coordinates):
        '''set coordinate map by using a map object that maps parameters.
        This object helps facilitate parameter searches in linear/log/sigmoid space.
        Defaults to simple Map
        '''
        pass
    def set(self,index,parameters):
        '''set individual parameter'''
        pass
    def get(self,index):
        '''get all parameters'''
        pass
    def setAll(self,parameters):
        '''set individual parameter'''
        pass
    def getAll(self):
        '''get all parameters'''
        pass

class StateTrajectory(iTrajectory):
    def __init__(self,*args):
        if len(args)==2:
            time=np.array(args[0],dtype='double')
            state = np.array(args[1],dtype='double')
        elif len(args)==0:
            time=np.array([],dtype='double')
            state=np.array([],dtype='double')
        else:
            raise ValueError
        self.time=time
        self.state=state
    def setTime(self,time):
        self.time=time
    def getTime(self):
        return self.time
    def setState(self,state):
        self.state=state
    def getState(self):
        return self.state

class ProbabilityTrajectory(iTrajectory):
    def __init__(self,*args):
        if len(args)==2:
            time=np.array(args[0],dtype='double')
            state = np.array(args[1],dtype='double')
        elif len(args)==0:
            time=np.array([],dtype='double')
            state=np.array([],dtype='double')
        else:
            raise ValueError
        self.time=time
        self.state=state
    def setTime(self,time):
        self.time=time
    def getTime(self):
        return self.time
    def setState(self,state):
        self.state=state
    def getState(self):
        return self.state

class StateTrajectories(iTrajectories):
    def __init__(self):
        self.repetition=[]
    def add(self,trajectory):
        if not isinstance(trajectory,StateTrajectory):
            raise TypeError
        self.repetition.append(trajectory)

class Model:
    parameters=None
    propensity=lambda t,x,p: None
    stoichiometry=None
    state=None
    time=None
    def __init__(self):
        self.parameters=ModelParameters()
    def setParameters(self,parameters,bounds=None):
        if isinstance(parameters,list):
            parameters=np.array(parameters,dtype='double')
        if not isinstance(parameters,(ModelParameters)):
            raise TypeError
        if isinstance(parameters,np.ndarray):
            self.parameters=ModelParameters(parameters,bounds=bounds)

    def setParameter(self,index,parameter,bounds=None):
        self.parameters.set(index,parameter,bounds=bounds)

    def setAllParameters(self,parameters,bounds=None):
        self.parameters.setAll(parameters,bounds=bounds)

    def getParameters(self):
        return self.parameters.getAll()

    def getPropensity(self):
        return self.propensity

    def setTime(self,time):
        if isinstance(time,list):
            time=np.array(time,dtype='double')
        if not isinstance(time,np.ndarray):
            raise TypeError
        self.time=time

    def getTime(self):
        return self.time

    def setState(self, state):
        if isinstance(state,list):
            time=np.array(state,dtype='double')
        if not isinstance(state,np.ndarray):
            raise TypeError
        self.state=state

    def getState(self):
        return self.state

    def setStoichiometry(self,stoichiometry):
        self.stoichiometry=stoichiometry

    def getStoichiometry(self):
        return self.stoichiometry

    def getdxdt(self):
        p=self.parameters.getAll()
        return lambda x,t:self.stoichiometry @ self.propensity(t,x,p)

    def evalpropensity(self,t,x):
        p = self.parameters.getAll()
        return self.propensity(t, x, p)


class CoordinateMap():
    def __init__(self,*args):
        pass

    def map(self, parameters):
        if isinstance(parameters,list):
            parameters=np.array(parameters,dtype='double')
        if not isinstance(parameters, np.ndarray):
            raise TypeError
        mapped_parameters = parameters
        return mapped_parameters
    def inverse(self,parameters):
        return parameters

class LogCoordinateMap:
    def __init__(self,*args):
        pass
    def map(self, parameters):
        if isinstance(parameters, list):
            parameters = np.array(parameters,dtype='double')
        if not isinstance(parameters, np.ndarray):
            raise TypeError
        mapped_parameters = np.log(parameters)
        return mapped_parameters
    def inverse(self,parameters):
        if isinstance(parameters, list):
            parameters = np.array(parameters,dtype='double')
        if not isinstance(parameters, np.ndarray):
            raise TypeError
        return np.exp(parameters)

class SigmoidCoordinateMap:
    def __init__(self):
        self.amplitude=1.
        self.rate=1.
    def map(self,parameters):
        if isinstance(parameters,list):
            parameters=np.array(parameters,dtype='double')
        if not isinstance(parameters,np.ndarray):
            raise TypeError
        mapped_parameters = self.amplitude/(1+np.exp(-parameters*self.rate))
        return mapped_parameters
    def inverse(self,parameters):
        if isinstance(parameters, list):
            parameters = np.array(parameters,dtype='double')
        if not isinstance(parameters, np.ndarray):
            raise TypeError
        mapped_parameters=-np.log(self.amplitude/parameters-1)/self.rate
        return mapped_parameters


class ModelParameters(iModelParameters):
    bounds=None
    coordinates=None
    parameters=None
    def __init__(self,*args,bounds=None,coordinates=CoordinateMap()):
        if len(args)==1:
            parameters=args[0]
            if isinstance(parameters, list):
                parameters = np.array(parameters,dtype='double')
            if not isinstance(parameters, np.ndarray):
                raise TypeError
        elif len(args)>1:
            raise ValueError
        else:
            parameters=[]
        if bounds is not None:
            if isinstance(bounds,list):
                bounds=np.array(bounds)
            if not isinstance(bounds,np.ndarray):
                raise TypeError
        self.bounds=bounds
        self.coordinates=coordinates
        if bounds is not None:
            self.setAll(parameters,bounds=bounds)
        else:
            self.setAll(parameters)
        self.isConverted=False

    def set(self,index,parameter,bounds=None):
        if isinstance(parameter,int):
            parameter=float(parameter)
        if not isinstance(parameter,(float)):
            raise TypeError
        if bounds is not None:
            if parameter < bounds[0]:
                parameter = bounds[0]
            if parameter > bounds[1]:
                parameter = bounds[1]
        maxLength=max(len(self.parameters),index+1)
        parameters=np.zeros(maxLength)
        for i in range(len(self.parameters)):
            parameters[i]=self.parameters
        parameters[index]=parameter
        self.parameters=parameters


    def setAll(self,parameters,bounds=None):
        if isinstance(parameters, list):
            parameters = np.array(parameters,dtype='double')
        if not isinstance(parameters, np.ndarray):
            raise TypeError
        self.parameters=np.array(parameters,dtype='double')
        if bounds is not None:
            for i in range(len(parameters)):
                if self.parameters[i] < bounds[i][0]:
                    self.parameters[i] = bounds[i][0]
                if self.parameters[i] > bounds[i][1]:
                    self.parameters[i] = bounds[i][1]

    def get(self,index):
        return self.parameters[index]

    def getAll(self):
        return self.parameters

    def convert(self):
        if not self.isConverted:
            self.parameters=self.coordinates.map(self.parameters)
            self.isConverted=True
        if self.isConverted:
            self.parameters=self.coordinates.inverse(self.parameters)
            self.isConverted=False



class ModelLibrary:
    def get(self,key):
        command='self.'+key+'()'
        model=eval(command)
        return model
    def birthDecay(self):
        model = Model()
        model.time = np.linspace(0, 5)
        model.state = np.array([0]).T
        model.stoichiometry = np.array([[1, -1]])
        model.propensity = lambda t, x, p: np.array([p[0], p[1] * x[0]]).T
        model.setAllParameters(np.array([10, 1]))
        return model

    def birthDecay2D(self):
        model = Model()
        model.time = np.linspace(0, 5)
        model.state = np.array([0,0]).T
        model.stoichiometry = np.array([[1, -1,0,0], [0,0,1,-1]])
        model.propensity = lambda t, x, p: np.array([p[0], p[1] * x[0],p[2],p[3]*x[1]]).T
        model.setAllParameters(np.array([10, 1,2,3]))
        return model


    def burstingGeneExpression(self):
        model = Model()
        model.time = np.linspace(0, 100,1000)
        model.state = np.array([0,0]).T
        model.propensity = lambda t, x, p: np.array([p[0]*(1-x[0]),p[1]*x[0],p[2]*x[0],p[3]*x[1]]).T
        model.stoichiometry = np.array([[1, -1, 0, 0], [0, 0, 1, -1]])
        model.setAllParameters(np.array([.1, .5,10,1]))
        return model

    def geneticToggle(self):
        model = Model()
        model.time = np.linspace(0, 50, 1000)
        model.state = np.array([0, 0]).T
        model.propensity = lambda t, x, p: np.array([p[0]+p[1]/(1+p[4]*x[0]**p[4]),p[6]*x[0],p[7]+p[8]/(1+p[9]*x[1]**p[10]),p[11]*x[1]]).T
        model.stoichiometry = np.array([[1, -1, 0, 0], [0, 0, 1, -1]])
        model.setAllParameters(np.array([1,1,1,1,1,1,1,1,1,1,1,1]))
        return model

    def birthDecay2DTimeVarying(self):
        model = Model()
        model.time = np.linspace(0, 5)
        model.state = np.array([0,0]).T
        model.stoichiometry = np.array([[1, -1,0,0], [0,0,1,-1]])
        model.propensity = lambda t, x, p: np.array([p[0]*(1+np.sin(t*2*np.pi/10)), p[1] * x[0],p[2]*(1+np.sin(t*2*np.pi/10)),p[3]*x[1]]).T
        model.setAllParameters(np.array([5,1,5,1]))
        return model

    def stochasticResonance(self):
        model=Model()
        model.time=np.linspace(0,5)
        model.state=np.array([0, 0,0])
        model.stoichiometry = np.array([[-1, 1, 0, 0],
                                        [1, -1, 0, 0],
                                        [0,0, 1, -1 ]])
        model.propensity = lambda t,x,p: np.array([x[0]*x[2]**p[0]/(p[1]**p[0]+x[2]**p[0]),p[2]*x[1]/(1+x[2]**p[0]),p[3]*x[1],p[4]*x[2]]).T
        model.setAllParameters(np.array([10,1000,100,20,0.02]))

    def autoregulationModel(self):
        model = Model()
        model.time = np.linspace(0, 5)
        model.state = np.array([0, 0]).T
        model.stoichiometry = np.array([[1, -1, 0, 0], [0, 0, 1, -1]])
        model.propensity = lambda t, x, p: 10 * np.array(
            [p[0] * (1 + np.sin(t * 2 * np.pi / 10)), p[1] * x[0], p[2] * (1 + np.sin(t * 2 * np.pi / 10)),
             p[3] * x[1]]).T
        model.parameters = np.array([5, 1, 5, 1])
        return model

    def explosionExtinctionModel(self):
        model=Model()
        model.time=np.linspace(0,100)
        model.state=np.array([20])
        model.stoichiometry=np.array([[1,-1]])
        model.setAllParameters(np.array([.05/19,.05]))
        def propensity(t,x,p):
            w1 = p[0] * x[0] * (x[0] - 1)
            w2 = p[1] * x[0]
            if x[0]>500:
                w1=0.00000000001
                w2=0.00000000001
            if w1==0:
                w1=0.00000000001
            if w2==0:
                w2=0.00000000001
            return np.array([w1,w2]).T
        model.propensity=propensity
        return model

class IntegratorODE:
    def integrate(self, model):
        if not isinstance(model,Model):
            raise TypeError
        equation = model.getdxdt()
        time = model.getTime()
        state = odeint(equation, model.state, time)
        return StateTrajectory(time, state)
class SolverODE:
    model=Model()
    def __init__(self):
        self.integrator=IntegratorODE()

    def run(self,model):
        return self.integrator.integrate(model)

    def getTime(self):
        if len(self.model.time)==2:
            return np.linspace(self.model.time[0],self.model.time[-1])
        else:
            return self.model.time

    def accept(self,visitor):
        return visitor.visit(self)

class IntegratorSSAParsed:
    verbose=False

    def run(self,model,*args):
        if len(args)==1:
            numRuns=args[0]
        else:
            numRuns=1
        return self.runTrajectories(model,numRuns)
    def runTrajectories(self,model,numRuns):
        trajectories=StateTrajectories()
        for i in range(numRuns):
            trajectory=self.runSingleTrajectory(model)
            trajectories.add(trajectory)
        return trajectories
    def runSingleTrajectory(self,model):
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
        return StateTrajectory(timeHistory,stateHistory.T)
    def getInitialHistory(self,model):
        n=len(model.time)
        m=len(model.state)
        stateHistory=np.zeros([m,n])
        stateHistory[::,0]=model.state
        time=model.time
        return (stateHistory,time)

    def getCumulativeRate(self,time,state,model):
        rate=model.evalpropensity(time,state)
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
    intgrator=IntegratorSSAParsed()
    def __init__(self):
        self.intgrator=IntegratorSSAParsed()

    def run(self,model,*args):
        if len(args)==0:
            numRuns=1
        elif len(args)==1:
            numRuns=args[0]
            if numRuns<1:
                raise ValueError
        else:
            raise ValueError
        return self.intgrator.run(model,numRuns)

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
        stateSpaceStoich = np.zeros(stateSpaceDims)
        numReactions = self.model.stoichiometry.shape
        errorStoich = np.zeros(self.dims)
        for i in range(numReactions[1]):
            (newStateSpaceStoich,newError)=self.makeSingleReactionInfGenSync( i, time)
            stateSpaceStoich = stateSpaceStoich + newStateSpaceStoich
            errorStoich  = errorStoich+newError
        return (stateSpaceStoich,errorStoich)

    def getInfGenTensorWithoutError(self,time):
        stateSpaceDims = np.concatenate((self.dims, self.dims))
        stateSpaceStoich = np.zeros(stateSpaceDims)
        numReactions = self.model.stoichiometry.shape
        for i in range(numReactions[1]):
            stateSpaceStoich = stateSpaceStoich + self.makeSingleReactionInfGen( i, time)
        return stateSpaceStoich
    def makeSingleReactionInfGen(self,dims,i):
        #print('Error: Overwrite this function to complete functionality')
        pass

    def connectStates(self,fromState,toState,stateSpaceStoich,reactionIndex,time):
        propensity=self.model.evalpropensity(time,fromState)[reactionIndex]
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
            pass
        return core
class FSPGenerator1D(FSPGeneratorCore):
    def makeSingleReactionInfGen(self,reactionIndex,time):
        xMap=list(range(0,self.dims[0]))
        stateSpaceDims=np.concatenate((self.dims,self.dims))
        stateSpaceStoich=np.zeros(stateSpaceDims)
        rxnVector=self.model.stoichiometry[::,reactionIndex]
        for i in range(len(xMap)):
            state=np.array([xMap[i]])
            if self.isInStateSpace(state+rxnVector,self.dims):
                stateSpaceStoich=self.connectStates(state,state+rxnVector,stateSpaceStoich,reactionIndex,time)
        return stateSpaceStoich

    def makeSingleReactionInfGenSync(self,reactionIndex,time):
        xMap=list(range(0,self.dims[0]))
        stateSpaceDims=np.concatenate((self.dims,self.dims))
        stateSpaceStoich=np.zeros(stateSpaceDims)
        errorStoich = np.zeros(self.dims)
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
        stateSpaceStoich = np.zeros(stateSpaceDims)
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
        stateSpaceStoich=np.zeros(stateSpaceDims)
        errorStoich = np.zeros(self.dims)
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
    generator=FSPGenerator()
    dims=np.array([])
    sink=False
    isTimeVarying=False
    def __init__(self,dims):
        self.dims=dims

    def run(self,model):
        state=self.getState(model)
        maxInd=len(model.time)
        P=np.zeros([len(state),maxInd])
        P[::,0]=state.flatten()
        infGen = self.getInfGenerator(model,model.time[0])
        for i in range(1,maxInd):
            deltaT=model.time[i]-model.time[i-1]
            if self.isTimeVarying:
                infGen=self.getInfGenerator(model,model.time[i])
            trajectory=odeint(lambda P,t: infGen @ P,state,[0, deltaT])
            state = trajectory[1,:]
            P[::,i]=state
        trajectory=ProbabilityTrajectory(model.time,np.array(P).T)
        return trajectory

    def getInfGenerator(self,model,time):
        return self.generator.getInfGenerator(model,self.dims,self.sink,time)

    def getState(self,model):
        if len(model.state)==np.prod(self.dims):
            state=model.state
        else:
            state=np.zeros(self.dims)
            state[tuple(model.state)]=1
            state=np.reshape(state,np.prod(self.dims))
        if self.sink:
            state=np.concatenate((state,[0]))
        return state

class SolverSensitvity:
    def __init__(self,solver):
        self.solver=solver
        self.dp=.0001
    def run(self,model):
        origional_parameters=model.getParameters()
        origional_trajectory=self.solver.run(model)
        for i in range(len(origional_parameters)):
            model.setAllParameters(origional_parameters)
            p=origional_parameters[i]*(1+self.dp)
            model.setParameter(i,p)
            new_trajectory=self.solver.run(model)
            dStatedp=(new_trajectory.getState()-origional_trajectory.getState())/(origional_parameters[i]*self.dp)

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
    trajectory=ode.run()
    return trajectory.time,trajectory.state

def solveSSA(time,intialState,stoichiometry,propensity,parameters):
    model=newModel(time,intialState,stoichiometry,propensity,parameters)
    ssa = SolverSSA(model)
    trajectory = ssa.run()
    return trajectory.time, trajectory.state

def solveFSP(time,intialState,stoichiometry,propensity,parameters,dimensions,isTimeVarying=False,sink=True):
    model=newModel(time,intialState,stoichiometry,propensity,parameters)
    fsp = SolverFSP(model,dimensions)
    fsp.isTimeVarying=isTimeVarying
    fsp.sink=sink
    trajectory = fsp.run()
    return trajectory.time, trajectory.state

def makeInfGenerator(stoichiometry,propensity,parameters,dimensions,sink=True):
    model=Model()
    model.time=np.linspace(0,1)
    model.stoichiometry=stoichiometry
    model.propensity=propensity
    model.parameters=parameters
    fsp=SolverFSP(model,dimensions)
    return fsp.getInfGenerator(0)

