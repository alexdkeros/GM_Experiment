'''
@author: ak
'''
import time
from GM_Exp import Config
from GM_Exp.GM.OptimalPairWDataUpdatesEnviroment import OptimalPairWDataUpdatesEnviroment

class NaiveOptimalPairEnviroment (OptimalPairWDataUpdatesEnviroment):
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
        
        OptimalPairWDataUpdatesEnviroment.__init__(self,
                                                   balancing=balancing, 
                                                   cumulationFactor=cumulationFactor, 
                                                   nodeNum=nodeNum, 
                                                   threshold=threshold, 
                                                   monitoringFunction=monitoringFunction, 
                                                   lambdaVel=lambdaVel, 
                                                   meanDistr=meanDistr, 
                                                   stdDistr=stdDistr, 
                                                   dataSetFile=dataSetFile, 
                                                   streamNormalizing=streamNormalizing)
                                            
                                            
    
    def runSimulation(self,timeLimit=Config.timeLimit):
        '''
        @override
        main enviroment method simulating geometric monitoring, naive version. Goes with Naive______Coordinator. Call balance() implicitly
            at end of iteration
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
            print("-----------------iteration %d----------------------"%self.iterCounter)
            
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
            
            #imlicitly call balance method
            self.nodes[self.coordId].balance()
            
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
    def newIter(self):
        self.iterCounter+=1
        self.reqMsgsPerIter.append(0)
        self.repMsgsPerIter.append(0)
        if not self.balancingVectors:
            self.balancingVectors.append(0)
        else:
            self.balancingVectors.append(self.balancingVectors[-1])
        
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
            if self.reqMsgsPerBal:
                self.reqMsgsPerBal[-1]+=1 #counting reqsPerBalance by the num of adjSlk msgs sent
            else:
                self.reqMsgsPerBal.append(0)    
        elif msg=="globalViolation":
            if self.reqMsgsPerBal:
                if self.reqMsgsPerBal[-1]==0:
                    self.reqMsgsPerBal[-1]=len(self.nodes)-1 #at last balancing(i.e.GV all nodes take place)
        elif msg=="balancingVector":
            self.balancingVectors[-1]=data
            
            
                    
        
    def processExpRes(self):
        self.lVsPerIter=[i-j for i,j in zip(self.repMsgsPerIter,self.reqMsgsPerIter)]
        self.reqMsgsPerBal=[i for i in self.reqMsgsPerIter if i>0] 
        self.remainingDist=[self.threshold-self.monintoringFunction(b) for b in self.balancingVectors]
        if self.lVsPerIter:
            self.avgReqsPerLv=float(sum(self.reqMsgsPerIter))/float(sum(self.lVsPerIter))
        else:
            self.avgReqsPerLv=0
        for node in self.nodes.values():
            if node.getId()!="Coord":
                self.uLogs.append(node.getuLog())
        self.totalLVs=sum(self.lVsPerIter)
'''        
        
        
#----------------------------------------------------------------------------
#---------------------------------TEST---------------------------------------
#----------------------------------------------------------------------------
            
if __name__=="__main__":
    #running test - OK
    '''
    import sys
    
    env=NaiveEnviroment(balancing="NaiveHeuristic", 
                   nodeNum=2, 
                   threshold=10, 
                   monitoringFunction=lambda x: x,
                    lambdaVel=1,
                    meanDistr=(8,2),
                    stdDistr=(2,0+sys.float_info.min),
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
    
    env=NaiveOptimalPairEnviroment(balancing="NaiveOptimalPair",
                   cumulationFactor=10,
                   threshold=100,
                   monitoringFunction=lambda x:x,
                   dataSetFile='/home/ak/git/GM_Experiment/Experiments/datasets/DATASET_l-0_n-5_m-10_std-10.p')
    env.runSimulation(None)
    print(env.getExpRes())
    res=env.getExpRes()