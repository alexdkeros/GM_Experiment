'''
@author: ak
'''
from Simulation.Utilities.DatasetHandler import splitTrainTestDataset
from Simulation.OptimalPairer.RandomPairer import RandomPairer
from Simulation.Network.SingleHandlingNetwork import SingleHandlingNetwork
from Simulation.Nodes.MonitoringNode import MonitoringNode
from Simulation.Nodes.CoordinatorNode import CoordinatorNode
from Simulation.Balancer.ClassicBalancer import classicBalancer
from Simulation.Utilities.ExperimentalResultsHandler import saveExpResults
from Simulation.OptimalPairer.DistributionPairer import DistributionPairer
from Simulation.Utilities.Dec import *
from Simulation.Balancer.HeuristicBalancer import heuristicBalancer

def classic_random_experiment(expName, dataset,datasetName, monFunc,monFuncDescription, threshold):
    
    #split Dataset
    train, test=splitTrainTestDataset(dataset)
    
    #create OptimalPairer
    pairer=RandomPairer(train)
    
    #create network
    ntw=SingleHandlingNetwork()
    
    #create nodes
    nWd={nId: 1.0 for nId in dataset.items}
    nodes={nId:MonitoringNode(ntw,test.loc[nId,:,:],threshold,monFunc) for nId in dataset.items}
    
    #create coordinator Node
    coord=CoordinatorNode(network=ntw, nodes=nodes.keys(), threshold=threshold,monFunc=monFunc)
    
    #set node request mechanism
    selectNodeReq=lambda coordInstance,x: pairer.getOptPairing(x)

    setattr(CoordinatorNode,'selectNodeReq',selectNodeReq)
    
    #set balancing method
    setattr(CoordinatorNode,'balancer', classicBalancer)
    
    #simulate
    ntw.simulate()
    
    #save results
    conf={'threshold':threshold,
          'monFunc':monFuncDescription,
          'bal_type':'classic',
          'pairer_type':'random',
          'network_type':'singleHandling',
          'node_num':len(dataset.items),
          'data_dims':len(dataset.minor_axis),
          'dataset_name':datasetName,
          'node_dict':nWd}
    saveExpResults(expName, '/home/ak/git/GM_Experiment/Experiments/', conf, pairer, nodes, coord, ntw, train, test)


def heuristic_distOptPair_experiment(expName, dataset,datasetName, monFunc,monFuncDescription, threshold):
    
    #split Dataset
    train, test=splitTrainTestDataset(dataset)
    
    #create OptimalPairer
    pairer=RandomPairer(train)
    distPairer=DistributionPairer(deDec(train),monFunc,threshold)
    
    #create network
    ntw=SingleHandlingNetwork()
    
    #create nodes
    nWd={nId: 1.0 for nId in dataset.items}
    nodes={nId:MonitoringNode(ntw,test.loc[nId,:,:],threshold,monFunc) for nId in dataset.items}
    
    #create coordinator Node
    coord=CoordinatorNode(network=ntw, nodes=nodes.keys(), threshold=threshold,monFunc=monFunc)
    
    #set node request mechanism
    selectNodeReq=lambda coordInstance,x: distPairer.getOptPairingfromSubset(x) and distPairer.getOptPairingfromSubset(x) or pairer.getOptPairing(x)

    setattr(CoordinatorNode,'selectNodeReq',selectNodeReq)
    
    #set balancing method
    setattr(CoordinatorNode,'balancer', heuristicBalancer)
    
    #simulate
    ntw.simulate()
    
    #save results
    conf={'threshold':threshold,
          'monFunc':monFuncDescription,
          'bal_type':'heuristic',
          'pairer_type':'distance_opt_pair_and_random',
          'network_type':'singleHandling',
          'node_num':len(dataset.items),
          'data_dims':len(dataset.minor_axis),
          'dataset_name':datasetName,
          'node_dict':nWd}
    saveExpResults(expName, '/home/ak/git/GM_Experiment/Experiments/', conf, pairer, nodes, coord, ntw, train, test)

    