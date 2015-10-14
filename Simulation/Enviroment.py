'''
@author: ak
'''
import random as r
import pandas as pd
import scipy as sp
from Simulation.Utilities.DatasetHandler import createNormalsDataset,\
    splitTrainTestDataset
from Simulation.OptimalPairer.RandomPairer import RandomPairer
from Simulation.Network.SingleHandlingNetwork import SingleHandlingNetwork
from Simulation.Nodes.CoordinatorNode import CoordinatorNode
from Simulation.Nodes.MonitoringNode import MonitoringNode
from Simulation.Balancer.ClassicBalancer import classicBalancer
from Simulation.Utilities.ArrayOperations import hashable

def monFunc1D(x):
    
    if (isinstance(x,sp.ndarray) and len(x)==1):
        return x[0]
    else:
        return x

def monFunc2D(x):
    return x[0]+x[1]

def test_enviroment():
    #number of nodes
    nodeNum=2
    
    #threshold
    thresh=30
    
    #monFunc !!!x is always an sp.ndarray
    monFunc=monFunc2D
    
    #create Dataset
    ds=pd.Panel({'n'+str(i):createNormalsDataset(r.randint(0, 5), 0.01, [50,2], cumsum=True) for i in range(nodeNum)})

    #split dataset
    train,test=splitTrainTestDataset(ds)
    
    #create OptimalPairer
    pairer=RandomPairer(train)
    
    #create network
    ntw=SingleHandlingNetwork()
    
    #create nodes
    nodes={'n'+str(i):MonitoringNode(ntw,test.loc['n'+str(i),:,:],thresh,monFunc,nid='n'+str(i)) for i in range(nodeNum)}
    
    #create coordinator node
    coord=CoordinatorNode(network=ntw, nodes=nodes.keys(), threshold=thresh, monFunc=monFunc)
    
    #set node request mechanism
    setattr(CoordinatorNode,'selectNodeReq',pairer.getOptPairing)
    
    #set balancing method
    setattr(CoordinatorNode,'balancer', classicBalancer)
    
    ntw.simulate()
    
    mL=ntw.getMsgLog()
    
    for msgType in mL:
        print(msgType)
        for msg in mL[msgType]:
            if msgType=='rep':
                print('Iter:%s, Sender:%s, Target:%s, MsgType:%s, Msg:%s'%(msg[0],msg[1],msg[2],msg[3],[msg[4][0].unwrap(),msg[4][1].unwrap(), msg[4][2]]))
            else:
                print(msg)
                
    
if __name__=='__main__':
    test_enviroment()