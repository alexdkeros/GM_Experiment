'''
@author: ak
'''
import pandas as pd
from Simulation.Utilities.Plotter import *

def countMsgs(networkDict):
    msgs=networkDict['msgLogDict']
    
    return sum([len(msgs[m]) for m in msgs if m!='globalViolation'])

if __name__=='__main__':
    
    resPath='/home/ak/git/GM_Experiment/Experiments/'
    f='networkData.p'
    #experimental result paths
    expRes=[[resPath+'singleH_classic_random_linear_1D2N/'+f,resPath+'singleH_classic_random_random_1D2N/'+f,resPath+'singleH_classic_random_linear_5D5N/'+f,resPath+'singleH_classic_random_random_5D5N/'+f,resPath+'singleH_classic_random_linear_10D10N/'+f,resPath+'singleH_classic_random_random_10D10N/'+f],
            [resPath+'singleH_heuristic_distOptPair_linear_1D2N/'+f,resPath+'singleH_heuristic_distOptPair_random_1D2N/'+f,resPath+'singleH_heuristic_distOptPair_linear_5D5N/'+f,resPath+'singleH_heuristic_distOptPair_random_5D5N/'+f,resPath+'singleH_heuristic_distOptPair_linear_10D10N/'+f,resPath+'singleH_heuristic_distOptPair_random_10D10N/'+f]]
    
    resDicts=[map(pd.read_pickle,i) for i in expRes]
    
    counts=[map(countMsgs,i) for i in resDicts]
    
    barChart(counts, labels=['classic random','heuristic dist opt pair'], xticks=['linear1D2N','random1D2N','linear5D5N','random5D5N','linear10D10N','random10D10N'], saveFlag=True, filename=resPath+'Simple_showcase_msg_count', showFlag=True,figsize=(20,10))