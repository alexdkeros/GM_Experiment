'''
Created on Feb 8, 2016

@author: ak
'''
import pandas as pd
import scipy as sp
from Simulation.Utilities.Plotter import multiplePlots2d

def bcheck(filename,monfunc):
    
    nodedata=pd.read_pickle(filename+'nodeData.p')
    
    nt=[[nodedata['uLogDict'][node][i][0] for i in range(len(nodedata['uLogDict'][node]))] for node in nodedata['uLogDict']]
    nv=[[nodedata['uLogDict'][node][i][1] for i in range(len(nodedata['uLogDict'][node]))] for node in nodedata['uLogDict']]
    fnv=[[monfunc(nodedata['uLogDict'][node][i][1]) for i in range(len(nodedata['uLogDict'][node]))] for node in nodedata['uLogDict']]
    
    vt=[range(len(nodedata['monFuncVelDict'][node])) for node in nodedata['monFuncVelDict']]
    vv=[nodedata['monFuncVelDict'][node] for node in nodedata['monFuncVelDict']]

    print(vv)
    
    coorddata=pd.read_pickle(filename+'coordData.p')
    
    b=coorddata
    
    bt=[i[0] for i in b]
    bv=[i[2] for i in b]
    fbv=[monfunc(i) for i in bv]
    
    networkData=pd.read_pickle(filename+'networkData.p')
    adjslk=networkData['msgLogDict']['adjSlk']
    print('------------------ADJSLKS '+str(len(adjslk)))
    for i in range(len(adjslk)):
        print(i)
        print(adjslk[i])
    print('------------------BALANCES '+str(len(b)))
    for i in range(len(b)):
        print(i)
        print('balsetlen:'+str(len(b[i][1])))
        print(b[i])
    print('-----------------------------------')
    multiplePlots2d(vt, vv, saveFlag=True, filename=filename+'vels')
    multiplePlots2d([bt]+nt, [fbv]+fnv, labels=['bal']+nodedata['uLogDict'].keys(),saveFlag=True,title=str(len(b))+' balances', filename=filename+'Us')
    
def monFunc1D(x):
    
    if (isinstance(x,sp.ndarray) and len(x)==1):
        return x[0]
    else:
        return x
    
def monFunc5D(x):
    nom=x[0]+x[4]+x[3]
    denom=x[1]+x[2]
    
    return nom**2-denom

def monFunc10D(x):
    return ((x[0]+x[1]+x[2]-x[3]+x[4]-x[5]+x[6]-x[7]+x[8]-x[9]))**2
    
if __name__=='__main__':
    
    filename=['/home/ak/git/GM_Experiment/Experiments/singleH_classic_random_linear_5D2N/singleH_classic_random_linear_5D2N_0/',
              '/home/ak/git/GM_Experiment/Experiments/singleH_heuristic_distOptPair_linear_5D2N/singleH_heuristic_distOptPair_linear_5D2N_0/']
    #filename='/home/ak/git/GM_Experiment/test/'
    for i in filename:
        bcheck(i, monFunc5D)
    
    
    