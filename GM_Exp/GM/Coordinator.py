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



class Coordinator(Node):
    '''
    geometric monitoring, Coordinator node
    '''


    def __init__(self, env, nodes, 
                 nid="Coord", 
                 threshold=Config.threshold, 
                 monitoringFunction=Config.defMonFunc, 
                 balancing=Config.balancing, 
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
            @param balancing: the balancing scheme
            @param cumulationFactor: parameter of cumulative Balancing methods (non-classic), number of requests
                                     for (first/all) balancing
        '''
        Node.__init__(self, env, nid=nid, weight=0)
        
        self.threshold=threshold
        self.monitoringFunction=monitoringFunction
        self.balancing=balancing
        self.cumulationFactor=cumulationFactor

        self.nodes=nodes    #dictionary {"id":weight,}
        self.balancingSet=set() #set containing tuples (nodeId,v,u) if classicBalance, (nodeId,v,u,vel) if heuristicBalance
        self.sumW=sum(nodes.values())
        
        self.e=0
        
        
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
            w=dat[1]
            v=dat[0]
            self.e+=(w*v)/self.sumW
            if len(self.balancingSet)==len(self.nodes):
                self.balancingSet.clear()
                self.newEst()
    
    def rep(self,dat, sender):
        '''
            "rep" signal
            "rep" msg to dispach, varies between Balancing methods, dispach to appropriate method
        '''
        f=getattr(self, self.balancing+"Rep", self.classicRep)
        return f(dat, sender)
    
    
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
        f=getattr(self, self.balancing+"Balance", self.classicBalance)
        return f()
    
    
    '''
    -----------------------------------------CLASSIC balance-------------------------------------------------------
    '''
    
    def classicRep(self,dat,sender):
        '''
            "rep" signal for classic balancing
            at each "rep" msg initiate balancing process
        '''
        self.balancingSet.add((sender,)+dat)    
        self.balance()
    
    
    
    def classicBalance(self):
        '''
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
                
                #DBG
                print("Coord: GLOBAL VIOLATION:v=%f,u=%f,f(v)=%f"%(vGl,uGl,self.monitoringFunction(vGl)))
                
                self.e=vGl
                
                self.balancingSet.clear()
                
                #self.newEst()
                
                self.globalViolation()
                
                
    
    '''
    -----------------------------------------HEURISTIC balance-------------------------------------------------------
    '''
                
    def heuristicRep(self,dat,sender):
        '''
            "rep" signal for heuristic balancing
            at each "rep" msg initiate balancing process
        '''
        self.balancingSet.add((sender,)+dat)    
        self.balance()
        
        
    def heuristicBalance(self):
        '''
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
            
            results=heuristicNLP(list((str(nid),vel) for nid,v,u,vel in self.balancingSet),self.threshold,b,self.monitoringFunction)
            
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
            
            if len(diffSet): #i.e. len(balancingSet)!=len(nodes)
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
                
    
    
    '''
    -----------------------------------------ONCE CUMULATIVE balance------------------------------------------------
    '''
    
    def onceCumulativeRep(self,dat,sender):
        '''
            "rep" signal for once cumulative balancing
            an Coordinator's node request for balancing collect self.cumulativeFactor nodes the first time of each LV
                resolution, then one at a time
        '''
        self.balancingSet.add((sender,)+dat)  
        if not (1<len(self.balancingSet)<self.cumulationFactor+1) or len(self.balancingSet)==len(self.nodes):
            self.balance()
    
    
    
    def onceCumulativeBalance(self):
        '''
        balance method requesting self.cumulationFactor random nodes for the first balance of a LV
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
                
                if len(self.balancingSet)==1 and len(diffSet)>=self.cumulationFactor:   #first time in balacing method, just received LV msg
                    reqNodeId=random.sample(diffSet,self.cumulationFactor)
                else:
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
    -----------------------------------------STATIC CUMULATIVE balance----------------------------------------------
    '''
    
    
    def staticCumulativeRep(self,dat,sender):
        '''
            "rep" signal for static cumulative balancing
            at each Coordinator's request for balancing collect self.cumulativeFactor nodes at once
        '''
        self.balancingSet.add((sender,)+dat)    
        if len(self.balancingSet)%self.cumulationFactor==1 or len(self.balancingSet)==len(self.nodes):
            self.balance()
    
    
    
    def staticCumulativeBalance(self):
        '''
        balance method requesting self.cumulationFactor random nodes at each request
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
                if len(diffSet)>=self.cumulationFactor:
                    reqNodeId=random.sample(diffSet,self.cumulationFactor)
                else:
                    reqNodeId=random.sample(diffSet,len(diffSet))
            
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
    -----------------------------------------INCREMENTAL CUMULATIVE balance-----------------------------------------
    '''
    
    def incrementalCumulativeRep(self,dat,sender):
        '''
            "rep" signal for incremental cumulative balancing
            at each Coordinator's request for balancing collect 2x nodes each time
        '''
        self.balancingSet.add((sender,)+dat)
        
        #DBG
        print('------COORDBAL:adding node %s to bal set, length: %d'%(str(sender),len(self.balancingSet)))
        
        if log(len(self.balancingSet),2).is_integer() or len(self.balancingSet)==len(self.nodes):   
            
            #DBG
            print('------COORDBAL:balancing...bal set length:%d'%len(self.balancingSet))
            
            self.balance()
    
    
    
    def incrementalCumulativeBalance(self):
        '''
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
                
                
                #DBG
                print('------COORDBAL:requesting %d nodes'%(len(reqNodeId) if isinstance(reqNodeId,list) else 1))
                
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


#----------------------------------------------------------------------------
#---------------------------------TEST---------------------------------------
#----------------------------------------------------------------------------
         
#see Enviroment module