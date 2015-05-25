'''
@author: ak
'''
import uuid
import random
from types import StringType

from GM_Exp import Config
from GM_Exp.GM.Node import Node
from GM_Exp.GM.Coordinator import Coordinator
from GM_Exp.Utils.Utils import dec,deDec
from GM_Exp.Heuristics.NonLinearProgramming import heuristicNLP


class HeuristicStaticCumulativeCoordinator(Coordinator):
    '''
    geometric monitoring, coordinator with heuristic balancing scheme
    '''


    def __init__(self,  env, nodes, 
                 nid="Coord", 
                 threshold=Config.threshold, 
                 monitoringFunction=Config.defMonFunc,
                 cumulationFactor=Config.defCumulationFactor):

        '''
        Constructor
        args:
             ------node params
            @param nid: unique node id - "Coord"
            ------geometric monitoring params
            @param env: networking/monitoring enviroment creating Coordinator
            @param threshold: monitoring threshold
            @param monitoringFunction: monitoring function
            @param cumulationFactor: parameter of cumulative Balancing methods (non-classic), number of requests
                                     for (first/all) balancing

            '''
        Coordinator.__init__(self, env, nodes, nid, threshold, monitoringFunction)
        self.cumulationFactor=cumulationFactor

    '''
    ----------------------------------------------------------------------
    messages methods:
    incoming: methodName(self,data,sender) format
    ----------------------------------------------------------------------

    '''
    def rep(self,dat,sender):
        '''
             @override
            "rep" signal for static cumulative balancing
            at each Coordinator's request for balancing collect self.cumulativeFactor nodes at once
        '''
        self.balancingSet.add((sender,)+dat)    
        if len(self.balancingSet)%self.cumulationFactor==1 or len(self.balancingSet)==len(self.nodes) or self.cumulationFactor==1:
            self.balance()
   
    '''
    ----------------------------------------------------------------------------------------------------------------
    ********************************************BALANCING FUNCTION*************************************************
    ----------------------------------------------------------------------------------------------------------------

    '''
    def balance(self):
        '''
        @override
        balance method requesting self.cumulationFactor random nodes at each request
        '''
        b=sum(u*self.nodes[i] for i,v,u,vel in self.balancingSet)/sum(self.nodes[i] for i,v,u,vel in self.balancingSet)
        
        
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
            
            bSetDict={str(nid):u for nid,v,u,vel in self.balancingSet}
            
            results=heuristicNLP(list((str(nid),deDec(vel)) for nid,v,u,vel in self.balancingSet),deDec(self.threshold),deDec(b),self.monitoringFunction)
            
            dDelta=[]
            nodeIds=[]
            for i in results.keys():
                nodeIds.append(uuid.UUID(i))
                dDelta.append(self.nodes[uuid.UUID(i)]*dec(results[i])-self.nodes[uuid.UUID(i)]*bSetDict[i])
            
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
            diffSet=set(self.nodes.keys())-set(i for i,v,u,vel in self.balancingSet)
            
            if len(diffSet): #i.e. len(balancingSet)!=len(nodes)
                if len(diffSet)>=self.cumulationFactor:
                    reqNodeId=random.sample(diffSet,self.cumulationFactor)
                else:
                    reqNodeId=random.sample(diffSet,len(diffSet))
            
                self.req(reqNodeId)
            
            else:
                #----------------
                #Global Violation
                #----------------
                vGl=sum(v*self.nodes[i] for i,v,u,vel in self.balancingSet)/sum(self.nodes[i] for i,v,u,vel in self.balancingSet)   #global stats vector
                uGl=sum(u*self.nodes[i] for i,v,u,vel in self.balancingSet)/sum(self.nodes[i] for i,v,u,vel in self.balancingSet)   #global stats vector (via drift vectors *convexity property*)
                
                #EXP - log balancing vector
                self.send(None, "balancingVector", b)
                
                #DBG
                print("Coord: GLOBAL VIOLATION:v=%f,u=%f,f(v)=%f"%(vGl,uGl,self.monitoringFunction(vGl)))
                
                self.e=vGl
                
                self.balancingSet.clear()
                
                #self.newEst()
                
                self.globalViolation()
      