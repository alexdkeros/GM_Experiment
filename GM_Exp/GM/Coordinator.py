'''
@author: ak
'''
import uuid
import random
from GM_Exp import Config
from GM_Exp.GM.Node import Node
from GM_Exp.Heuristics import NonLinearProgramming
from GM_Exp.Heuristics.NonLinearProgramming import heuristicNLP
from types import StringType



class Coordinator(Node):
    '''
    classdocs
    '''


    def __init__(self,env,nodes, nid="Coord",threshold=Config.threshold,monitoringFunction=Config.defMonFunc,balancing=Config.balancing ):
        '''
        Constructor
        '''
        Node.__init__(self, env, nid=nid, weight=0, threshold=threshold, monitoringFunction=monitoringFunction,balancing=balancing)
        self.nodes=nodes    #dictionary {"id":weight,}
        self.balancingSet=set() #set containing tuples (nodeId,v,u) if classicBalance, (nodeId,v,u,vel) if heuristicBalance
        self.sumW=sum(nodes.values())
        
        #DBG - OK
        #print("Coord: node dict")
        #print(self.nodes)
        
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
        self.balancingSet.add((sender,)+dat)    
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
        
    '''
    ---classic balance
    '''
    def balance(self):
        f=getattr(self, self.balancing+"Balance", self.classicBalance)
        return f()
    
    def classicBalance(self):
        '''
        balance method based on original paper
        '''
        b=sum(u*self.nodes[i] for i,v,u in self.balancingSet)/sum(self.nodes[i] for i,v,u in self.balancingSet)
        
        
        #DBG
        if not self.balancingSet:
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
            
            if len(diffSet): #i.e. len(balancingSet)==len(nodes)
                reqNodeId=random.sample(diffSet,1)[0]   #request new node data at random
                self.req(reqNodeId)
            
            else:
                #----------------
                #Global Violation
                #----------------
                vGl=sum(v*self.nodes[i] for i,v,u in self.balancingSet)/sum(self.nodes[i] for i,v,u in self.balancingSet)   #global stats vector
                uGl=sum(u*self.nodes[i] for i,v,u in self.balancingSet)/sum(self.nodes[i] for i,v,u in self.balancingSet)   #global stats vector (via drift vectors *convexity property*)
                
                #DBG
                print("Coord: GLOBAL VIOLATION:v=%f,u=%f,f(v)=%f"%(vGl,uGl,self.monitoringFunction(vGl)))
                
                self.e=vGl
                
                self.balancingSet.clear()
                
                #self.newEst()
                
                self.globalViolation()
                
                
                
    '''
    ---heuristic balance
    '''  
    def heuristicBalance(self):
        '''
        heuristic based balancing method
        '''
        b=sum(u*self.nodes[i] for i,v,u,vel in self.balancingSet)/sum(self.nodes[i] for i,v,u,vel in self.balancingSet)
                
        #DBG
        if not self.balancingSet:
            print("Coord:LOCAL VIOLATION")
        else:
            print("balancing set is:")
            print(self.balancingSet)
        print("Coord: balance vector is: %f, threshold is %f"%(b,self.threshold))
        
        if self.monitoringFunction(b)<self.threshold:
            #----------------------------------------------------------------
            #SUCESSfull balancing
            #----------------------------------------------------------------
            
            bSetDict={str(id):u for id,v,u,vel in self.balancingSet}
            
            results=heuristicNLP(list((str(id),vel) for id,v,u,vel in self.balancingSet),self.threshold,b,self.monitoringFunction)
            
            dDelta=[]
            nodeIds=[]
            for i in results.keys():
                nodeIds.append(uuid.UUID(i))
                dDelta.append(self.nodes[uuid.UUID(i)]*results[i]-self.nodes[uuid.UUID(i)]*bSetDict[i])
                
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
            
            if len(diffSet): #i.e. len(balancingSet)==len(nodes)
                reqNodeId=random.sample(diffSet,1)[0]   #request new node data at random
                self.req(reqNodeId)
            
            else:
                #----------------
                #Global Violation
                #----------------
                vGl=sum(v*self.nodes[i] for i,v,u,vel in self.balancingSet)/sum(self.nodes[i] for i,v,u,vel in self.balancingSet)   #global stats vector
                uGl=sum(u*self.nodes[i] for i,v,u,vel in self.balancingSet)/sum(self.nodes[i] for i,v,u,vel in self.balancingSet)   #global stats vector (via drift vectors *convexity property*)
                
                #DBG
                print("Coord: GLOBAL VIOLATION:v=%f,u=%f,f(v)=%f"%(vGl,uGl,self.monitoringFunction(vGl)))
                
                self.e=vGl
                
                self.balancingSet.clear()
                
                #self.newEst()
                
                self.globalViolation()
        
