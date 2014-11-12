'''
@author: ak
'''
import time
import uuid
from GM_Exp import Config
from GM_Exp.DataStream.InputStreamFactory import InputStreamFactory 
from GM_Exp.GM.MonitoringNode import MonitoringNode
from GM_Exp.GM.Coordinator import Coordinator

class Enviroment():
    '''
    classdocs
    '''


    def __init__(self, nodeNum=Config.defNodeNum, threshold=Config.threshold, monitoringFunction=Config.defMonFunc, lambdaVel=Config.lambdaVel, mean=Config.defMean, std=Config.defStd):
        '''
        Constructor
        '''
        #create a dictionary {"coord": coord instance, "node id #1":node instance, ...}
        self.inputStreamFactory=InputStreamFactory(lambdaVel=lambdaVel, mean=mean, std=std)
        self.inputStreamFetcher=self.inputStreamFactory.getInputStream()
        
        self.nodes={}
        coordDict={}
        
        self.globalViolationFlag=False

        #creating nodes
        for i in range(nodeNum):
            node=MonitoringNode(env=self, nid=uuid.uuid4(),inputStream=self.inputStreamFetcher.next().getData(),threshold=threshold, monitoringFunction=monitoringFunction)
            self.nodes[node.getId()]=node
            coordDict[node.getId()]=node.getWeight()
            
            #DBG - OK
            #print("Creating node %d:"%i)
            #print(node)
            #print(self.nodes)
        

        #creating coordinator
        coordinator=Coordinator(env=self, nodes=coordDict,threshold=threshold, monitoringFunction=monitoringFunction)
        self.nodes[coordinator.getId()]=coordinator
            
        #DBG - OK
        #print("Nodes:")
        #print(self.nodes)
        
        #experimental results
        self.iterCounter=0
        self.reqMsgsPerIter=[]
        self.repMsgsPerIter=[]
        self.reqMsgsPerBal=[]
        self.lVsPerIter=[]
        
            
            
    def signal(self,data): 
        '''
        data format: (sender id, target id, msg, data)
        '''
        #DBG
        print("SIGNAL:")
        print(data)
        
        #EXP-sniff msg
        self.newMsg(data[2])
        
        self.nodes[data[1]].rcv(data)
        
        if data[2]=="globalViolation":
            self.globalViolationFlag=True
        
        
        
    def runSimulation(self,timeLimit=Config.timeLimit):
        #initialize nodes
        for nodeId in self.nodes.keys():
            self.signal((None, nodeId, "init", None))
            
        startTime=time.time()
        elapsedT=0
        
        #EXP-initialize experimental results
        self.resetExpRes()
        
        
        #run simulation
        while elapsedT<timeLimit and self.globalViolationFlag==False:
            
            #EXP
            self.newIter()
            
            
            #DBG
            print("-----------------iteration %d----------------------"%self.iterCounter)
            
            for node in self.nodes.values():
                #DBG
                print("-------node running:%s"%node.getId())
                
                node.run()
                
                if self.globalViolationFlag==True:
                    break
            
            elapsedT=time.time()-startTime
            
        
        #DBG    
        if elapsedT>=timeLimit:
            print("TIMEOUT")
        if self.globalViolationFlag:
            print("GLOBAL VIOLATION")
            
        #EXP - process experimental results
        self.processExpRes()
            
    
    '''
    Experimental Results methods
    '''
    def resetExpRes(self):
        self.iterCounter=0
        self.reqMsgsPerIter=[]
        self.repMsgsPerIter=[]
        self.reqMsgsPerBal=[]
        self.lVsPerIter=[]
        
    
    def newIter(self):
        self.iterCounter+=1
        self.reqMsgsPerIter.append(0)
        self.repMsgsPerIter.append(0)
        
        
    def newMsg(self,msg):
        if msg=="req":
            self.reqMsgsPerIter[-1]+=1
            
            if self.reqMsgsPerBal and self.reqMsgsPerBal[-1]==0:
                pass
            else:
                self.reqMsgsPerBal.append(0)
                
        elif msg=="rep":
            self.repMsgsPerIter[-1]+=1
        elif msg=="adjSlk":
            self.reqMsgsPerBal[-1]+=1 #counting reqsPerBalance by the num of adjSlk msgs sent
        elif msg=="globalViolation":
            if self.reqMsgsPerBal[-1]==0:
                self.reqMsgsPerBal[-1]=len(self.nodes)-1 #at last balancing(i.e.GV all nodes take place)

                
        
    def processExpRes(self):
        self.lVsPerIter=[i-j for i,j in zip(self.repMsgsPerIter,self.reqMsgsPerIter)]
        self.reqMsgsPerBal=[i-1 for i in self.reqMsgsPerBal] # the num of adjSlk msgs contain violating node, so remove it for correct computation of req msgs per balance
    
    def getExpRes(self):
        return {"iters":self.iterCounter,"repMsgsPerIter":self.repMsgsPerIter, "reqMsgsPerIter":self.reqMsgsPerIter, "lVsPerIter":self.lVsPerIter, "reqsPerBal":self.reqMsgsPerBal}

#----------------------------------------------------------------------------
#---------------------------------TEST---------------------------------------
#----------------------------------------------------------------------------
            
if __name__=="__main__":
    env=Enviroment()
    env.runSimulation()
    res=env.getExpRes()
    print(res)
    print("must equal iters:")
    print(len(res["repMsgsPerIter"]))
    print(len(res["reqMsgsPerIter"]))
    print(len(res["lVsPerIter"]))
    print("total lVs:%d (from msgs are:%d)"%(sum(res["lVsPerIter"]),sum(res["repMsgsPerIter"])-sum(res["reqMsgsPerIter"])))