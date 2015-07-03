'''
Comparison of Classic,Heuristic, NaiveHeuristic and HeuristicOptimalPair balancing schemes

@author: ak
'''
import os
import pickle
import math
import numpy as np
from itertools import chain
from GM_Exp.Util.Utils import avgListsOverIters
from GM_Exp.Util.Plotter import multiplePlots2d
from GM_Exp.Util.Plotter import barChart
from GM_Exp.GM.Enviroment import Enviroment
from GM_Exp.GM.NaiveEnviroment import NaiveEnviroment
from GM_Exp.GM.NaiveOptimalPairEnviroment import NaiveOptimalPairEnviroment
from GM_Exp.GM.OptimalPairWDataUpdatesEnviroment import OptimalPairWDataUpdatesEnviroment

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
    
    
    
    
    
    
def __runExperimentsOnDataSet(dataSetFile,repeats,threshold, monitoringFunction):
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
    classicRes={}
    for rep in range(repeats):
        print("***------------------------------------rep %d---------------------------------***"%rep)
        env=None
                 
        env=Enviroment(balancing="Classic",
                   threshold=threshold,
                   monitoringFunction=monitoringFunction,
                   dataSetFile=dataSetFile)
        env.runSimulation(None)
        res=env.getExpRes()
        
        
        #collect repeat results
        if not classicRes:
            for metric in res:
                classicRes[metric]=[]

        for metric in res:
            classicRes[metric].append(res[metric])
   
    for metric in classicRes:
        if metric!="driftVectors":
            classicRes[metric]=avgListsOverIters(classicRes[metric])
    
    
    
    #DBG
    print("-------------Heuristic")
    heuristicRes={}
    for rep in range(repeats):
        print("***------------------------------------rep %d---------------------------------***"%rep)
        env=None
        env=Enviroment(balancing="Heuristic",
                   threshold=threshold,
                   monitoringFunction=monitoringFunction,
                   dataSetFile=dataSetFile)
        env.runSimulation(None)
        res=env.getExpRes()
        
        #collect repeat results
        if not heuristicRes:
            for metric in res:
                heuristicRes[metric]=[]

        for metric in res:
            heuristicRes[metric].append(res[metric])
   
    for metric in heuristicRes:
        if metric!="driftVectors":
            heuristicRes[metric]=avgListsOverIters(heuristicRes[metric])
    
    
                
    
    #DBG
    print("-------------HeuristicOptimalPairWDataUps")
    optPairWDataUpsHeuristicRes={}
    for rep in range(repeats):
        print("***------------------------------------rep %d---------------------------------***"%rep)
        env=None
        env=OptimalPairWDataUpdatesEnviroment(balancing="HeuristicOptimalPair",
                   threshold=threshold,
                   monitoringFunction=monitoringFunction,
                   dataSetFile=dataSetFile)
        env.runSimulation(None)
        res=env.getExpRes()
        
        #collect repeat results
        if not optPairWDataUpsHeuristicRes:
            for metric in res:
                optPairWDataUpsHeuristicRes[metric]=[]

        for metric in res:
            optPairWDataUpsHeuristicRes[metric].append(res[metric])
   
    for metric in optPairWDataUpsHeuristicRes:
        if metric!="driftVectors":
            optPairWDataUpsHeuristicRes[metric]=avgListsOverIters(optPairWDataUpsHeuristicRes[metric])
        
        
    
    
    #DBG
    print("-------------NaiveHeuristic")
    naiveHeuristicRes={}
    for rep in range(repeats):
        print("***------------------------------------rep %d---------------------------------***"%rep)
        env=None
        env=NaiveEnviroment(balancing="NaiveHeuristic",
                   threshold=threshold,
                   monitoringFunction=monitoringFunction,
                   dataSetFile=dataSetFile)
        env.runSimulation(None)
        res=env.getExpRes()
        
        #collect repeat results
        if not naiveHeuristicRes:
            for metric in res:
                naiveHeuristicRes[metric]=[]

        for metric in res:
            naiveHeuristicRes[metric].append(res[metric])
   
    for metric in naiveHeuristicRes:
        if metric!="driftVectors":
            naiveHeuristicRes[metric]=avgListsOverIters(naiveHeuristicRes[metric])
            
            
            
            
    
    #DBG
    print("-------------NaiveClassic")
    naiveClassicRes={}
    for rep in range(repeats):
        print("***------------------------------------rep %d---------------------------------***"%rep)
        env=None
        env=NaiveEnviroment(balancing="NaiveClassic",
                   threshold=threshold,
                   monitoringFunction=monitoringFunction,
                   dataSetFile=dataSetFile)
        env.runSimulation(None)
        res=env.getExpRes()
    
        #collect repeat results
        if not naiveClassicRes:
            for metric in res:
                naiveClassicRes[metric]=[]

        for metric in res:
            naiveClassicRes[metric].append(res[metric])
   
    for metric in naiveClassicRes:
        if metric!="driftVectors":
            naiveClassicRes[metric]=avgListsOverIters(naiveClassicRes[metric])
            
            
            
    
    #DBG
    print("-------------NaiveHeuristicOptimalPairWDataUps")
    naiveOptPairWDataUpsHeuristicRes={}
    for rep in range(repeats):
        print("***------------------------------------rep %d---------------------------------***"%rep)
        env=None
        env=NaiveOptimalPairEnviroment(balancing="NaiveOptimalPair",
                   threshold=threshold,
                   monitoringFunction=monitoringFunction,
                   dataSetFile=dataSetFile)
        env.runSimulation(None)
        res=env.getExpRes()
        
        #collect repeat results
        if not naiveOptPairWDataUpsHeuristicRes:
            for metric in res:
                naiveOptPairWDataUpsHeuristicRes[metric]=[]

        for metric in res:
            naiveOptPairWDataUpsHeuristicRes[metric].append(res[metric])
   
    for metric in naiveOptPairWDataUpsHeuristicRes:
        if metric!="driftVectors":
            naiveOptPairWDataUpsHeuristicRes[metric]=avgListsOverIters(naiveOptPairWDataUpsHeuristicRes[metric])
        
        
    

    return {"Classic": classicRes,
            "Heuristic":heuristicRes, 
            "NaiveHeuristic":naiveHeuristicRes, 
            "NaiveClassic":naiveClassicRes,
            "HeuristicOptimalPairWDataUps":optPairWDataUpsHeuristicRes,
            "NaiveOptPairWDataUpsHeuristic":naiveOptPairWDataUpsHeuristicRes}


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
    naiveClassicRes=[datasetRes[key]["NaiveClassic"][plotVal] for key in keys]
    optPairWDataUpsHeuristicRes=[datasetRes[key]["HeuristicOptimalPairWDataUps"][plotVal] for key in keys]
    naiveOptPairWDataUpsHeuristicRes=[datasetRes[key]["NaiveOptPairWDataUpsHeuristic"][plotVal] for key in keys]


    barChart([classicRes,heuristicRes,optPairWDataUpsHeuristicRes,naiveClassicRes,naiveHeuristicRes,naiveOptPairWDataUpsHeuristicRes],
             labels=["Classic","Heuristic","HeuristicOptimalPairWDataUps","NaiveClassic","NaiveHeuristic","NaiveOptPairWDataUpsHeuristic"],
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
    repeats=conf.repeats
    
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
                                              repeats,
                                              threshold, 
                                              monitoringFunctions[i])
                datasetRes[pureName]=res
                
                #plotting dataset specific experiments
                
                #drift vectors plot
                multiplePlots2d([np.array(list(chain.from_iterable(zip(range(int(math.ceil(len(ar)/float(2)))),range(int(math.ceil(len(ar)/float(2)))))))[0:(-1 if len(ar)%2==1 else len(ar))]) for rep in res["Classic"]["driftVectors"] for ar in rep],
                                [ar for rep in res["Classic"]["driftVectors"] for ar in rep],
                                xLabel="iterations",
                                yLabel="drift vector value",
                                title="drift vectors of classic balance for f="+functionNames[i]+" thresh="+str(threshold),
                                saveFlag=conf.saveFlag,
                                filename="./"+pureName+"/"+"classic_drifts_f-"+functionNames[i]+"_thresh-"+str(threshold),
                                showFlag=conf.showFlag)
                
                
                multiplePlots2d([np.array(list(chain.from_iterable(zip(range(int(math.ceil(len(ar)/float(2)))),range(int(math.ceil(len(ar)/float(2)))))))[0:(-1 if len(ar)%2==1 else len(ar))]) for rep in res["Heuristic"]["driftVectors"] for ar in rep],
                                [ar for rep in res["Heuristic"]["driftVectors"] for ar in rep],
                                xLabel="iterations",
                                yLabel="drift vector value",
                                title="drift vectors of heuristic balance for f="+functionNames[i]+" thresh="+str(threshold),
                                saveFlag=conf.saveFlag,
                                filename="./"+pureName+"/"+"heuristic_drifts_f-"+functionNames[i]+"_thresh-"+str(threshold),
                                showFlag=conf.showFlag)
                
                multiplePlots2d([np.array(list(chain.from_iterable(zip(range(int(math.ceil(len(ar)/float(2)))),range(int(math.ceil(len(ar)/float(2)))))))[0:(-1 if len(ar)%2==1 else len(ar))]) for rep in res["NaiveHeuristic"]["driftVectors"] for ar in rep],
                                [ar for rep in res["NaiveHeuristic"]["driftVectors"] for ar in rep],
                                xLabel="iterations",
                                yLabel="drift vector value",
                                title="drift vectors of naive heuristic balance for f="+functionNames[i]+" thresh="+str(threshold),
                                saveFlag=conf.saveFlag,
                                filename="./"+pureName+"/"+"naive_heuristic_drifts_f-"+functionNames[i]+"_thresh-"+str(threshold),
                                showFlag=conf.showFlag)
                
                multiplePlots2d([np.array(list(chain.from_iterable(zip(range(int(math.ceil(len(ar)/float(2)))),range(int(math.ceil(len(ar)/float(2)))))))[0:(-1 if len(ar)%2==1 else len(ar))]) for rep in res["NaiveClassic"]["driftVectors"] for ar in rep],
                                [ar for rep in res["NaiveClassic"]["driftVectors"] for ar in rep],
                                xLabel="iterations",
                                yLabel="drift vector value",
                                title="drift vectors of naive classic balance for f="+functionNames[i]+" thresh="+str(threshold),
                                saveFlag=conf.saveFlag,
                                filename="./"+pureName+"/"+"naive_classic_drifts_f-"+functionNames[i]+"_thresh-"+str(threshold),
                                showFlag=conf.showFlag)
                
                multiplePlots2d([np.array(list(chain.from_iterable(zip(range(int(math.ceil(len(ar)/float(2)))),range(int(math.ceil(len(ar)/float(2)))))))[0:(-1 if len(ar)%2==1 else len(ar))]) for rep in res["HeuristicOptimalPairWDataUps"]["driftVectors"] for ar in rep],
                                [ar for rep in res["HeuristicOptimalPairWDataUps"]["driftVectors"] for ar in rep],
                                xLabel="iterations",
                                yLabel="drift vector value",
                                title="drift vectors of heuristic optimal pair with data updates balance for f="+functionNames[i]+" thresh="+str(threshold),
                                saveFlag=conf.saveFlag,
                                filename="./"+pureName+"/"+"opt_pair_w_data_ups_heuristic_drifts_f-"+functionNames[i]+"_thresh-"+str(threshold),
                                showFlag=conf.showFlag)

                multiplePlots2d([np.array(list(chain.from_iterable(zip(range(int(math.ceil(len(ar)/float(2)))),range(int(math.ceil(len(ar)/float(2)))))))[0:(-1 if len(ar)%2==1 else len(ar))]) for rep in res["NaiveOptPairWDataUpsHeuristic"]["driftVectors"] for ar in rep],
                                [ar for rep in res["NaiveOptPairWDataUpsHeuristic"]["driftVectors"] for ar in rep],
                                xLabel="iterations",
                                yLabel="drift vector value",
                                title="drift vectors of naive optimal pair w data updates heuristic balance for f="+functionNames[i]+" thresh="+str(threshold),
                                saveFlag=conf.saveFlag,
                                filename="./"+pureName+"/"+"naive_opt_pair_heuristic_drifts_f-"+functionNames[i]+"_thresh-"+str(threshold),
                                showFlag=conf.showFlag)
                
                #remaining distance plot
                multiplePlots2d([np.arange(1,len(res["Classic"]["remainingDist"])+1),np.arange(1,len(res["Heuristic"]["remainingDist"])+1),np.arange(1,len(res["HeuristicOptimalPairWDataUps"]["remainingDist"])+1),np.arange(1,len(res["NaiveClassic"]["remainingDist"])+1),np.arange(1,len(res["NaiveHeuristic"]["remainingDist"])+1),np.arange(1,len(res["NaiveOptPairWDataUpsHeuristic"]["remainingDist"])+1)],
                                [res["Classic"]["remainingDist"],res["Heuristic"]["remainingDist"],res["HeuristicOptimalPairWDataUps"]["remainingDist"],res["NaiveClassic"]["remainingDist"],res["NaiveHeuristic"]["remainingDist"],res["NaiveOptPairWDataUpsHeuristic"]["remainingDist"]],
                                labels=["Classic","Heuristic","HeuristicOptimalPairWDataUps","NaiveClassic","NaiveHeuristic","NaiveOptPairWDataUpsHeuristic"],
                                xLabel="local violations",
                                yLabel="distance",
                                title="remaining distance for f="+functionNames[i]+" thresh="+str(threshold),
                                saveFlag=conf.saveFlag,
                                filename="./"+pureName+"/"+"rem_dist_f-"+functionNames[i]+"_thresh-"+str(threshold),
                                showFlag=conf.showFlag)
                
                #lvs per iter plot
                multiplePlots2d([np.arange(len(res["Classic"]["lVsPerIter"])),np.arange(len(res["Heuristic"]["lVsPerIter"])),np.arange(len(res["HeuristicOptimalPairWDataUps"]["lVsPerIter"])),np.arange(len(res["NaiveClassic"]["lVsPerIter"])),np.arange(len(res["NaiveHeuristic"]["lVsPerIter"])),np.arange(len(res["NaiveOptPairWDataUpsHeuristic"]["lVsPerIter"]))],
                                [res["Classic"]["lVsPerIter"],res["Heuristic"]["lVsPerIter"],res["HeuristicOptimalPairWDataUps"]["lVsPerIter"],res["NaiveClassic"]["lVsPerIter"],res["NaiveHeuristic"]["lVsPerIter"],res["NaiveOptPairWDataUpsHeuristic"]["lVsPerIter"]],
                                labels=["Classic","Heuristic","HeuristicOptimalPairWDataUps","NaiveClassic","NaiveHeuristic","NaiveOptPairWDataUpsHeuristic"],
                                xLabel="iterations",
                                yLabel="local violations",
                                title="local violations per iteration for f="+functionNames[i]+" thresh="+str(threshold),
                                saveFlag=conf.saveFlag,
                                filename="./"+pureName+"/"+"lvs_per_iter_f-"+functionNames[i]+"_thresh-"+str(threshold),
                                showFlag=conf.showFlag)
                
                
            
            #plotting experiments
            #datasetRes={"dataset":{"Classic":{},"Heuristic":{},"HeuristicOptimalPairWDataUps":{},"NaiveClassic":{},"NaiveHeuristic":{},"NaiveOptPairWDataUpsHeuristic":{}}}
                
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
    #print(datasetRes)