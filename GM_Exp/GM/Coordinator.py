'''
@author: ak
'''
import uuid
import random
from math import log
from GM_Exp import Config
from GM_Exp.GM.Node import Node
from types import StringType
from GM_Exp.Heuristics.NonLinearProgramming import heuristicNLP
from GM_Exp.Util.Utils import dec,deDec



class Coordinator(Node):
    '''
    geometric monitoring, Coordinator node
    '''


    def __init__(self, env, nodes, 
                 nid="Coord", 
                 threshold=Config.threshold, 
                 monitoringFunction=Config.defMonFunc):
        '''
        Constructor
        args:
             ------node params
            @param nid: unique node id - "Coord"
            ------geometric monitoring params
            @param env: networking/monitoring enviroment creating Coordinator
            @param threshold: monitoring threshold
            @param monitoringFunction: monitoring function
        '''
        Node.__init__(self, env, nid=nid, weight=0)
        
        self.threshold=threshold
        self.monitoringFunction=monitoringFunction
        
        self.nodes=nodes    #dictionary {"id":weight,}
        self.balancingSet=set() #set containing tuples (nodeId,v,u) if classicBalance, (nodeId,v,u,vel) if heuristicBalance
        self.sumW=sum(nodes.values())
        
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
        if sender:
            self.balancingSet.add(sender)
            w=dec(dat[1])
            v=dec(dat[0])
            self.e+=(w*v)/self.sumW
            if len(self.balancingSet)==len(self.nodes):
                self.balancingSet.clear()
                self.newEst()
    
    def rep(self,dat, sender):
        '''
            "rep" signal
            "rep" msg to dispach, varies between Balancing methods, dispach to appropriate method
        '''
        pass
    
    
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
        pass
    
                
                
                      
#----------------------------------------------------------------------------
#---------------------------------TEST---------------------------------------
#----------------------------------------------------------------------------
         
#see Enviroment module