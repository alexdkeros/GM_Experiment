'''
@author: ak
'''
import uuid

from GM_Exp import Config
from GM_Exp.GM.Node import Node
from GM_Exp.Utils.Utils import dec, deDec


class MonitoringNode(Node):
    '''
   geometric monitoring, stream monitoring Node
    '''


    def __init__(self, env, inputStream,
                 nid=uuid.uuid4(), 
                 weight=Config.defWeight, 
                 initV=Config.defV,
                 threshold=Config.threshold,
                 monitoringFunction=Config.defMonFunc,
                 balancing=Config.balancing):
        '''
        Constructor
        args:
            ------node params
            @param nid: unique node id
            @param weight: node's weight
            ------geometric monitoring params
            @param env: networking/monitoring enviroment creating Node
            @param inputStream: node's input stream, incoming updates to monitor
            @param initV: initial statistics vector
            @param threshold: monitoring threshold
            @param monitoringFunction: monitoring function
            @param balancing: the balancing scheme
            
        '''
        Node.__init__(self, env, nid=nid, weight=weight)
        
        self.threshold=threshold
        self.monitoringFunction=monitoringFunction
        self.balancing=balancing
        
        self.v=initV
        self.vLast=0
        self.u=0
        self.delta=0
        self.e=0
        
        self.inputStreamInstance=inputStream
        self.inputStream=inputStream.getData()
        
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
        self.send("Coord", "init", (self.vLast,self.weight))
    
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
            "rep" msg to dispach, varies between Balancing methods, dispach to appropriate method
        '''
        if self.balancing in Config.classicBalances:
            f=getattr(self, "classicRep", self.classicRep)
        elif self.balancing in Config.heuristicBalances:
            f=getattr(self, "heuristicRep", self.classicRep)
        else:
            f=self.classicRep
        return f()
    
    #-------------------CLASSIC BALANCING--------------------------------
    def classicRep(self):
        '''
            "rep" signal
            "rep" msg for CLASSIC balancing scheme
                data is (v,u)
        '''
        self.send("Coord", "rep", (self.v,self.u))
    
    
    #-------------------HEURISTIC BALANCING-------------------------------    
    def heuristicRep(self):
        '''
            "rep" signal
            "rep" msg for HEURISTIC balancing scheme
                data is (v,u,velocity)
        '''
        self.send("Coord", "rep", (self.v,self.u,self.inputStreamInstance.getVelocity()))
        
    
    '''
    ----------------------------------------------------------------------
    other functions
    ----------------------------------------------------------------------
    '''
    def getuLog(self):
        '''
            returns u's throught monitoring process
            @return: array of u values
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
        
        #DBG
        print('--Node %s reporting u: %f'%(self.id,self.u))
        
        if self.monitoringFunction(self.u)>=self.threshold:
            self.rep()
            
    def run(self):
        '''
        main Monitoring Node function
        receive, process updates
        '''
        self.v=dec(self.inputStream.next())
        
        #EXP
        self.uLog.append(self.u)
        
        self.u=self.e+(self.v-self.vLast)+(self.delta/self.weight)
        
        #EXP
        self.uLog.append(self.u)
    
    
        
    