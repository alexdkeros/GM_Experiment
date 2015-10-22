'''
@author: ak
'''
import os
import pandas as pd
from Simulation.Utilities.Plotter import *
from scipy import mean

def countMsgs(networkDict):
    msgs=networkDict['msgLogDict']
    
    return sum([len(msgs[m]) for m in msgs if m!='globalViolation'])

def collectMeanMetricFromSubfolders(p,f):
    '''
    parent, file
    '''
    #extract subfolders (repeats)
    subfolders=next(os.walk(p))[1]
    
    #create full path to file for each one
    subfolders=[p+i+'/'+f for i in subfolders]
    
    #dictionary inside pickle file
    resDicts=[pd.read_pickle(i) for i in subfolders]
    
    #get desired value from each one
    res=[countMsgs(i) for i in resDicts]
    
    return mean(res)

if __name__=='__main__':
    
    resPath='/home/ak/git/GM_Experiment/Experiments/'
    f='networkData.p'
    
    #experimental result paths
    expRes=[[resPath+'singleH_classic_random_linear_1D2N/',resPath+'singleH_classic_random_random_1D2N/',resPath+'singleH_classic_random_linear_1D10N/',resPath+'singleH_classic_random_random_1D10N/',resPath+'singleH_classic_random_linear_5D5N/',resPath+'singleH_classic_random_random_5D5N/',resPath+'singleH_classic_random_linear_10D10N/',resPath+'singleH_classic_random_random_10D10N/'],
            [resPath+'singleH_heuristic_distOptPair_linear_1D2N/',resPath+'singleH_heuristic_distOptPair_random_1D2N/',resPath+'singleH_heuristic_distOptPair_linear_1D10N/',resPath+'singleH_heuristic_distOptPair_random_1D10N/',resPath+'singleH_heuristic_distOptPair_linear_5D5N/',resPath+'singleH_heuristic_distOptPair_random_5D5N/',resPath+'singleH_heuristic_distOptPair_linear_10D10N/',resPath+'singleH_heuristic_distOptPair_random_10D10N/']]
    
    counts=[[collectMeanMetricFromSubfolders(fol, f) for fol in p] for p in expRes]
    
    barChart(counts, labels=['classic random','heuristic dist opt pair'], xticks=['linear1D2N','random1D2N','linear1D10N','random1D10N','linear5D5N','random5D5N','linear10D10N','random10D10N'], saveFlag=True, filename=resPath+'Simple_showcase_msg_count', showFlag=False,figsize=(20,10))