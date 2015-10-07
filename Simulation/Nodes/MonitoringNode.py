'''
@author: ak
'''
import uuid
import scipy as sp
from Simulation.Nodes.GenericNode import GenericNode
from Simulation.Utilities.GeometryFunctions import *
from Simulation.Utilities.Dec import *
from Simulation.Utilities.ArrayOperations import hashable

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
                 weight=dec(1)):
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
        '''
        GenericNode.__init__(self, network, dataset, nid=nid, weight=weight)
        
        self.threshold=threshold
        self.monFunc=monFunc
        
        #get generator from dataset in form (index, Series)
        self.update=dataset.iterrows()
        
        self.v=self.update.next()[1].as_matrix() #initial update
        self.vLast=0
        self.u=0
        self.delta=0
        self.e=0
        self.monFuncVel=0 #current velocity of f(u)
        
        #EXP
        self.uLog=[0]

        
        #convert to decimals
        self.threshold=dec(self.threshold)
        self.v=dec(self.v)
        self.vLast=dec(self.vLast)
        self.u=dec(self.u)
        self.delta=dec(self.delta)
        self.e=dec(self.e)
        self.uLog=dec(self.uLog)
        
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
        
        self.u=self.u+(dDelta/self.weight)  #recalculate last drift vector value with new slack vector(needed in case of "req" msg before run is called
        
        #EXP
        self.uLog.append(self.u)

        
    def newEst(self,dat,sender):
        '''
            "newEst" signal
            "newEst" msg received from Coord
        '''
        self.e=dec(dat)
        self.vLast=self.v
        self.delta=0
        
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
        self.send(self.network.getCoordId(), "rep", (hashable(self.v),hashable(self.u),self.monFuncVel))
        
    
    '''
    ----------------------------------------------------------------------
    other functions
    ----------------------------------------------------------------------
    '''
    def getuLog(self):
        '''
            returns u's throught monitoring process
            @return: array of u vectors
        '''
        return self.uLog
    
    '''
    ----------------------------------------------------------------------
    monitoring operation
    ----------------------------------------------------------------------
    '''
    def check(self):
        '''
        performs threshold check of drift vector's function value: f(u)
        '''
        #bounding sphere
        ball=computeBallFromDiametralPoints(self.e,self.u)
        
        #monochromaticity check
        funcMax=computeExtremesFuncValuesInBall(self.monFunc,ball,type='max')
        
        if funcMax>=self.threshold:
            self.rep()
            
    def run(self):
        '''
        main Monitoring Node function
        receive, process updates
        '''
        self.v=dec(self.update.next())
        
        #EXP
        #self.uLog.append(self.u)
        
        self.u=self.e+(self.v-self.vLast)+(self.delta/self.weight)
        
        #EXP
        self.uLog.append(self.u)
    
        #current velocity computation
        self.monFuncVel=self.monFunc(self.uLog[-1])-self.monFunc(self.uLog[-2])
        
    