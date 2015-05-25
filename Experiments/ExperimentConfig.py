'''
Experiments configuration parameters

@author: ak
'''

#classic heuristic comparison test
saveFlag=True
showFlag=False
dataSetFolder="./rerun_datasets"

thresholds=[100]
monitoringFunctions=[lambda x:x,lambda x:x,lambda x:x,lambda x:x,lambda x:x]# lambda x:x**2]
functionNames=["x-1", "x-2","x-3","x-4","x-5"]

cumulationFactors=[2,5,7,10,12,15,17]
balTypes=["classic",
          "staticCumulative",
          "onceCumulative",
          "incrementalCumulative",
          "heuristic",
          "heuristicOnceCumulative",
          "heuristicStaticCumulative",
          "heuristicIncrementalCumulative"]
