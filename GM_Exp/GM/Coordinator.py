'''
@author: ak
'''
import random
from GM_Exp import Config
from GM_Exp.GM.Node import Node


class Coordinator(Node):
    '''
    classdocs
    '''


    def __init__(self,env,nodes, id="Coord",threshold=Config.threshold,monitoringFunction=Config.defMonFunc ):
        '''
        Constructor
        '''
        Node.__init__(self, env, id=id, weight=0, threshold=threshold, monitoringFunction=monitoringFunction)
        self.nodes=nodes    #dictionary {"id":weight,}
        self.balancingSet=set()
        self.sumW=sum(nodes.values())
        
    '''
    messages methods:
    incoming: methodName(self,data,sender) format
    '''
    def init(self,dat,sender):
        if sender:
            self.balancingSet.add(sender)
            w=dat[1]
            v=dat[0]
            self.e+=(w*v)/self.sumW
            if len(self.balancingSet)==len(self.nodes):
                self.balancingSet.clear()
                self.newEst()
    
    def rep(self,dat, sender):
        self.balancingSet.add((sender,)+dat)    #set containing tuples (nodeId,v,u)
        self.balance()
    
    '''
    messages methods:
    outgoing: methodName(self) format
    '''
    def newEst(self):
        self.send(self.nodes.keys(),"newEst",self.e)
        
    def req(self,nodeId):
        self.send(nodeId,"req",None)
        
    def adjSlk(self,nodeId,dat):   
        self.send(nodeId,"adjSlk",dat)
        
    def globalViolation(self):
        self.send(self.nodes.keys(),"globalViolation",None)
        
    '''
    other functions
    '''
    def balance(self):
        b=sum(u*self.nodes[i] for i,v,u in self.balancingSet)/sum(self.nodes[i] for i,v,u in self.balancingSet)
        
        
        if self.monitoringFunction(b)<self.threshold:
            #----------------------------------------------------------------
            #SUCESSfull balancing
            #----------------------------------------------------------------
            dDelta=list((self.nodes[i]*b-self.nodes[i]*u) for i,v,u in self.balancingSet)
            nodeIds=list(i for i,v,u in self.balancingSet)
            
            self.balancingSet.clear()

            self.adjSlk(nodeIds, dDelta)
                    
        else:
            #-----------------------------------------------------------------
            #FAILed balancing
            #-----------------------------------------------------------------
            diffSet=set(self.nodes.keys())-set(i for i,v,u in self.balancingSet)
            
            if len(diffSet): #i.e. len(balancingSet)==len(nodes)
                reqNodeId=random.sample(diffSet,1)[0]   #request new node data at random
                self.req(reqNodeId)
            
            else:
                #----------------
                #Global Violation
                #----------------
                vGl=sum(v*self.nodes[i] for i,v,u in self.balancingSet)/sum(self.nodes[i] for i,v,u in self.balancingSet)   #global stats vector
                uGl=sum(u*self.nodes[i] for i,v,u in self.balancingSet)/sum(self.nodes[i] for i,v,u in self.balancingSet)   #global stats vector (via drift vectors *convexity property*)
                
                self.e=vGl
                
                self.balancingSet.clear()
                
                #self.newEst()
                
                self.globalViolation()
                
    
         
        
        
        
