'''
@author: ak
'''
from Simulation.Nodes.GenericNode import GenericNode
from Simulation.Utilities.Dec import *

class CoordinatorNode(GenericNode):
    '''
    geometric monitoring, Coordinator node
    '''


    def __init__(self, 
                 network, 
                 nid="Coord",
                 nodes, 
                 threshold, 
                 monFunc):
        '''
        Constructor
        args:
             ------node params
            @param network: networking enviroment
            @param nid: unique node id - "Coord"
            ------geometric monitoring params
            @param nodes: node id list
            @param threshold: monitoring threshold
            @param monFunc: monitoring function
        '''
        GenericNode.__init__(self, network, nid=nid, weight=0)
        
        self.threshold=threshold
        self.monFunc=monFunc
        
        self.nodes=dict(zip(nodes,len(nodes)*[0])) #{'id':weight,}
        
        self.balancingSet=set() #set containing tuples (nodeId,v,u,monFuncVel)
        self.sumW=0
        
        self.e=0
        
        #converting to decimals
        self.threshold=dec(self.threshold)
        self.sumW=dec(self.sumW)
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
            "init" msg sent by all nodes for monitoring initialization
        '''
        if sender in self.nodes:
            self.balancingSet.add(sender)
            v=dec(dat[0])
            w=dec(dat[1])
            self.nodes[sender]=w    #append node weight to dictionary
            self.e+=(w*v)   #compute estimate vector nominator
            if len(self.balancingSet)==len(self.nodes):
                self.sumW=sum(self.nodes.values())  #compute estimate vector denominator, i.e. sum of weights
                self.e=self.e/self.sumW #compute estimate vector
                
                self.balancingSet.clear()
                self.newEst()   #dispach estimate vector
    
    def rep(self,dat, sender):
        '''
            "rep" signal
            "rep" msg to dispach, varies between Balancing methods, dispach to appropriate method
        '''
        raise NotImplementedError
    
    
    '''
    ----------------------------------------------------------------------
    messages methods:
    outgoing: methodName(self) format
    ----------------------------------------------------------------------
    '''
    def newEst(self):
        '''
            "newEst" signal
            "newEst" mgs sent to nodes at monitoring initialization/global Violation occurence
        '''
        self.send(self.nodes.keys(),"newEst",self.e)
        
    def req(self,nodeId):
        '''
            "req" signal
            "req" msg sent to nodeId to request data for balancing
        '''
        self.send(nodeId,"req",None)
        
    def adjSlk(self,nodeId,dat):
        '''
            "adjSlk" signal
            "adjSlk" msg sent at balance success
        '''
        self.send(nodeId,"adjSlk",dat)
        
    def globalViolation(self):
        '''
            "globalViolation" signal
            "globalViolation" msg (not in original Geometric Monitoring method) sent at global violation occurence
        '''
        self.send(self.nodes.keys(),"globalViolation",None)
        
        
        
    '''
    ----------------------------------------------------------------------------------------------------------------
    ********************************************BALANCING FUNCTIONS*************************************************
    ----------------------------------------------------------------------------------------------------------------

    '''
    def balance(self):
        '''
        balancing handler
        dispaches to selected balancing scheme method
        '''
        raise NotImplementedError
    
                
