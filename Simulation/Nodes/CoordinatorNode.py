'''
@author: ak
'''
from Simulation.Nodes.GenericNode import GenericNode
from Simulation.Utilities.GeometryFunctions import *
from Simulation.Utilities.Dec import *

class CoordinatorNode(GenericNode):
    '''
    geometric monitoring, Coordinator node
    
    must setattr() functions selectNodeReq
                             balancer
    '''


    def __init__(self, 
                 network, 
                 nid="Coord",
                 nodes, 
                 threshold, 
                 monFunc,
                 autoBalance=True):
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
            @param autoBalance: True=perform balancing automatically at received req msg
                                False=must implicitly call CoordinatorNode.balance()
        '''
        GenericNode.__init__(self, network, nid=nid, weight=0)
        
        self.threshold=threshold
        self.monFunc=monFunc
        
        self.nodes=dict(zip(nodes,len(nodes)*[0])) #{'id':weight,}
        
        self.balancingSet=set() #set containing tuples (nodeId,v,u,monFuncVel)
        self.pendingReps=0  #keeps track of pending reports produced by Coordinator request
        self.autoBalance=autoBalance
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
    
    def rep(self,dat,sender):
        '''
            "rep" signal
            "rep" msg to dispach, varies between Balancing methods, dispach to appropriate method
        '''
        self.balancingSet.add((sender,)+dat)
        if self.autoBalance or self.pendingReps>0:
            self.pendingReps=max([self.pendingReps-1,0])
            self.balance()
    
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
    ----------------------------------------------------------------------
    other methods:
    ----------------------------------------------------------------------
    '''
    def selectNodeReq(self,balSet,nodeSet):
        '''
        select node to request data for further balancing
        args:
            @param balSet: balancing set (only node ids)
            @param nodeSet: set of all node ids
        @return set of node ids to send requests
        '''
        raise NotImplementedError
    
    def balancer(self,balSet,balVec,threshold,monFunc,nodeWeightDict):
        '''
        computes dDeltas
        args:
            @param balSet: balancing set containing (nodeID,v,u,velocity) tuples
            @param balVec: balancing vector
            @param threshold: monitoring threshold
            @param monFunc: the monitoring function
            @param nodeWeightDict: {nodeID:weight dictionary}
        @return {nodeId: dDelta}
        '''
        raise NotImplementedError
    
    '''
    ----------------------------------------------------------------------------------------------------------------
    ********************************************BALANCING FUNCTION**************************************************
    ----------------------------------------------------------------------------------------------------------------

    '''
    def balance(self):
        
        b=sum(u*self.nodes[i] for i,v,u,vel in self.balancingSet)/sum(self.nodes[i] for i,v,u,vel in self.balancingSet)
        
        #bounding sphere
        ball=computeBallFromDiametralPoints(self.e,b)
        
        #monochromaticity check
        funcMax=computeExtremesFuncValuesInBall(self.monFunc,ball,type='max')
        
        if funcMax>=self.threshold:
            #===================================================================
            # FAILED BALANCING
            #===================================================================
            
            reqNodesId=self.selectNodeReq((i for i[0] in self.balancingSet),set(self.nodes.keys()))
            
            self.pendingReps=len(reqNodesId)
            
            if reqNodesId:
                #===============================================================
                # FAILED BALANCING - request nodes
                #===============================================================
                self.req(reqNodesId)
            else:
                #===============================================================
                # FAILED BALANCING - GLOBAL VIOLATION
                #===============================================================
                
                vGl=sum(v*self.nodes[i] for i,v,u,vel in self.balancingSet)/sum(self.nodes[i] for i,v,u,vel in self.balancingSet)   #global stats vector
                uGl=sum(u*self.nodes[i] for i,v,u,vel in self.balancingSet)/sum(self.nodes[i] for i,v,u,vel in self.balancingSet)   #global stats vector (via drift vectors *convexity property*)
                
                #new Estimate
                self.e=vGl
                
                #self.newEst()
                
                self.balancingSet.clear()
                self.globalViolation()
        else:
            #===================================================================
            # SUCCESSFUL BALANCING
            #===================================================================
            
            dDeltaDict=self.balancer(self.balancingSet,b,self.threshold,self.monFunc,self.nodes)
            
            self.balancingSet.clear()
            
            self.adjSlk(dDeltaDict.keys(), dDeltaDict.values())