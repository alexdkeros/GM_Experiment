'''
Created on Dec 11, 2014

@author: ak
'''
import numpy as np
import pylab as pl
from GM_Exp import Config
from GM_Exp.Utils import Utils
from GM_Exp.Utils import Plotter
from GM_Exp.GM.Enviroment import Enviroment

if __name__ == '__main__':
    
    #-----------------------------------------------------------Env init
    #nodeNum=Config.defNodeNum
    #threshold=Config.threshold
    #monitoringFunction=Config.defMonFunc
    #lambdaVel=Config.lambdaVel
    #mean=Config.defMean
    #std=Config.defStd
    #balancing=Config.balancing
    #----------------------------------------------------------Results
    #{"nodes": int, becomes list
    # "iters": int, becomes list
    # "avgReqsPerLv":int, becomes list
    # "repMsgsPerIter": list, becomes 2dlist
    # "reqMsgsPerIter": list, becomes 2dlist
    # "lVsPerIter": list, becomes 2dlist
    # "reqsPerBal": list, becomes 2dlist
    # "balancingVectors": list, becomes 2dlist
    # "remainingDist": list, becomes 2dlist}

      
    #different experiments
    for t in Config.expTypes:
        print("*-------------------------------------------------------------------------------\n \
*------------------------------experiment %s------------------------------------\n \
*-------------------------------------------------------------------------------"%t)
        Config.config(t) #set experimental ranges
        
        totalResults={}
        
        for bal in Config.balancingTypes:
            
            print("*------------------------------balancing %s------------------------------------*"%bal)
            
            expRangeResults={"avgReqsPerLv":[],"nodes":[],"iters":[],"repMsgsPerIter":[], "reqMsgsPerIter":[], "lVsPerIter":[], "reqsPerBal":[], "balancingVectors":[], "remainingDist":[]}
            
            #iterating over range
            for expVal in pl.arange(Config.expRangeStart,Config.expRangeEnd+1,Config.expRangeStep):
                
                print("*---------------------------------- %s , %f--------------------------------*"%(t,expVal))
                
                repResults={"avgReqsPerLv":[],"nodes":[],"iters":[],"repMsgsPerIter":[], "reqMsgsPerIter":[], "lVsPerIter":[], "reqsPerBal":[], "balancingVectors":[], "remainingDist":[]}

                
                #repeating same range-experiment to avg over
                for rep in range(Config.defRepeats):
                    print("***------------------------------------rep %d---------------------------------***"%rep)
                    env=None
                    
                    if t=="Nodes":
                        env=Enviroment(nodeNum=expVal,balancing=bal)
                    elif t=="Threshold":
                        env=Enviroment(threshold=expVal,balancing=bal)
                    elif t=="Mean":
                        env=Enviroment(mean=expVal,balancing=bal)
                    elif t=="Std":
                        env=Enviroment(std=expVal,balancing=bal)
                    elif t=="Lambda":
                        env=Enviroment(lambdaVel=expVal,balancing=bal)
                    else:
                        print("WRONG EXPERIMENTAL TYPE")
            
                    env.runSimulation()
                    res=env.getExpRes()
                    
                    #collect repeat results
                    for metric in res.keys():
                        repResults[metric].append(res[metric])
                
                print(repResults)
                #collect experimental range results
                for metric in repResults.keys():
                    expRangeResults[metric].append(Utils.avgListsOverIters(repResults[metric]))
                  
            print(expRangeResults)
            #collect total results for balancing scheme
            totalResults[bal]=expRangeResults
        
        print(totalResults)
        
        #print results - heuristic and classic balancing
        
        #--2D PLOTS
        
        #iters plot
        Plotter.plots2d(Config.expRangeStart, Config.expRangeEnd, totalResults["classic"]["iters"], "classic", \
                        Config.expRangeStart,Config.expRangeEnd, totalResults["heuristic"]["iters"], "heuristic",\
                        xLabel=t, yLabel="iterations", title="Iterations in "+t+" Range",\
                        saveFlag=True, filename="ItersIn"+t+"RangeCompare", showFlag=True)
        #lvs plot
        Plotter.plots2d(Config.expRangeStart, Config.expRangeEnd, [sum(l) for l in totalResults["classic"]["lVsPerIter"]], "classic", \
                        Config.expRangeStart,Config.expRangeEnd, [sum(l) for l in totalResults["heuristic"]["lVsPerIter"]], "heuristic",\
                        xLabel=t, yLabel="Local Violations", title="Local Violations in "+t+" Range",\
                        saveFlag=True, filename="LVsIn"+t+"RangeCompare", showFlag=True)
        
        #avgReqsPerLv plot
        Plotter.plots2d(Config.expRangeStart, Config.expRangeEnd, totalResults["classic"]["avgReqsPerLv"], "classic", \
                        Config.expRangeStart,Config.expRangeEnd, totalResults["heuristic"]["avgReqsPerLv"], "heuristic",\
                        xLabel=t, yLabel="Requests", title="Average Requests in "+t+" Range",\
                        saveFlag=True, filename="AvgReqsIn"+t+"RangeCompare", showFlag=True)
        
        #remaining distance plot
        select=int(np.floor(np.average(range(len(totalResults["classic"]["remainingDist"])))))
        data1=totalResults["classic"]["remainingDist"][select]
        print("DATA1")
        print(data1)
        data2=totalResults["heuristic"]["remainingDist"][select]
        print("DATA2")
        print(data2)
        Plotter.plots2d(1,len(data1),data1,"classic",\
                        1,len(data2),data2,"heuristic",\
                        yScale='log',\
                        xLabel="Iterations",yLabel="Distance",title="Remaining Distance in "+t+" Range",\
                        saveFlag=True,filename="RemainingDistance"+t+"Compare",showFlag=True)
        
        #--3D PLOTS
        for bal in Config.balancingTypes:
            
            #remaining distance 3d plot
            Plotter.plot3d(Config.expRangeStart, Config.expRangeEnd, totalResults[bal]["remainingDist"],\
                           xLabel="Iterations", yLabel=t, zLabel="Distance", \
                           zScale='log', \
                           title="Distance remaining per Iteration In "+t+" Range,"+bal, \
                           saveFlag=True, filename=bal+"DistRemPerIterIn"+t+"Range3D", showFlag=True)
            
            #lvs per iter 3d plot
            Plotter.plot3d(Config.expRangeStart, Config.expRangeEnd, totalResults[bal]["lVsPerIter"],\
                           xLabel="Iterations", yLabel=t, zLabel="Local Violations", \
                           title="LocalViolations Per Iterations In "+t+" Range,"+bal, \
                           saveFlag=True, filename=bal+"lVsPerIterIn"+t+"Range3D", showFlag=True)
            
            #lvs per iter 3d plot
            Plotter.plot3d(Config.expRangeStart, Config.expRangeEnd, totalResults[bal]["reqsPerBal"],\
                           xLabel="Balances", yLabel=t, zLabel="Requests", \
                           title="Requests Per Balance In "+t+" Range,"+bal, \
                           saveFlag=True, filename=bal+"ReqsPerBalIn"+t+"Range3D", showFlag=True)
        
        