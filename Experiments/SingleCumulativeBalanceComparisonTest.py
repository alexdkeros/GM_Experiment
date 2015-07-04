'''
Comparison of Cumulative and Classic balancing schemes

@author: ak
'''
import os
import pickle
import numpy as np
from GM_Exp.Util.Plotter import multiplePlots2d
from GM_Exp.Util.Plotter import barChart
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
    
    
    
    
    
    
def __runExperimentsOnDataSet(dataSetFile,balancing, cumulationFactor,threshold, monitoringFunction):
    '''
    runs classic and heuristic tests on dataset
    args:
        @param dataSetFile: dataset file
        @param balancing: balancing scheme
        @param cumulationFactor: cumulation factor for cumulative balancing schemes
        @param threshold: monitoring threshold
        @param monitoringFunction: the monitoring function
    @return: results for classic and heuristic tests, dict {"classic":{},"heuristic":{}}
    '''
    env=Enviroment(balancing=balancing,
                   cumulationFactor=cumulationFactor,
                   threshold=threshold,
                   monitoringFunction=monitoringFunction,
                   dataSetFile=dataSetFile)
    env.runSimulation(None)
    
    return env.getExpRes()
    



    
if __name__ == '__main__':
    #params
    thresholds=conf.thresholds
    monitoringFunctions=conf.monitoringFunctions
    functionNames=conf.functionNames
    cumulationFactors=conf.cumulationFactors
    balTypes=conf.balTypes
    
    #load dataset
    print("---LOADING DATASETS---")
    datasets=os.listdir(conf.dataSetFolder)
    print(datasets)
    for threshold in thresholds:
        for i in range(len(monitoringFunctions)):
                   
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
                
                balRes={}
                for bal in balTypes:
                    methodRes={}
                    for cumulation in cumulationFactors:
                        res=__runExperimentsOnDataSet(conf.dataSetFolder+"/"+dataset,
                                                      bal, 
                                                      cumulation, 
                                                      threshold, 
                                                      monitoringFunctions[i])
                        methodRes[cumulation]=res
                    balRes[bal]=methodRes
                
                #barCharts
                
                #total msgs
                barChart([[balRes[key][keyb]["totalMsgs"] for keyb in cumulationFactors] for key in balTypes],
                         labels=balTypes,
                         xLabel="cumulation factor",
                         yLabel="total msgs",
                         title="total msgs compare for f()="+functionNames[i]+" dataset:"+pureName.replace("_"," "),
                         xticks=map(str,cumulationFactors),
                         saveFlag=conf.saveFlag,
                         filename="./"+pureName+"/total_msgs_cmp_f_"+functionNames[i]+pureName,
                         showFlag=conf.showFlag,
                         figsize=(155,15),totalBarWidth=0.82)
                #total lvs
                barChart([[balRes[key][keyb]["totalLVs"] for keyb in cumulationFactors] for key in balTypes],
                         labels=balTypes,
                         xLabel="cumulation factor",
                         yLabel="total lvs",
                         title="total lvs compare for f()="+functionNames[i]+" dataset:"+pureName.replace("_"," "),
                         xticks=map(str,cumulationFactors),
                         saveFlag=conf.saveFlag,
                         filename="./"+pureName+"/total_lvs_cmp_f_"+functionNames[i]+pureName,
                         showFlag=conf.showFlag,
                         figsize=(155,15),totalBarWidth=0.82)
                #iters
                barChart([[balRes[key][keyb]["iters"] for keyb in cumulationFactors] for key in balTypes],
                         labels=balTypes,
                         xLabel="cumulation factor",
                         yLabel="iters",
                         title="iters compare for f()="+functionNames[i]+" dataset:"+pureName.replace("_"," "),
                         xticks=map(str,cumulationFactors),
                         saveFlag=conf.saveFlag,
                         filename="./"+pureName+"/iters_cmp_f_"+functionNames[i]+pureName,
                         showFlag=conf.showFlag,
                         figsize=(155,15),totalBarWidth=0.82)
                #avgReqsPerLv
                barChart([[balRes[key][keyb]["avgReqsPerLv"] for keyb in cumulationFactors] for key in balTypes],
                         labels=balTypes,
                         xLabel="cumulation factor",
                         yLabel="avg reqs per lv",
                         title="avg reqs per lv compare for f()="+functionNames[i]+" dataset:"+pureName.replace("_"," "),
                         xticks=map(str,cumulationFactors),
                         saveFlag=conf.saveFlag,
                         filename="./"+pureName+"/avgReqsPerLv_cmp_f_"+functionNames[i]+pureName,
                         showFlag=conf.showFlag,
                         figsize=(155,15),totalBarWidth=0.82)
                
                