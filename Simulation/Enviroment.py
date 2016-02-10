'''
@author: ak
'''
import cPickle as pickle
import random as r
import pandas as pd
import scipy as sp
from Simulation.Utilities.DatasetHandler import createNormalsDataset,\
    splitTrainTestDataset
from Simulation.OptimalPairer.RandomPairer import RandomPairer
from Simulation.Network.SingleHandlingNetwork import SingleHandlingNetwork
from Simulation.Network.BlockingNetwork import BlockingNetwork
from Simulation.Nodes.CoordinatorNode import CoordinatorNode
from Simulation.Nodes.MonitoringNode import MonitoringNode
from Simulation.Balancer.ClassicBalancer import classicBalancer
from Simulation.Utilities.ArrayOperations import hashable
from Simulation.Balancer.HeuristicBalancer import heuristicBalancer
from Simulation.OptimalPairer.DistributionPairer import DistributionPairer
from Simulation.OptimalPairer.DistancePairer import DistancePairer
from Simulation.Utilities.Dec import *
from Simulation.Utilities.ExperimentalResultsHandler import saveExpResults

def monFunc1D(x):
    
    if (isinstance(x,sp.ndarray) and len(x)==1):
        return x[0]
    else:
        return x

def monFunc3D(x):
        return (x[0]+x[1])/x[2] if x[2]!=0.0 else (x[0]+x[1])

def monFunc5D(x):
    nom=x[0]+x[4]+x[3]
    denom=x[1]+x[2]
    
    return nom**2-denom


def monFunc10D(x):
    return ((x[0]+x[1]+x[2]-x[3]+x[4]-x[5]+x[6]-x[7]+x[8]-x[9]))**2
    
def test_enviroment():
    #tolerance
    tolerance=1e-7
    
    #global decimal context
    context=decimal.getcontext()
    context.prec=6
    context.rounding=getattr(decimal,'ROUND_HALF_EVEN')
    
    #number of nodes
    nodeNum=10
    
    #threshold
    thresh=1*10**4
    
    #monFunc !!!x is always an sp.ndarray
    monFunc=monFunc1D
    
    #create Dataset
    #ds=pd.Panel({'n'+str(i):createNormalsDataset(r.randint(0, 10), 0.01, [200,5], cumsum=True) for i in range(nodeNum)})
    ds=pd.read_pickle('/home/ak/git/GM_Experiment/Experiments/datasets/random1D10N.p')
    
    #create node weight dictionary
    nWd={'n'+str(i):1.0 for i in range(nodeNum)}
    
    #split dataset
    train,test=splitTrainTestDataset(ds)
    
    #create OptimalPairer
    pairer=RandomPairer(train)
    distributionPairer=DistributionPairer(deDec(train),monFunc,thresh)
    distancePairer=DistancePairer(deDec(train),nWd,monFunc)
    #print(distPairer.getTypeDict())
    #print(distPairer.getWeightDict())
    
    selectNodeReq=lambda coordInstance,x: distancePairer.getOptPairingfromSubset(x) and distancePairer.getOptPairingfromSubset(x) or pairer.getOptPairing(x)
    #selectNodeReq=lambda coordInstance,x: pairer.getOptPairing(x)
    
    #create network
    ntw=SingleHandlingNetwork()
    
    #create nodes
    nodes={'n'+str(i):MonitoringNode(ntw,test.loc['n'+str(i),:,:],thresh,monFunc,nid='n'+str(i),tolerance=tolerance) for i in range(nodeNum)}
    
    #create coordinator node
    coord=CoordinatorNode(network=ntw, nodes=nodes.keys(), threshold=thresh, monFunc=monFunc,tolerance=tolerance)
    
    #set node request mechanism
    setattr(CoordinatorNode,'selectNodeReq',selectNodeReq)
    
    #set balancing method
    setattr(CoordinatorNode,'balancer', heuristicBalancer)
    
    ntw.simulate()
    
    mL=ntw.getMsgLog()
    
    for msgType in mL:
        print(msgType)
        for msg in mL[msgType]:
            if msgType=='rep':
                print('Iter:%s, Sender:%s, Target:%s, MsgType:%s, Msg:%s'%(msg[0],msg[1],msg[2],msg[3],[msg[4][0].unwrap(),msg[4][1].unwrap(), msg[4][2]]))
            else:
                print(msg)
    
    for node in nodes:
        print(nodes[node].getMonFuncVelLog())
    
    print('FINISHED')
    saveExpResults('test', '/home/ak/git/GM_Experiment/', {'test':'test'}, pairer, nodes, coord, ntw, train, test)
    
    
if __name__=='__main__':
    
    test_enviroment()