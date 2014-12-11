'''
@author: ak
'''
from __future__ import division
import math
import numpy as np

#- NODE RANGE
nodeStart=2 #2
nodeEnd=50 #50

#- THRESHOLD RANGE
thresStart=10
thresEnd=300 #300

#- MEAN RANGE
meanStart=0 #0
meanEnd=30 #30
meanStep=0.5
meanLvsPerIterPlotLim=500
meanReqPerBalPlotLim=100

#- STD RANGE
stdStart=0.5
stdEnd=10 #10
stdStep=0.2
stdLvsPerIterPlotLim=500
stdReqPerBalPlotLim=100

expTypes=['Nodes', 'Threshold', 'Mean', 'Std']
expRangeStart=None
expRangeEnd=None

def config(type):
    global expRangeStart
    global expRangeEnd
    if type=='Nodes':
        expRangeStart=nodeStart
        expRangeEnd=nodeEnd
    elif type=='Threshhold':
        expRangeStart=thresStart
        expRangeEnd=thresEnd
    elif type=='Mean':
        expRangeStart=meanStart
        expRangeEnd=meanEnd
    elif type=='Std':
        expRangeStart=stdStart
        expRangeEnd=stdEnd



#--------------default values---------------------
#exp config
defRepeats=1 #30

#runtime limit(in sec)
timeLimit=50

#default InputStream data
lambdaVel=1 #1:static , 0:random
defInitXData=0

#default vel distribution params
defMean=5
defStd=1

#default Node values
defNodeNum=5
defV=0
defWeight=1

#default geometric monitoring params
threshold=100 #1000
defMonFunc= lambda x: x

#balancing
balancing="heuristic"

if balancing=="classic":
    rep="classicRep"
    balancingMethod="classicBalance"
elif balancing=="heuristic":
    rep="heuristicRep"
    balancingMethod="heuristicBalance"
    


        
