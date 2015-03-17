'''
Comparison of Classic and Heuristic balancing schemes

@author: ak
'''
import os
import pickle
import numpy as np
from GM_Exp.Utils.Plotter import multiplePlots2d
from GM_Exp.Utils.Plotter import barChart
from GM_Exp.GM.Enviroment import Enviroment
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
    env=Enviroment(balancing="classic",
                   threshold=threshold,
                   monitoringFunction=monitoringFunction,
                   dataSetFile=dataSetFile)
    env.runSimulation(None)
    classicRes=env.getExpRes()
    
    env=Enviroment(balancing="heuristic",
                   threshold=threshold,
                   monitoringFunction=monitoringFunction,
                   dataSetFile=dataSetFile)
    env.runSimulation(None)
    heuristicRes=env.getExpRes()

    return {"classic": classicRes, "heuristic":heuristicRes}


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
    keys=datasetRes.keys()
    classicRes=[datasetRes[key]["classic"][plotVal] for key in keys]
    heuristicRes=[datasetRes[key]["heuristic"][plotVal] for key in keys]
    barChart([classicRes,heuristicRes],
             labels=["classic","heuristic"],
             xLabel="datasets",
             yLabel="messages",
             title=plotVal,
             xticks=keys,
             saveFlag=saveFlag,
             filename=filename,
             showFlag=showFlag
             )
    
    
    
if __name__ == '__main__':
    #params
    thresholds=[100]
    monitoringFunctions=[lambda x:x, lambda x:x**2]
    functionNames=["x", "x2"]
    
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
        
                res=__runExperimentsOnDataSet(conf.dataSetFolder+"/"+dataset,
                                              threshold, 
                                              monitoringFunctions[i])
                datasetRes[pureName]=res
                
                
                
                
                
                
                
                #plotting dataset specific experiments
                
                #drift vectors plot
                multiplePlots2d([np.arange(res["classic"]["iters"])]*res["classic"]["nodes"],
                                res["classic"]["driftVectors"],
                                xLabel="iterations",
                                yLabel="drift vector value",
                                title="drift vectors of classic balance for f="+functionNames[i]+" thresh="+threshold,
                                saveFlag=conf.saveFlag,
                                filename="./"+pureName+"/"+"classic_drifts_f-"+functionNames[i]+"_thresh-"+threshold,
                                showFlag=conf.showFlag)
                
                multiplePlots2d([np.arange(res["heuristic"]["iters"])]*res["heuristic"]["nodes"],
                                res["heuristic"]["driftVectors"],
                                xLabel="iterations",
                                yLabel="drift vector value",
                                title="drift vectors of heuristic balance for f="+functionNames[i]+" thresh="+threshold,
                                saveFlag=conf.saveFlag,
                                filename="./"+pureName+"/"+"heuristic_drifts_f-"+functionNames[i]+"_thresh-"+threshold,
                                showFlag=conf.showFlag)
                
                #remaining distance plot
                multiplePlots2d([np.arange(res["classic"]["iters"]),np.arange(res["heuristic"]["iters"])],
                                [res["classic"]["remainingDist"],res["heuristic"]["remainingDist"]],
                                labels=["classic","heuristic"],
                                xLabel="iterations",
                                yLable="distance",
                                title="remaining distance for f="+functionNames[i]+" thresh="+threshold,
                                saveFlag=conf.saveFlag,
                                filename="./"+pureName+"/"+"rem_dist_f-"+functionNames[i]+"_thresh-"+threshold,
                                showFlag=conf.showFlag)
                
                #lvs per iter plot
                multiplePlots2d([np.arange(res["classic"]["iters"]),np.arange(res["heuristic"]["iters"])],
                                [res["classic"]["lVsPerIter"],res["heuristic"]["lVsPerIter"]],
                                labels=["classic","heuristic"],
                                xLabel="iterations",
                                yLable="local violations",
                                title="local violations per iteration for f="+functionNames[i]+" thresh="+threshold,
                                saveFlag=conf.saveFlag,
                                filename="./"+pureName+"/"+"lvs_per_iter_f-"+functionNames[i]+"_thresh-"+threshold,
                                showFlag=conf.showFlag)
                
                
            
        #plotting experiments
        #datasetRes={"dataset":{"classic":{},"heuristic":{}}
            
        if not os.path.exists(functionNames[i]):
            os.makedirs(functionNames[i]) 
        
        #total messages bar chart
        __barChartPlots(datasetRes,
                        "totalMsgs",
                        "./"+functionNames[i]+"/totalMsgs_thresh-"+threshold,
                        conf.saveFlag,
                        conf.showFlag)
        
        #total LVs bar chart
        __barChartPlots(datasetRes,
                        "totalLVs",
                        "./"+functionNames[i]+"/totalLVs_thresh-"+threshold,
                        conf.saveFlag,
                        conf.showFlag)
        
        #avgReqsPerLV bar chart
        __barChartPlots(datasetRes,
                        "avgReqsPerLv",
                        "./"+functionNames[i]+"/avgReqsPerLv_thresh-"+threshold,
                        conf.saveFlag,
                        conf.showFlag)
        
        #iters bar chart
        __barChartPlots(datasetRes,
                        "iters",
                        "./"+functionNames[i]+"/iters_thresh-"+threshold,
                        conf.saveFlag,
                        conf.showFlag)
        