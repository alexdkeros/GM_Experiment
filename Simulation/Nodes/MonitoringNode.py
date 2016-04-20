'''
@author: ak
'''
import uuid
import scipy as sp
from Simulation.Nodes.GenericNode import GenericNode
from Simulation.Utilities.GeometryFunctions import *
from Simulation.Utilities.Dec import *
from Simulation.Utilities.ArrayOperations import hashable
from Simulation.Utilities.SavitzkyGolayFiltering import *

class MonitoringNode(GenericNode):
    '''
    Geometric Monitoring, stream monitoring Node
    '''

    def __init__(self,
                 network,
                 dataset,
                 threshold,
                 monFunc,
                 nid=uuid.uuid4(), 
                 weight=dec(1),
                 wl=200,
                 wr=0,
                 approximationOrder=3,
                 tolerance=1e-7):
        '''
        Constructor
        args:
            ------node params
            @param nid: unique node id
            @param weight: node's weight
            ------geometric monitoring params
            @param network: networking enviroment
            @param dataset: pandas' Dataframe containing updates
            @param threshold: monitoring threshold
            @param monFunc: monitoring function
            @param tolerance: error tolerance

            ------velocity computation params
            @param windowSize: sliding window size
            @param approximationOrder: order of velocity curve
        '''
        GenericNode.__init__(self, network, dataset, nid=nid, weight=weight,tolerance=tolerance)
        
        self.threshold=threshold
        self.monFunc=monFunc
        
        #get generator from dataset in form (index, Series)
        self.update=dataset.iterrows()
        
        self.v=self.update.next()[1].as_matrix() #initial update
        self.vLast=sp.repeat([0.0],len(self.v))
        self.u=sp.repeat([0.0],len(self.v))
        self.delta=sp.repeat([0.0],len(self.v))
        self.e=sp.repeat([0.0],len(self.v))
        
        #velocity computation params
        self.wl=wl
        self.wr=wr
        self.approximationOrder=approximationOrder
        
        #EXP
        self.uLog=[(self.network.getIterationCount(),hashable(dec(sp.repeat([0.0],len(self.v)))))]
        self.vLog=[self.v]
        self.monFuncVelLog=[]
        self.maxFuncValLog=[]
        
        #convert to decimals
        self.threshold=dec(self.threshold)
        self.v=dec(self.v)
        self.vLast=dec(self.vLast)
        self.u=dec(self.u)
        self.delta=dec(self.delta)
        self.e=dec(self.e)
        
    '''
    ----------------------------------------------------------------------
    messages methods:
    incoming: methodName(self,data,sender) format
    ----------------------------------------------------------------------
    '''
        
    def init(self,dat,sender):
        '''
            "init" signal
            send signal "init" to Coordinator
        '''
        self.vLast=self.v
        self.send(self.network.getCoordId(), "init", (self.vLast,self.weight))
    
    def req(self,dat, sender):
        '''
            "req" signal
            "req" msg received from Coord
        '''
        self.rep()
            
    def adjSlk(self,dat, sender):
        '''
            "adjSlk" signal
            "adjSlk" msg received from  Coord
        '''
        dDelta=dec(dat)
        
        self.delta+=dDelta  #adjusting current slack vector
        
        self.u=self.u+vecquantize((dDelta/self.weight))  #recalculate last drift vector value with new slack vector(needed in case of "req" msg before run is called
        
        #EXP
        self.uLog.append((self.network.getIterationCount(),hashable(self.u)))

        
    def newEst(self,dat,sender):
        '''
            "newEst" signal
            "newEst" msg received from Coord
        '''
        self.e=dec(dat)
        self.vLast=self.v
        self.delta=dec(sp.repeat([0.0],len(self.v)))
        
    def globalViolation(self,dat,sender):
        '''
            "globalViolation" signal
            "globalViolation" msg (not in original Geometric Monitoring method) received from Coord
        '''
        pass
        
        
    '''
    ----------------------------------------------------------------------
    messages methods:
    outgoing: methodName(self) format
              see Node.send() method
    ----------------------------------------------------------------------
    '''
    def rep(self):
        '''
            "rep" signal
            in classic balancing velocity is not used
        '''
        self.send(self.network.getCoordId(), "rep", (hashable(self.v),hashable(self.u),sp.mean(self.monFuncVelLog[self.network.getIterationCount()-2]),sp.mean(self.monFuncAccLog[self.network.getIterationCount()-2])))
        
    
    '''
    ----------------------------------------------------------------------
    other functions
    ----------------------------------------------------------------------
    '''
        
    def getMonFuncVelLog(self):
        '''
            returns monitoring functions velocity log
            @return: velocity array
        '''
        return self.monFuncVelLog
    
    def getMaxFuncValLog(self):
        '''
            returns max function val log
            @return: max func value array
        '''
        return self.maxFuncValLog
    
    def getuLog(self):
        '''
            returns u's throught monitoring process
            @return: array of u vectors
        '''
        return self.uLog
    
    
    def computeMonFuncVel(self,func,dataLog, wl,wr, order):
        '''
            computes monitoring function velocity for heuristic optimization
            args:
                @param func: the monitoring function
                @param dataLog: log of vectors
                @param windowSize: window size
                @param order: approximation order
            @return monitoring function velocity array
        ''' 
        
        data=sp.array(map(func, dataLog))
        
        if wl>len(data):
            wlt=len(data) if len(data)%2==0 else len(data)-1
        else:
            wlt=wl
        if order+2>wlt+wr+1:
            ordert=wlt+wr+1-2
        else:
            ordert=order
        return savitzky_golay(deDec(data) ,wl=wlt,wr=wr,order=ordert,deriv=1) if len(data)>=3 else [(data[-1]-data[0])/len(data)]*len(data) 
    
    def computeMonFuncAcc(self,func,dataLog, wl,wr, order):
        '''
            computes monitoring function acceleration for heuristic optimization
            args:
                @param func: the monitoring function
                @param dataLog: log of vectors
                @param windowSize: window size
                @param order: approximation order
            @return monitoring function acceleration array
        ''' 
        
        data=sp.array(map(func, dataLog))
        
        if wl>len(data):
            wlt=len(data) if len(data)%2==0 else len(data)-1
        else:
            wlt=wl
        if order+2>wlt+wr+1:
            ordert=wlt+wr+1-2
        else:
            ordert=order
        return savitzky_golay(deDec(data) ,wl=wlt,wr=wr,order=2,deriv=2) if len(data)>=4 else [(self.monFuncVelLog[-1]-self.monFuncVelLog[0])/len(self.monFuncVelLog)]*len(self.monFuncVelLog) 
    '''
    ----------------------------------------------------------------------
    monitoring operation
    ----------------------------------------------------------------------
    '''
    def check(self):
        '''
        performs threshold check of drift vector's function value: f(u)
        '''
        
        #DBG
        #print('--Check: Node: %s u:%.10f'%(self.id, self.u))
        
        #bounding sphere
        ball=computeBallFromDiametralPoints(self.e,self.u)
        
        #monochromaticity check
        funcMax=computeExtremesFuncValuesInBall(self.monFunc,(deDec(ball[0]),deDec(ball[1])),type='max',tolerance=self.tolerance)
                    
                    
        #DBG         
        #print(dec(funcMax)-self.threshold)

        if dec(funcMax)>self.threshold:
                
            self.rep()

        
    def run(self):
        '''
        main Monitoring Node function
        receive, process updates
        '''
        
        self.v=dec(self.update.next()[1].as_matrix())
        
        #EXP
        self.vLog.append(self.v)
        
        self.u=self.e+(self.v-self.vLast)+vecquantize((self.delta/self.weight))
        
        #DBG
        #print('--')
        #print('NODE: %s ITER: %d'%(self.id, self.network.getIterationCount()))
        #print('%.10f'%self.u[0])
        #print('%.10f'%self.e[0])
        #print('%.10f'%self.v[0])
        #print('%.10f'%self.vLast[0])
        #print('%.10f'%self.delta[0])

        
        #EXP
        self.uLog.append((self.network.getIterationCount(),hashable(self.u)))
    
        #current velocity computation
        #velocity is max value in ball velocity
        ballr=computeBallFromDiametralPoints(self.e, (self.v-self.vLast))
        self.maxFuncValLog.append(computeExtremesFuncValuesInBall(self.monFunc,(deDec(ballr[0]),deDec(ballr[1])),type='max',tolerance=self.tolerance))
        self.monFuncVelLog=vecquantize(dec(self.computeMonFuncVel(lambda x:x, self.maxFuncValLog, self.wl, self.wr, self.approximationOrder)))
        self.monFuncAccLog=vecquantize(dec(self.computeMonFuncAcc(lambda x:x, self.maxFuncValLog, self.wl, self.wr, self.approximationOrder)))
        #DBG
        #print('iter count:%d'%self.network.getIterationCount())
        #print('node: %s'%str(self.id))
        #print(self.monFuncVelLog)
        #print(len(self.monFuncVelLog))
        #print('--Run: Node: %s u:%s'%(self.id, self.u))
        
