'''
@author: ak
'''
import time
import sys
import pkgutil
import uuid
from GM_Exp import Config
from GM_Exp.DataStream.InputStreamFactory import InputStreamFactory 
from GM_Exp.GM.MonitoringNode import MonitoringNode
from GM_Exp.GM.HeuristicOptimalPairCoordinator import HeuristicOptimalPairCoordinator
from GM_Exp.Heuristics.NonLinearProgramming import heuristicNLP
from GM_Exp.Config import dataSetFile, lambdaVel, streamNormalizing
from GM_Exp.Util.OptimalPairer import WeightedOptimalPairerWDataUpdates


class OptimalPairWDataUpdatesEnviroment:
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
        self.dataSetFlag=False
        if dataSetFile:
            self.dataSetFlag=True
        
        

        #--------------------------------------------------------------------------------------------------------------------
        # experimental results
        #--------------------------------------------------------------------------------------------------------------------
        self.iterCounter=0
        self.avgReqsPerLv=0
        self.totalMsgs=0
        self.totalLVs=0
        self.reqMsgsPerIter=[]
        self.repMsgsPerIter=[]
        self.reqMsgsPerBal=[]
        self.lVsPerIter=[]
        self.balancingVectors=[]
        self.remainingDist=[]
        self.uLogs=[]
        
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
        # building optimal pairing dictionary
        #--------------------------------------------------------------------------------------------------------------------
        self.optimalPairer=WeightedOptimalPairerWDataUpdates(threshold=self.threshold)
        
        #DBG
        #print("OPTIMAL PAIRER: DISTRIBUTIONS")
        #print({nId:self.nodes[nId].getVelocityDistr() for nId in self.nodes.keys()})
        
        if dataSetFile:
            self.optimalPairer.optimize(nodes={nId:self.nodes[nId].getDataUpdatesLog()[0:1000] for nId in self.nodes.keys()}, threshold=threshold,func= self.monintoringFunction)
            for i in self.optimalPairer.getTypeDict().keys():
                print(i)
                print(self.optimalPairer.getTypeDict()[i])
        
        #--------------------------------------------------------------------------------------------------------------------
        # creating optimal pairing coordinator
        #--------------------------------------------------------------------------------------------------------------------
        mod = __import__("GM_Exp.GM."+self.balancing+"Coordinator", fromlist=[self.balancing+"Coordinator"])
        coordObj= getattr(mod, self.balancing+"Coordinator")        
        
        #DBG
        #print(coordObj)
        
        coordinator=coordObj(env=self, 
                             nodes=coordDict,
                             threshold=threshold, 
                             monitoringFunction=monitoringFunction, 
                             cumulationFactor=self.cumulationFactor,
                             optimalPairer=self.optimalPairer)
        self.nodes[coordinator.getId()]=coordinator
        self.coordId=coordinator.getId()
        
        
                
                
    def getCoordId(self):
        '''
        @return: coordinator id
        '''
        return self.coordId
            
            
    def signal(self,data): 
        '''
        simulate signal transaction
        @param (sender id, target id, msg, data)
        '''
        #EXP-sniff msg
        self.newMsg(data[2],data[3])
        
        #DBG
        #print("signal received")
        #print("Sender: %s, Target: %s , msg: %s , data: %s"%(data[0],data[1],data[2],str(data[3])))
        
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
                #print("-------node running:%s"%node.getId())
                
                node.run()
                
            #optimization running for every iteration, if dataset not present
            if not self.dataSetFlag:
                self.optimalPairer.optimize({nId:self.nodes[nId].getDataUpdatesLog() for nId in self.nodes.keys() if nId!=self.coordId}, self.threshold,self.monintoringFunction)
                #DBG
                #print(self.optimalPairer.getDistrDict())
                #print(self.optimalPairer.getTypeDict())
                
            for node in self.nodes.values():
                #DBG
                #print("-------node checking:%s"%node.getId())
                
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
            self.totalMsgs+=1
            
            self.reqMsgsPerIter[-1]+=1
            
            if self.reqMsgsPerBal and self.reqMsgsPerBal[-1]==0:
                pass
            else:
                self.reqMsgsPerBal.append(0)
                
        elif msg=="rep":
            self.totalMsgs+=1
            
            self.repMsgsPerIter[-1]+=1
        elif msg=="adjSlk":
            self.totalMsgs+=1
            
            self.reqMsgsPerBal[-1]+=1 #counting reqsPerBalance by the num of adjSlk msgs sent
        elif msg=="globalViolation":
            if self.reqMsgsPerBal[-1]==0:
                self.reqMsgsPerBal[-1]=len(self.nodes)-1 #at last balancing(i.e.GV all nodes take place)
        elif msg=="balancingVector":
            self.balancingVectors.append(data)
        #DBG
        #print("REQ Message count per iter:")
        #print(self.reqMsgsPerIter)
                
        
    def processExpRes(self):
        self.lVsPerIter=[i-j for i,j in zip(self.repMsgsPerIter,self.reqMsgsPerIter)]
        self.reqMsgsPerBal=[i-1 for i in self.reqMsgsPerBal] # the num of adjSlk msgs contain violating node, so remove it for correct computation of req msgs per balance
        self.remainingDist=[self.threshold-self.monintoringFunction(b) for b in self.balancingVectors]
        if self.lVsPerIter:
            self.avgReqsPerLv=float(sum(self.reqMsgsPerIter))/float(sum(self.lVsPerIter))
        else:
            self.avgReqsPerLv=0
        for node in self.nodes.values():
            if node.getId()!="Coord":
                self.uLogs.append(node.getuLog())
        self.totalLVs=sum(self.lVsPerIter)
        
    def getExpRes(self):
        return {"driftVectors":self.uLogs,  #list of nodes lists
                "avgReqsPerLv":self.avgReqsPerLv,   #float
                "nodes":len(self.nodes)-1,    #int
                "iters":self.iterCounter,   #int
                "repMsgsPerIter":self.repMsgsPerIter,   #list of iters length 
                "reqMsgsPerIter":self.reqMsgsPerIter,   #list of iters length
                "lVsPerIter":self.lVsPerIter,   #list of iters length 
                "reqsPerBal":self.reqMsgsPerBal,    #list 
                "balancingVectors":self.balancingVectors,   #list of total LVs -1 length
                "remainingDist":self.remainingDist, #list of total LVs -1 length
                "totalMsgs":self.totalMsgs, #int
                "totalLVs":self.totalLVs}   #int
#----------------------------------------------------------------------------
#---------------------------------TEST---------------------------------------
#----------------------------------------------------------------------------
            
if __name__=="__main__":
    #running test - OK
    '''
    import sys
    
    env=OptimalPairEnviroment(balancing="HeuristicOptimalPair", 
                   nodeNum=6, 
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
    
    import decimal
    decimal.getcontext().prec=Config.prec
    decimal.getcontext().rounding=Config.rounding
    
    env=OptimalPairWDataUpdatesEnviroment(balancing='HeuristicOptimalPair',
                   threshold=100,
                   monitoringFunction=lambda x:x,
                   dataSetFile='/home/ak/workspace/GM_Experiment/Experiments/datasets/DATASET_l-1_n-5_m-5_std-5.p')
    env.runSimulation(None)
    print(env.getExpRes())
    '''
Created on Jun 11, 2015

@author: ak
'''
