'''
@author: ak
'''
import random as r
import pandas as pd
from Simulation.Utilities.DatasetHandler import createNormalsDataset,\
    splitTrainTestDataset
from Simulation.OptimalPairer.RandomPairer import RandomPairer
from Simulation.Network.SingleHandlingNetwork import SingleHandlingNetwork
from Simulation.Nodes.CoordinatorNode import CoordinatorNode
from Simulation.Nodes.MonitoringNode import MonitoringNode
from Simulation.Balancer.ClassicBalancer import classicBalancer

def test_enviroment():
    #number of nodes
    nodeNum=4
    
    #threshold
    thresh=30
    
    #monFunc
    monFunc=lambda x: x
    
    #create Dataset
    ds=pd.Panel({'n'+str(i):createNormalsDataset(r.randint(0, 10), 0.01, [50,1], cumsum=True) for i in range(nodeNum)})

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
    
    print(ntw.msgLog())
    
if __name__=='__main__':
    test_enviroment()