'''
@author: ak
'''
import uuid
from GM_Exp import Config
from GM_Exp.GM.Node import Node

class MonitoringNode(Node):
    '''
    classdocs
    '''


    def __init__(self, env, inputStream,nid=uuid.uuid4(), weight=Config.defWeight, initV=Config.defV,threshold=Config.threshold,monitoringFunction=Config.defMonFunc,balancing=Config.balancing):
        '''
        Constructor
        '''
        Node.__init__(self, env, nid=nid, weight=weight, threshold=threshold, monitoringFunction=monitoringFunction,balancing=balancing)
        self.inputStreamInstance=inputStream
        self.inputStream=inputStream.getData()
        self.v=initV
        self.vLast=0
        self.u=0
        self.delta=0
        
        
    '''
    messages methods:
    incoming: methodName(self,data,sender) format
    '''
        
    def init(self,dat,sender):
        '''
            "init" method
            send signal "init" to Coordinator
        '''
        self.vLast=self.v
        self.send("Coord", "init", (self.vLast,self.weight))
    
    def req(self,dat, sender):
        self.rep()
            
    def adjSlk(self,dat, sender):
        dDelta=dat
        
        #DBG - OK
        #print("prev d:%f"%self.delta)
        
        self.delta+=dDelta  #adjusting current slack vector
        
        #DBG - OK
        #print("adj d:%f"%self.delta)     
        
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
        if self.monitoringFunction(self.u)>=self.threshold:
            self.rep()
            
    def run(self):
        #DBG - OK
        #print("before:")
        #self.check()
        
        self.v=self.inputStream.next()
        
        self.u=self.e+(self.v-self.vLast)+(self.delta/self.weight)
        
        #DBG
        #print("node %s, v=%f, u=%f"%(self.id,self.v,self.u))
        
        #DBG - OK
        #print("after:")
        #self.check()
        
    
    
        
    