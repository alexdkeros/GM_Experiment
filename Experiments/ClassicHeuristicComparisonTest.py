'''
Comparison of Classic and Heuristic balancing schemes

@author: ak
'''
import os
import pickle
import numpy as np
from GM_Exp.Utils.Plotter import multiplePlots2d
from GM_Exp.GM.Enviroment import Enviroment

#result parameters
saveFlag=False
showFlag=True
dataSetFolder="./test_datasets"


#result storage
classicBalResults=[]
heuristicBalResults=[]

#experimental parameters
monitoringFunction=lambda x:x
threshold=100

def __viewDataset(dataSetFile,pureName):
    print(dataSetFile)
    dataSet=pickle.load(open(dataSetFile,"rb"))
    ranges=[np.arange(dataSet["iterations"])]*dataSet["streams"]
    #velocities
    multiplePlots2d(ranges,
                    dataSet["velocities"],
                    xLabel="iterations",
                    yLabel="velocity",
                    title="velocities of "+pureName.replace('_',' '),
                    saveFlag=saveFlag,
                    filename="./"+pureName+"/vel_plot_"+pureName,
                    showFlag=showFlag)
    
    #updates
    multiplePlots2d(ranges,
                    dataSet["updates"],
                    xLabel="iterations",
                    yLabel="update",
                    title="updates of "+pureName.replace('_',' '),
                    saveFlag=saveFlag,
                    filename="./"+pureName+"/upd_plot_"+pureName,
                    showFlag=showFlag)
    
    #updates detailed
    multiplePlots2d([np.arange(10)]*dataSet["streams"],
                    [d[0:10] for d in dataSet["updates"]],
                    xLabel="iterations",
                    yLabel="update",
                    title="updates of "+pureName.replace('_',' '),
                    saveFlag=saveFlag,
                    filename="./"+pureName+"/detail_upd_plot_"+pureName,
                    showFlag=showFlag)
    
def __runExperimentsOnDataSet(dataSetFile):
    env=Enviroment(balancing="classic",
                   threshold=threshold,
                   monitoringFunction=monitoringFunction,
                   dataSetFile=dataSetFile)
    env.runSimulation(None)
    res=env.getExpRes()
    
if __name__ == '__main__':
    #load dataset
    print("---LOADING DATASETS---")
    datasets=os.listdir(dataSetFolder)
    print(datasets)
    
    for dataset in datasets:
        pureName=os.path.splitext(dataset)[0]
        if not os.path.exists(os.path.splitext(pureName)[0]):
            os.makedirs(pureName)
        __viewDataset(dataSetFolder+"/"+dataset,pureName)