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
    
def test_enviroment():
    #number of nodes
    nodeNum=5
    
    #threshold
    thresh=10000
    
    #monFunc !!!x is always an sp.ndarray
    monFunc=monFunc5D
    
    #create Dataset
    ds=pd.Panel({'n'+str(i):createNormalsDataset(r.randint(0, 10), 0.01, [200,5], cumsum=True) for i in range(nodeNum)})
    
    #create node weight dictionary
    nWd={'n'+str(i):1.0 for i in range(nodeNum)}
    
    #split dataset
    train,test=splitTrainTestDataset(ds)
    
    #create OptimalPairer
    pairer=RandomPairer(train)
    distPairer=DistributionPairer(deDec(train),monFunc,thresh)
    
    print(distPairer.getTypeDict())
    print(distPairer.getWeightDict())
    
    selectNodeReq=lambda coordInstance,x: distPairer.getOptPairingfromSubset(x) and distPairer.getOptPairingfromSubset(x) or pairer.getOptPairing(x)
    
    #create network
    ntw=SingleHandlingNetwork()
    
    #create nodes
    nodes={'n'+str(i):MonitoringNode(ntw,test.loc['n'+str(i),:,:],thresh,monFunc,nid='n'+str(i)) for i in range(nodeNum)}
    
    #create coordinator node
    coord=CoordinatorNode(network=ntw, nodes=nodes.keys(), threshold=thresh, monFunc=monFunc)
    
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
    
    print(coord.getbLog())
    
    saveExpResults('test', '/home/ak/git/GM_Experiment/', {'test':'test'}, distPairer, nodes, coord, ntw, train, test)
    
    
if __name__=='__main__':
    test_enviroment()