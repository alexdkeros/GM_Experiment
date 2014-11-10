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
            
        #DBG
        print("Nodes:")
        print(self.nodes)
            
            
    def signal(self,data): 
        '''
        data format: (sender id, target id, msg, data)
        '''
        #DBG
        print("SIGNAL:")
        print(data)
        
        self.nodes[data[1]].rcv(data)
        if data[2]=="globalViolation":
            self.globalViolationFlag=True
        
        
    def runSimulation(self,timeLimit=Config.timeLimit):
        #initialize nodes
        for nodeId in self.nodes.keys():
            self.signal((None, nodeId, "init", None))
            
        iteration=0
        startTime=time.time()
        elapsedT=0
        
        #run simulation
        while elapsedT<timeLimit and self.globalViolationFlag==False:
            
            iteration+=1
            
            #DBG
            print("-----------------iteration %d----------------------"%iteration)
            
            for node in self.nodes.values():
                #DBG
                print("-------node running:%s"%node.getId())
                
                node.run()
                
                if self.globalViolationFlag==True:
                    break
            
            elapsedT=time.time()-startTime
            
        if elapsedT>=timeLimit:
            print("TIMEOUT")
        if self.globalViolationFlag:
            print("GLOBAL VIOLATION")
            

#----------------------------------------------------------------------------
#---------------------------------TEST---------------------------------------
#----------------------------------------------------------------------------
            
if __name__=="__main__":
    env=Enviroment()
    env.runSimulation()

        