'''
Experiments configuration parameters

@author: ak
'''

#classic heuristic comparison test
saveFlag=True
showFlag=False
dataSetFolder="/home/ak/workspace/GM_Experiment/Experiments/datasets"
repeats=10

thresholds=[100]
monitoringFunctions=[lambda x:x]#,lambda x:x**2]
functionNames=["x"]#,"x2"]

cumulationFactors=[2,5,7,10,12,15,17]
balTypes=["Classic",
          "StaticCumulative",
          "OnceCumulative",
          "IncrementalCumulative",
          "Heuristic",
          "HeuristicOnceCumulative",
          "HeuristicStaticCumulative",
          "HeuristicIncrementalCumulative",
          "NaiveHeuristic",
          "HeuristicOptimalPair"]
