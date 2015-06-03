'''
Comparison of Classic,Heuristic, NaiveHeuristic and HeuristicOptimalPair balancing schemes

@author: ak
'''
import os
import pickle
import math
import numpy as np
from itertools import chain
from GM_Exp.Utils.Plotter import multiplePlots2d
from GM_Exp.Utils.Plotter import barChart
from GM_Exp.GM.Enviroment import Enviroment
from GM_Exp.GM.NaiveEnviroment import NaiveEnviroment
from GM_Exp.GM.OptimalPairEnviroment import OptimalPairEnviroment


import ExperimentConfig as conf


def __viewDataset(dataSetFile,savePath,filename,saveFlag,showFlag):
    '''
    visualizes dataset data
    args:
        @param dataSetFile: dataset filename
        @param savePath: folder to place graphs
        @param filename: filename to save graphs
        @param saveFlag: boolean, to save graph
        @param showFlag: boolean, to show flag
    '''
    print(dataSetFile)
    dataSet=pickle.load(open(dataSetFile,"rb"))
    ranges=[np.arange(dataSet["iterations"])]*dataSet["streams"]
    #velocities
    multiplePlots2d(ranges,
                    dataSet["velocities"],
                    xLabel="iterations",
                    yLabel="velocity",
                    title="velocities of "+filename.replace("_"," "),
                    saveFlag=saveFlag,
                    filename=savePath+"vel_plot_"+filename,
                    showFlag=showFlag)
    
    #updates
    multiplePlots2d(ranges,
                    dataSet["updates"],
                    xLabel="iterations",
                    yLabel="update",
                    title="updates of "+filename.replace("_"," "),
                    saveFlag=saveFlag,
                    filename=savePath+"upd_plot_"+filename,
                    showFlag=showFlag)
    
    #updates detailed
    multiplePlots2d([np.arange(10)]*dataSet["streams"],
                    [d[0:10] for d in dataSet["updates"]],
                    xLabel="iterations",
                    yLabel="update",
                    title="detailed updates of "+filename.replace("_"," "),
                    saveFlag=saveFlag,
                    filename=savePath+"detail_upd_plot_"+filename,
                    showFlag=showFlag)
    
    
    
    
    
    
def __runExperimentsOnDataSet(dataSetFile,threshold, monitoringFunction):
    '''
    runs classic and heuristic tests on dataset
    args:
        @param dataSetFile: dataset file
        @param threshold: monitoring threshold
        @param monitoringFunction: the monitoring function
    @return: results for classic and heuristic tests, dict {"classic":{},"heuristic":{}}
    '''
    #DBG
    print("-------------Classic")
    env=Enviroment(balancing="Classic",
                   threshold=threshold,
                   monitoringFunction=monitoringFunction,
                   dataSetFile=dataSetFile)
    env.runSimulation(None)
    classicRes=env.getExpRes()
    
    #DBG
    print("-------------Heuristic")
    env=Enviroment(balancing="Heuristic",
                   threshold=threshold,
                   monitoringFunction=monitoringFunction,
                   dataSetFile=dataSetFile)
    env.runSimulation(None)
    heuristicRes=env.getExpRes()
    
    #DBG
    print("-------------NaiveHeuristic")
    env=NaiveEnviroment(balancing="NaiveHeuristic",
                   threshold=threshold,
                   monitoringFunction=monitoringFunction,
                   dataSetFile=dataSetFile)
    env.runSimulation(None)
    naiveHeuristicRes=env.getExpRes()
    
    #DBG
    print("-------------HeuristicOptimalPair")
    env=OptimalPairEnviroment(balancing="HeuristicOptimalPair",
                   threshold=threshold,
                   monitoringFunction=monitoringFunction,
                   dataSetFile=dataSetFile)
    env.runSimulation(None)
    optPairHeuristicRes=env.getExpRes()
    
    

    return {"Classic": classicRes, "Heuristic":heuristicRes, "NaiveHeuristic":naiveHeuristicRes, "HeuristicOptimalPair":optPairHeuristicRes}


def __barChartPlots(datasetRes,plotVal,filename,saveFlag,showFlag):
    '''
    barchart plots
    args:
        @param datasetRes: datasetRes={"dataset":{"classic":{},"heuristic":{}}
        @param plotVal: experimental plotting value
        @param filename: filename
        @param saveFlag: boolean
        @param showFlag: boolean
    '''

    keys=sorted(datasetRes.keys())
    classicRes=[datasetRes[key]["Classic"][plotVal] for key in keys]
    heuristicRes=[datasetRes[key]["Heuristic"][plotVal] for key in keys]
    naiveHeuristicRes=[datasetRes[key]["NaiveHeuristic"][plotVal] for key in keys]
    optPairHeuristicRes=[datasetRes[key]["HeuristicOptimalPair"][plotVal] for key in keys]
    barChart([classicRes,heuristicRes,naiveHeuristicRes,optPairHeuristicRes],
             labels=["Classic","Heuristic","NaiveHeuristic","HeuristicOptimalPair"],
             xLabel="datasets",
             yLabel=plotVal,
             title=plotVal,
             xticks=[key.replace("_"," ") for key in keys],
             saveFlag=saveFlag,
             filename=filename,
             showFlag=showFlag
             )
    
    
    
if __name__ == '__main__':
    #params
    thresholds=conf.thresholds
    monitoringFunctions=conf.monitoringFunctions
    functionNames=conf.functionNames
    
    
    #load dataset
    print("---LOADING DATASETS---")
    datasets=os.listdir(conf.dataSetFolder)
    print(datasets)
    
    #plotting datasets
    for dataset in datasets:
        pureName=os.path.splitext(dataset)[0]
        if not os.path.exists(pureName):
            os.makedirs(pureName)    
        
        __viewDataset(conf.dataSetFolder+"/"+dataset,
                      "./"+pureName+"/",
                      pureName,
                      conf.saveFlag,
                      conf.showFlag)
     
        
    #running experiments
    for threshold in thresholds:
        for i in range(len(monitoringFunctions)):
            datasetRes={}
            for dataset in datasets:
                
                pureName=os.path.splitext(dataset)[0]
                if not os.path.exists(pureName):
                    os.makedirs(pureName)    
                    
                #DBG
                print("-------------------------------------------------------"+pureName)
                res=__runExperimentsOnDataSet(conf.dataSetFolder+"/"+dataset,
                                              threshold, 
                                              monitoringFunctions[i])
                datasetRes[pureName]=res
                
                #plotting dataset specific experiments
                
                #drift vectors plot
                multiplePlots2d([np.array(list(chain.from_iterable(zip(range(int(math.ceil(len(ar)/float(2)))),range(int(math.ceil(len(ar)/float(2)))))))[0:(-1 if len(ar)%2==1 else len(ar))]) for ar in res["Classic"]["driftVectors"]],
                                res["Classic"]["driftVectors"],
                                xLabel="iterations",
                                yLabel="drift vector value",
                                title="drift vectors of classic balance for f="+functionNames[i]+" thresh="+str(threshold),
                                saveFlag=conf.saveFlag,
                                filename="./"+pureName+"/"+"classic_drifts_f-"+functionNames[i]+"_thresh-"+str(threshold),
                                showFlag=conf.showFlag)
                
                
                multiplePlots2d([np.array(list(chain.from_iterable(zip(range(int(math.ceil(len(ar)/float(2)))),range(int(math.ceil(len(ar)/float(2)))))))[0:(-1 if len(ar)%2==1 else len(ar))]) for ar in res["Heuristic"]["driftVectors"]],
                                res["Heuristic"]["driftVectors"],
                                xLabel="iterations",
                                yLabel="drift vector value",
                                title="drift vectors of heuristic balance for f="+functionNames[i]+" thresh="+str(threshold),
                                saveFlag=conf.saveFlag,
                                filename="./"+pureName+"/"+"heuristic_drifts_f-"+functionNames[i]+"_thresh-"+str(threshold),
                                showFlag=conf.showFlag)
                
                multiplePlots2d([np.array(list(chain.from_iterable(zip(range(int(math.ceil(len(ar)/float(2)))),range(int(math.ceil(len(ar)/float(2)))))))[0:(-1 if len(ar)%2==1 else len(ar))]) for ar in res["NaiveHeuristic"]["driftVectors"]],
                                res["NaiveHeuristic"]["driftVectors"],
                                xLabel="iterations",
                                yLabel="drift vector value",
                                title="drift vectors of naive heuristic balance for f="+functionNames[i]+" thresh="+str(threshold),
                                saveFlag=conf.saveFlag,
                                filename="./"+pureName+"/"+"naive_heuristic_drifts_f-"+functionNames[i]+"_thresh-"+str(threshold),
                                showFlag=conf.showFlag)
                
                multiplePlots2d([np.array(list(chain.from_iterable(zip(range(int(math.ceil(len(ar)/float(2)))),range(int(math.ceil(len(ar)/float(2)))))))[0:(-1 if len(ar)%2==1 else len(ar))]) for ar in res["HeuristicOptimalPair"]["driftVectors"]],
                                res["HeuristicOptimalPair"]["driftVectors"],
                                xLabel="iterations",
                                yLabel="drift vector value",
                                title="drift vectors of heuristic optimal pair balance for f="+functionNames[i]+" thresh="+str(threshold),
                                saveFlag=conf.saveFlag,
                                filename="./"+pureName+"/"+"opt_pair_heuristic_drifts_f-"+functionNames[i]+"_thresh-"+str(threshold),
                                showFlag=conf.showFlag)
                
                #remaining distance plot
                multiplePlots2d([np.arange(1,res["Classic"]["totalLVs"]+1),np.arange(1,res["Heuristic"]["totalLVs"]+1),np.arange(1,len(res["NaiveHeuristic"]["remainingDist"])+1),np.arange(1,res["HeuristicOptimalPair"]["totalLVs"]+1)],
                                [res["Classic"]["remainingDist"],res["Heuristic"]["remainingDist"],res["NaiveHeuristic"]["remainingDist"],res["HeuristicOptimalPair"]["remainingDist"]],
                                labels=["Classic","Heuristic","NaiveHeuristic","HeuristicOptimalPair"],
                                xLabel="local violations",
                                yLabel="distance",
                                title="remaining distance for f="+functionNames[i]+" thresh="+str(threshold),
                                saveFlag=conf.saveFlag,
                                filename="./"+pureName+"/"+"rem_dist_f-"+functionNames[i]+"_thresh-"+str(threshold),
                                showFlag=conf.showFlag)
                
                #lvs per iter plot
                multiplePlots2d([np.arange(res["Classic"]["iters"]),np.arange(res["Heuristic"]["iters"]),np.arange(res["NaiveHeuristic"]["iters"]),np.arange(res["HeuristicOptimalPair"]["iters"])],
                                [res["Classic"]["lVsPerIter"],res["Heuristic"]["lVsPerIter"],res["NaiveHeuristic"]["lVsPerIter"],res["HeuristicOptimalPair"]["lVsPerIter"]],
                                labels=["Classic","Heuristic","NaiveHeuristic","HeuristicOptimalPair"],
                                xLabel="iterations",
                                yLabel="local violations",
                                title="local violations per iteration for f="+functionNames[i]+" thresh="+str(threshold),
                                saveFlag=conf.saveFlag,
                                filename="./"+pureName+"/"+"lvs_per_iter_f-"+functionNames[i]+"_thresh-"+str(threshold),
                                showFlag=conf.showFlag)
                
                
            
            #plotting experiments
            #datasetRes={"dataset":{"Classic":{},"Heuristic":{},"NaiveHeuristic":{},"HeuristicOptimalPair":{}}}
                
            if not os.path.exists(functionNames[i]):
                os.makedirs(functionNames[i]) 
            
            
            #total messages bar chart
            __barChartPlots(datasetRes,
                            "totalMsgs",
                            "./"+functionNames[i]+"/totalMsgs_thresh-"+str(threshold),
                            conf.saveFlag,
                            conf.showFlag)
            
            #total LVs bar chart
            __barChartPlots(datasetRes,
                            "totalLVs",
                            "./"+functionNames[i]+"/totalLVs_thresh-"+str(threshold),
                            conf.saveFlag,
                            conf.showFlag)
            
            #avgReqsPerLV bar chart
            __barChartPlots(datasetRes,
                            "avgReqsPerLv",
                            "./"+functionNames[i]+"/avgReqsPerLv_thresh-"+str(threshold),
                            conf.saveFlag,
                            conf.showFlag)
            
            #iters bar chart
            __barChartPlots(datasetRes,
                            "iters",
                            "./"+functionNames[i]+"/iters_thresh-"+str(threshold),
                            conf.saveFlag,
                            conf.showFlag)
            