'''
Experiments configuration parameters

@author: ak
'''

#classic heuristic comparison test
saveFlag=True
showFlag=False
dataSetFolder="./datasets"

thresholds=[100]
monitoringFunctions=[lambda x:x, lambda x:x**2]
functionNames=["x", "x2"]

cumulationFactors=[2,5,7,10,12,15,17]
balTypes=["classic",
          "staticCumulative",
          "onceCumulative",
          "incrementalCumulative",
          "heuristic",
          "heuristicOnceCumulative",
          "heuristicStaticCumulative",
          "heuristicIncrementalCumulative"]
