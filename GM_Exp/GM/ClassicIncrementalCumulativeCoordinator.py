'''
@author: ak
'''
import random
from math import log
from GM_Exp import Config
from GM_Exp.GM.Node import Node
from GM_Exp.GM.Coordinator import Coordinator
from types import StringType
from GM_Exp.Utils.Utils import dec,deDec

class ClassicIncrementalCumulativeCoordinator(Coordinator):
    '''
    geometric monitoring, coordinator with cumulate-at-LV-alert-once balancing scheme
    '''


    def __init__(self,  env, nodes, 
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
        Coordinator.__init__(self, env, nodes, nid, threshold, monitoringFunction)

    '''
    ----------------------------------------------------------------------
    messages methods:
    incoming: methodName(self,data,sender) format
    ----------------------------------------------------------------------

    '''
    def rep(self,dat,sender):
        '''
            @override
            "rep" signal for incremental cumulative balancing
            at each Coordinator's request for balancing collect 2x nodes each time
        '''
        self.balancingSet.add((sender,)+dat)
        if log(len(self.balancingSet),2).is_integer() or len(self.balancingSet)==len(self.nodes):   
            self.balance()
    
    '''
    ----------------------------------------------------------------------------------------------------------------
    ********************************************BALANCING FUNCTION*************************************************
    ----------------------------------------------------------------------------------------------------------------

    '''
    def balance(self):
        '''
        @override
        balance method requesting 2x nodes each time for balancing
        '''
        b=sum(u*self.nodes[i] for i,v,u in self.balancingSet)/sum(self.nodes[i] for i,v,u in self.balancingSet)
        
        
        #DBG
        if len(self.balancingSet)==1:
            print("Coord:LOCAL VIOLATION")
        else:
            print("balancing set is:")
            print(self.balancingSet)
        print("Coord: balance vector is: %f, threshold is %f"%(b,self.threshold))
        
        if self.monitoringFunction(b)<self.threshold:
            #----------------------------------------------------------------
            #SUCESSfull balancing
            #----------------------------------------------------------------
            dDelta=[]
            nodeIds=[]
            for (i,v,u) in self.balancingSet:
                dDelta.append(self.nodes[i]*b-self.nodes[i]*u)
                nodeIds.append(i)
            
            #DBG
            print("Coord: balance success")
            print("dDelta:")
            print(dDelta)
            
            #EXP - log balancing vector
            self.send(None, "balancingVector", b)
            
            self.balancingSet.clear()

            self.adjSlk(nodeIds, dDelta)
                    
        else:
            #-----------------------------------------------------------------
            #FAILed balancing
            #-----------------------------------------------------------------
            diffSet=set(self.nodes.keys())-set(i for i,v,u in self.balancingSet)
            
            if len(diffSet): #i.e. len(balancingSet)!=len(nodes)
                
                if len(diffSet)>=len(self.balancingSet):
                    reqNodeId=random.sample(diffSet,len(self.balancingSet))
                else:
                    reqNodeId=random.sample(diffSet,len(diffSet))
                
                self.req(reqNodeId)
            
            else:
                #----------------
                #Global Violation
                #----------------
                vGl=sum(v*self.nodes[i] for i,v,u in self.balancingSet)/sum(self.nodes[i] for i,v,u in self.balancingSet)   #global stats vector
                uGl=sum(u*self.nodes[i] for i,v,u in self.balancingSet)/sum(self.nodes[i] for i,v,u in self.balancingSet)   #global stats vector (via drift vectors *convexity property*)
                
                #EXP - log balancing vector
                self.send(None, "balancingVector", b)
                
                #DBG
                print("Coord: GLOBAL VIOLATION:v=%f,u=%f,f(v)=%f"%(vGl,uGl,self.monitoringFunction(vGl)))
                
                self.e=vGl
                
                self.balancingSet.clear()
                
                #self.newEst()
                
                self.globalViolation()
