'''
@author: ak
'''
import time
from GM_Exp.GM.Enviroment import Enviroment
from GM_Exp import Config

class NaiveEnviroment(Enviroment):
    '''
    classdocs
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
        
        Enviroment.__init__(self,
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
        
        
        
#----------------------------------------------------------------------------
#---------------------------------TEST---------------------------------------
#----------------------------------------------------------------------------
            
if __name__=="__main__":
    #running test - OK
    
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
    