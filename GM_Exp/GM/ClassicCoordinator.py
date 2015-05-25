'''
@author: ak
'''
import random
from types import StringType

from GM_Exp import Config
from GM_Exp.GM.Coordinator import Coordinator
from GM_Exp.GM.Node import Node
from GM_Exp.Utils.Utils import dec, deDec


class ClassicCoordinator(Coordinator):
    '''
    geometric monitoring, coordinator with classic balancing scheme
    '''


    def __init__(self,  env, nodes, 
                 nid="Coord", 
                 threshold=Config.threshold, 
                 monitoringFunction=Config.defMonFunc,
                 cumulationFactor=None):
        '''
        Constructor
        args:
             ------node params
            @param nid: unique node id - "Coord"
            ------geometric monitoring params
            @param env: networking/monitoring enviroment creating Coordinator
            @param threshold: monitoring threshold
            @param monitoringFunction: monitoring function
            @param cumulationFactor: no role here, formating reasons only
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
            "rep" signal for classic balancing
            at each "rep" msg initiate balancing process
        '''
        self.balancingSet.add((sender,)+dat)    
        self.balance()
    
    '''
    ----------------------------------------------------------------------------------------------------------------
    ********************************************BALANCING FUNCTION*************************************************
    ----------------------------------------------------------------------------------------------------------------

    '''
    def balance(self):
        '''
            @override
            balance method based on original paper
        '''
        b=sum(u*self.nodes[i] for i,v,u in self.balancingSet)/sum(self.nodes[i] for i,v,u in self.balancingSet)
        
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
                reqNodeId=random.sample(diffSet,1)[0]   #request new node data at random
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
      