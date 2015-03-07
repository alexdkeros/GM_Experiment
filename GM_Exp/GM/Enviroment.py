'''
@author: ak
'''
import time
import uuid
from GM_Exp import Config
from GM_Exp.DataStream.InputStreamFactory import InputStreamFactory 
from GM_Exp.GM.MonitoringNode import MonitoringNode
from GM_Exp.GM.Coordinator import Coordinator
from GM_Exp.Heuristics.NonLinearProgramming import heuristicNLP
from GM_Exp.Config import dataSetFile

class Enviroment:
    '''
    simulation enviroment, responsible for running/coordinanting the simulation
    '''


    def __init__(self, 
                 balancing=Config.balancing, 
                 cumulationFactor=Config.defCumulationFactor, 
                 nodeNum=Config.defNodeNum, 
                 threshold=Config.threshold, 
                 monitoringFunction=Config.defMonFunc, 
                 lambdaVel=Config.lambdaVel, 
                 meanDistr=Config.defMeanN, 
                 stdDistr=Config.defStdN, 
                 dataSetFile=Config.dataSetFile, 
                 streamNormalizing=Config.streamNormalizing):
        '''
        Constructor
        ---geometric monitoring parameters
        @param nodeNum: number of monitoring nodes
        @param threshold: monitoring threshold
        @param monitoringFunction: arbitrary monitoring function 
        
        ---balancing parameters, see GM_Exp.GM.Coordinator
        @param balancing: selected balancing method, choices: classic, heuristic, onceCumulative, staticCumulative, incrementalCumulative
        @param cumulationFactor: if *Cumulative balance selected, must specify cumulation factor
        
        ---stream parameters, see GM_Exp.DataStream.InputStreamFactory
        @param lambdaVel: velocity changing factor lambdaVel*u+(1-lambdaVel)u', where u: old velocity, u':new velocity, lambdaVel:[0,1]
        @param meanDistr: distribution of inputStreams velocities' means, tuple (mean,std) 
        @param stdDistr: distribution of inputStreams velocities' stds, tuple (mean, std)
        @param dataSetFile: filename containing synthetic dataset to load
        @param streamNormalizing: boolean, normalize streams velocities to specified mean
        '''
        
        self.balancing=balancing
        self.cumulationFactor=cumulationFactor
        self.monintoringFunction=monitoringFunction
        self.threshold=threshold
        self.streamNormalizing=streamNormalizing
        self.globalViolationFlag=False
        

        #--------------------------------------------------------------------------------------------------------------------
        # experimental results
        #--------------------------------------------------------------------------------------------------------------------
        self.iterCounter=0
        self.avgReqsPerLv=0
        self.reqMsgsPerIter=[]
        self.repMsgsPerIter=[]
        self.reqMsgsPerBal=[]
        self.lVsPerIter=[]
        self.balancingVectors=[]
        self.remainingDist=[]
        
        
        #--------------------------------------------------------------------------------------------------------------------
        # creating Inputstreams
        #--------------------------------------------------------------------------------------------------------------------
        self.inputStreamFactory=InputStreamFactory(lambdaVel=lambdaVel, velMeanNormalDistr=meanDistr, velStdNormalDistr=stdDistr, dataSetFile=dataSetFile)
        self.inputStreamFetcher=self.inputStreamFactory.getInputStream()
        
        self.nodes={}
        coordDict={}
        
        #--------------------------------------------------------------------------------------------------------------------
        # creating Nodes (from scratch or from loaded dataset)
        #--------------------------------------------------------------------------------------------------------------------
        for i in range(nodeNum if not dataSetFile else self.inputStreamFactory.getInputStreamPopulation()):
            node = MonitoringNode(env=self, nid=uuid.uuid4(), inputStream=self.inputStreamFetcher.next(), threshold=threshold, monitoringFunction=monitoringFunction, balancing=balancing)
            self.nodes[node.getId()]=node
            coordDict[node.getId()]=node.getWeight()
        
        #--------------------------------------------------------------------------------------------------------------------
        # creating coordinator
        #--------------------------------------------------------------------------------------------------------------------
        coordinator=Coordinator(env=self, nodes=coordDict,threshold=threshold, monitoringFunction=monitoringFunction,balancing=balancing, cumulationFactor=cumulationFactor)
        self.nodes[coordinator.getId()]=coordinator
        
            
            
    def signal(self,data): 
        '''
        simulate signal transaction
        @param (sender id, target id, msg, data)
        '''
        #EXP-sniff msg
        self.newMsg(data[2],data[3])
        
        if data[1]:
            self.nodes[data[1]].rcv(data)
        
        if data[2]=="globalViolation":
            self.globalViolationFlag=True
        
        
        
    def runSimulation(self,timeLimit=Config.timeLimit):
        '''
        main enviroment method simulating geometric monitoring
        @param timeLimit: time limited simulation
        '''   
        #----------------------------------------------------------------------------
        # initializing simulation
        #----------------------------------------------------------------------------
        
        #initialize timer 
        startTime=time.time()
        elapsedT=0
        
        #EXP-initialize experimental results
        self.resetExpRes()
        
        
        #----------------------------------------------------------------------------
        # running simulation
        #----------------------------------------------------------------------------
        
        #initialize nodes
        for nodeId in self.nodes.keys():
            self.signal((None, nodeId, "init", None))
        
        #simulation
        while (elapsedT<timeLimit if timeLimit else True) and self.globalViolationFlag==False:
            
            #----------------------------------------------------------------------------
            # new iteration
            #----------------------------------------------------------------------------
            
            #EXP
            self.newIter()
            
            #DBG
            #print("-----------------iteration %d----------------------"%self.iterCounter)
            
            #normalizing velocities before new stream update
            if self.streamNormalizing:
                self.inputStreamFactory.normalizeVelocities()
            
            for node in self.nodes.values():
                #DBG
                print("-------node running:%s"%node.getId())
                
                node.run()
            
            for node in self.nodes.values():
                #DBG
                print("-------node checking:%s"%node.getId())
                
                node.check()
                
                if self.globalViolationFlag==True:
                    break
            
            elapsedT=time.time()-startTime
            
        
        #DBG
        if (elapsedT>=timeLimit if timeLimit else False):
            print("TIMEOUT")
        if self.globalViolationFlag:
            print("GLOBAL VIOLATION")
         
        #----------------------------------------------------------------------------
        # finalizing simulation, collecting results
        #----------------------------------------------------------------------------
           
        #EXP - process experimental results
        self.processExpRes()
            
    
    '''
    Experimental Results methods
    '''
    def resetExpRes(self):
        self.iterCounter=0
        self.avgReqsPerLv=0
        self.reqMsgsPerIter=[]
        self.repMsgsPerIter=[]
        self.reqMsgsPerBal=[]
        self.lVsPerIter=[]
        self.balancingVectors=[]
        self.remainingDist=[]
    
    def newIter(self):
        self.iterCounter+=1
        self.reqMsgsPerIter.append(0)
        self.repMsgsPerIter.append(0)
        
        
    def newMsg(self,msg,data):
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
        elif msg=="balancingVector":
            self.balancingVectors.append(data)
                
        
    def processExpRes(self):
        self.lVsPerIter=[i-j for i,j in zip(self.repMsgsPerIter,self.reqMsgsPerIter)]
        self.reqMsgsPerBal=[i-1 for i in self.reqMsgsPerBal] # the num of adjSlk msgs contain violating node, so remove it for correct computation of req msgs per balance
        self.remainingDist=[self.threshold-self.monintoringFunction(b) for b in self.balancingVectors]
        if not self.lVsPerIter:
            self.avgReqsPerLv=float(sum(self.reqMsgsPerIter))/float(sum(self.lVsPerIter))
        else:
            self.avgReqsPerLv=0
            
    def getExpRes(self):
        return {"avgReqsPerLv":self.avgReqsPerLv,"nodes":len(self.nodes),"iters":self.iterCounter,"repMsgsPerIter":self.repMsgsPerIter, "reqMsgsPerIter":self.reqMsgsPerIter, "lVsPerIter":self.lVsPerIter, "reqsPerBal":self.reqMsgsPerBal, "balancingVectors":self.balancingVectors, "remainingDist":self.remainingDist}

#----------------------------------------------------------------------------
#---------------------------------TEST---------------------------------------
#----------------------------------------------------------------------------
            
if __name__=="__main__":
    #running test and heuristic test - OK
    '''
    import sys
    
    env=Enviroment(balancing="heuristic", 
                   nodeNum=2, 
                   threshold=10, 
                   monitoringFunction=lambda x: x,
                    lambdaVel=1,
                    meanDistr=(2,2),
                    stdDistr=(0,0+sys.float_info.min),
                    streamNormalizing=True)
    env.runSimulation()
    res=env.getExpRes()
    print(res)
    print("must equal iters:")
    print(len(res["repMsgsPerIter"]))
    print(len(res["reqMsgsPerIter"]))
    print(len(res["lVsPerIter"]))
    print("total lVs:%d (from msgs are:%d)"%(sum(res["lVsPerIter"]),sum(res["repMsgsPerIter"])-sum(res["reqMsgsPerIter"])))
    '''
    #dataset import test - OK
    
    env=Enviroment(balancing='heuristic',
                   threshold=100,
                   monitoringFunction=lambda x:x**2,
                   dataSetFile='/home/ak/git/GM_Experiment/GM_Exp/DataStream/datasetTest.p')
    env.runSimulation(None)
    print(env.getExpRes())
    