'''
@author: ak
'''
import sys


#- NODE RANGE
nodeStart=3 #2
nodeEnd=6 #50

#- THRESHOLD RANGE
thresStart=10 #10
thresEnd=30 #300

#- MEAN RANGE
meanStart=2 #0
meanEnd=5 #30
meanStep=0.5


#- STD RANGE
stdStart=3 #0.5
stdEnd=10#10
stdStep=0.5

#- LAMBDA RANGE
lambdaStart=0
lambdaEnd=1
lambdaStep=0.1

expTypes=['Nodes', 'Threshold', 'Mean', 'Std','Lambda']
#expTypes=['Lambda']
expRangeStart=None
expRangeEnd=None
expRangeStep=1

def config(exptype):
    global expRangeStart
    global expRangeEnd
    global expRangeStep
    if exptype=='Nodes':
        expRangeStart=nodeStart
        expRangeEnd=nodeEnd
        
    elif exptype=='Threshold':
        expRangeStart=thresStart
        expRangeEnd=thresEnd
    elif exptype=='Mean':
        expRangeStart=meanStart
        expRangeEnd=meanEnd
        expRangeStep=meanStep
    elif exptype=='Std':
        expRangeStart=stdStart
        expRangeEnd=stdEnd
        expRangeStep=stdStep
    elif exptype=='Lambda':
        expRangeStart=lambdaStart
        expRangeEnd=lambdaEnd
        expRangeStep=lambdaStep



#--------------default values---------------------
#exp config
defRepeats=2 #30

#runtime limit(in sec)
timeLimit=60

#default InputStream data
lambdaVel=1 #1:static , 0:random
defInitXData=0
streamNormalizing=True
dataSetFile=None

#default vel distribution params
defMeanN=(5,1+sys.float_info.min)
defStdN=(0,1+sys.float_info.min)

#default Node values
defNodeNum=5
defV=0
defWeight=1

#default geometric monitoring params
threshold=100 #100
defMonFunc= lambda x: x**2

#balancing - heuristic/classic
balancingTypes=["Classic","ClassicOnceCumulative","ClassicStaticCumulative","ClassicIncrementalCumulative",
                "Heuristic","HeuristicOnceCumulative","HeuristicStaticCumulative","HeuristicIncrementalCumulative","NaiveHeuristic"]
classicBalances=balancingTypes[0:4]
heuristicBalances=balancingTypes[4:]
balancing="Heuristic"
defCumulationFactor=defNodeNum/5

#NLP
NLPPlot=False

#plotting
showFlag=True
saveFlag=False

#decimal
prec=8
rounding="ROUND_HALF_DOWN"


        
