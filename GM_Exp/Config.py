'''
@author: ak
'''
from __future__ import division
import math
import numpy as np

#- NODE RANGE
nodeStart=2 #2
nodeEnd=5 #50

#- THRESHOLD RANGE
thresStart=10 #10
thresEnd=15 #300

#- MEAN RANGE
meanStart=3 #0
meanEnd=5 #30
meanStep=0.5


#- STD RANGE
stdStart=0.5
stdEnd=1#10
stdStep=0.2

#- LAMBDA RANGE
lambdaStart=1
lambdaEnd=0
lambdaStep=0.2

expTypes=['Nodes', 'Threshold', 'Mean', 'Std','Lambda']
expRangeStart=None
expRangeEnd=None
expRangeStep=1

def config(type):
    global expRangeStart
    global expRangeEnd
    if type=='Nodes':
        expRangeStart=nodeStart
        expRangeEnd=nodeEnd
        
    elif type=='Threshold':
        expRangeStart=thresStart
        expRangeEnd=thresEnd
    elif type=='Mean':
        expRangeStart=meanStart
        expRangeEnd=meanEnd
        expRangeStep=meanStep
    elif type=='Std':
        expRangeStart=stdStart
        expRangeEnd=stdEnd
        expRangeStep=stdStep
    elif type=='Lambda':
        expRangeStart=lambdaStart
        expRangeEnd=lambdaEnd
        expRangeStep=lambdaStep



#--------------default values---------------------
#exp config
defRepeats=1 #30

#runtime limit(in sec)
timeLimit=30

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
threshold=50 #1000
defMonFunc= lambda x: x

#balancing - heuristic/classic
balancingTypes=['classic','heuristic']
balancing="heuristic"


#NLP
NLPPlot=False

    


        
