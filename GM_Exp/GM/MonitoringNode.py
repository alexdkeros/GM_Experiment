'''
@author: ak
'''
import uuid
from GM_Exp import Config
from GM_Exp.GM.Node import Node

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
        
    '''
    messages methods:
    incoming: methodName(self,data,sender) format
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
        dDelta=dat
        
        self.delta+=dDelta  #adjusting current slack vector
        
        self.u=self.u+(dDelta/self.weight)  #recalculate last drift vector value with new slack vector(needed in case of "req" msg before run is called
        
        
    def newEst(self,dat,sender):
        self.e=dat
        self.vLast=self.v
        self.delta=0
        
    def globalViolation(self,dat,sender):
        pass
        
    '''
    messages methods:
    outgoing: methodName(self) format
    '''
    def rep(self):
        f=getattr(self, self.balancing+"Rep", self.classicRep)
        return f()
    
    def classicRep(self):
        self.send("Coord", "rep", (self.v,self.u))
        
    def heuristicRep(self):
        self.send("Coord", "rep", (self.v,self.u,self.inputStreamInstance.getVelocity()))
    
    '''
    monitoring operation
    '''    
    def check(self):
        #DBG
        print("-checking node %s , u:%f"%(self.id,self.u))
        
        if self.monitoringFunction(self.u)>=self.threshold:
            self.rep()
            
    def run(self):
        
        self.v=self.inputStream.next()
        
        self.u=self.e+(self.v-self.vLast)+(self.delta/self.weight)
        
        #DBG
        print("-running node %s, v=%f, u=%f"%(self.id,self.v,self.u))
        
        
    
    
        
    