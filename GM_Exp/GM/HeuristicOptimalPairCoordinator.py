'''
@author: ak
'''
import random
from types import StringType
import uuid

from GM_Exp import Config
from GM_Exp.GM.Coordinator import Coordinator
from GM_Exp.GM.Node import Node
from GM_Exp.Heuristics.NonLinearProgramming import heuristicNLP
from GM_Exp.Util.Utils import dec, deDec
from GM_Exp.Util.OptimalPairer import OptimalPairerWDataUpdates,OptimalPairerWDistr


class HeuristicOptimalPairCoordinator(Coordinator):
    '''
    geometric monitoring, coordinator with heuristic balancing scheme
    '''


    def __init__(self,  env, nodes, 
                 nid="Coord", 
                 threshold=Config.threshold, 
                 monitoringFunction=Config.defMonFunc,
                 cumulationFactor=None,
                 optimalPairer=None):
        '''
        Constructor
        args:
             ------node params
            @param nid: unique node id - "Coord"
            ------geometric monitoring params
            @param env: networking/monitoring enviroment creating Coordinator
            @param threshold: monitoring thresholdtypeDictionary=typeDict
            @param monitoringFunction: monitoring function
            @param cumulationFactor: no role here, formating reasons only
            @param optimalPairer: optimal pairs generator, per type
            '''
        Coordinator.__init__(self, env, nodes, nid, threshold, monitoringFunction)
        
        self.optimalPairer=optimalPairer
        self.remainingReps=0 #set it to the number of expected reports during balancing
    '''
    ----------------------------------------------------------------------
    messages methods:
    incoming: methodName(self,data,sender) format
    ----------------------------------------------------------------------

    '''
    def rep(self,dat,sender):
        '''
            @override
            "rep" signal for heuristic balancing
            at each "rep" msg initiate balancing process
        '''
        self.balancingSet.add((sender,)+dat) 
        self.remainingReps-=1
        if self.remainingReps<=0:   
            self.balance()
    
    '''
    ----------------------------------------------------------------------------------------------------------------
    ********************************************BALANCING FUNCTION*************************************************
    ----------------------------------------------------------------------------------------------------------------

    '''
    def balance(self):
        '''
            @override
            heuristic based balancing method
        '''
        b=sum(u*self.nodes[i] for i,v,u,vel in self.balancingSet)/sum(self.nodes[i] for i,v,u,vel in self.balancingSet)
                
        #DBG
        if len(self.balancingSet)==1:
            print("Coord:LOCAL VIOLATION")
        else:
            print("balancing set is:")
            print(self.balancingSet)
        
        print("Coord: balance vector is: %f,f(b)= %f, threshold is %f"%(b,self.monitoringFunction(b),self.threshold))
        
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
                reqNodeId=self.optimalPairer.getOptPairing(set(i for i,v,u,vel in self.balancingSet))
                if reqNodeId:
                    #request matching pair
                    #DBG
                    print("Coord: requesting MATCHING PAIR")
                    print(reqNodeId)
            
                    self.remainingReps=len(reqNodeId)
                    self.req(list(reqNodeId))
                else:
                    #request node at random
                    reqNodeId=random.sample(diffSet,1)[0]   #request new node data at random
                    
                    #DBG
                    print("Coord: requesting RANDOM NODE")
                    print(reqNodeId)
                    
                    self.remainingReps=1
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