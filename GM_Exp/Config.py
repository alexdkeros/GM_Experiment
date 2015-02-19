'''
@author: ak
'''
from __future__ import division
import math
import numpy as np

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

#expTypes=['Nodes', 'Threshold', 'Mean', 'Std','Lambda']
expTypes=['Lambda']
expRangeStart=None
expRangeEnd=None
expRangeStep=1

def config(type):
    global expRangeStart
    global expRangeEnd
    global expRangeStep
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
defRepeats=2 #30

#runtime limit(in sec)
timeLimit=60

#default InputStream data
lambdaVel=1 #1:static , 0:random
defInitXData=0
streamNormalizing=True

#default vel distribution params
defMeanN=(5,1)
defStdN=(0,1)

#default Node values
defNodeNum=5
defV=0
defWeight=1

#default geometric monitoring params
threshold=100 #100
defMonFunc= lambda x: x

#balancing - heuristic/classic
balancingTypes=['classic','heuristic']
#balancingTypes=['classic']
balancing="heuristic"


#NLP
NLPPlot=True

#plotting
showFlag=False
saveFlag=True

    


        
