'''
@author: ak
'''
import sys
sys.path.append('/home/ak/git/GM_Experiment/')

from Simulation.Utilities.DatasetHandler import splitTrainTestDataset
from Simulation.OptimalPairer.RandomPairer import RandomPairer
from Simulation.OptimalPairer.DistancePairer import DistancePairer
from Simulation.Network.SingleHandlingNetwork import SingleHandlingNetwork
from Simulation.Nodes.MonitoringNode import MonitoringNode
from Simulation.Nodes.CoordinatorNode import CoordinatorNode
from Simulation.Balancer.ClassicBalancer import classicBalancer
from Simulation.Utilities.ExperimentalResultsHandler import saveExpResults
from Simulation.Utilities.Dec import *
from Simulation.Balancer.HeuristicBalancer import heuristicBalancer

def classic_random_experiment(expName, dataset,datasetName, monFunc,monFuncDescription, threshold, repeats):
    
    for i in range(repeats):
        #split Dataset
        train, test=splitTrainTestDataset(dataset)
        
        #create OptimalPairer
        pairer=RandomPairer(train)
        
        #create network
        ntw=SingleHandlingNetwork()
        
        #create nodes
        nWd={nId: 1.0 for nId in dataset.items}
        nodes={nId:MonitoringNode(ntw,test.loc[nId,:,:],threshold,monFunc,nid=nId) for nId in dataset.items}
        
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
              'node_dict':nWd,
              'repeat':i}
        saveExpResults(expName+'_'+str(i), '/home/ak/git/GM_Experiment/Experiments/'+expName+'/', conf, pairer, nodes, coord, ntw, train, test)


def heuristic_distOptPair_experiment(expName, dataset,datasetName, monFunc,monFuncDescription, threshold, repeats):
    
    for i in range(repeats):
        #create network
        ntw=SingleHandlingNetwork()
        
        #split Dataset
        train, test=splitTrainTestDataset(dataset)
           
        #create nodes
        nWd={nId: 1.0 for nId in dataset.items}
        nodes={nId:MonitoringNode(ntw,test.loc[nId,:,:],threshold,monFunc,nid=nId) for nId in dataset.items}
        
        #create coordinator Node
        coord=CoordinatorNode(network=ntw, nodes=nodes.keys(), threshold=threshold,monFunc=monFunc)
        
        #create OptimalPairer
        pairer=RandomPairer(train)
        distPairer=DistancePairer(deDec(train),nWd,monFunc)
        
        
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
              'node_dict':nWd,
              'repeat':i}
        
        saveExpResults(expName+'_'+str(i), '/home/ak/git/GM_Experiment/Experiments/'+expName+'/', conf, distPairer, nodes, coord, ntw, train, test)

#===============================================================================
# MONITORING FUNCTIONS
#===============================================================================
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
    nom=x[0]+x[1]+x[2]+x[3]+x[4]+x[9]
    denom=x[5]+x[6]+x[7]+x[8]
    
    return (nom/denom)**2
#===============================================================================
# RUN
#===============================================================================
if __name__=='__main__':
    
    #datasets Load
    datasetPath='/home/ak/git/GM_Experiment/Experiments/datasets/'
    
    dslinear1D2N=pd.read_pickle(datasetPath+'linear1D2N.p')
    dsrandom1D2N=pd.read_pickle(datasetPath+'random1D2N.p')

    dslinear1D10N=pd.read_pickle(datasetPath+'linear1D10N.p')
    dsrandom1D10N=pd.read_pickle(datasetPath+'random1D10N.p')
    
    dslinear5D5N=pd.read_pickle(datasetPath+'linear5D5N.p')
    dsrandom5D5N=pd.read_pickle(datasetPath+'random5D5N.p')
    
    dslinear10D10N=pd.read_pickle(datasetPath+'linear10D10N.p')
    dsrandom10D10N=pd.read_pickle(datasetPath+'random10D10N.p')
    
    
    #classic random experiments
    classic_random_experiment('singleH_classic_random_linear_1D2N', dslinear1D2N, 'linear1D2N', monFunc1D, 'x', 600, repeats=10)
    classic_random_experiment('singleH_classic_random_random_1D2N', dsrandom1D2N, 'random1D2N', monFunc1D, 'x', 600, repeats=10)

    classic_random_experiment('singleH_classic_random_linear_1D10N', dslinear1D10N, 'linear1D10N', monFunc1D, 'x', 600, repeats=10)
    classic_random_experiment('singleH_classic_random_random_1D10N', dsrandom1D10N, 'random1D10N', monFunc1D, 'x', 600, repeats=10)
    
    classic_random_experiment('singleH_classic_random_linear_5D5N', dslinear5D5N, 'linear5D5N', monFunc5D, 'sq(x_0+x_4+x_3)-(x[1]+x[2])', 5000, repeats=10)
    classic_random_experiment('singleH_classic_random_random_5D5N', dsrandom5D5N, 'random5D5N', monFunc5D, 'sq(x_0+x_4+x_3)-(x[1]+x[2])', 5000, repeats=10)

    classic_random_experiment('singleH_classic_random_linear_10D10N', dslinear10D10N, 'linear10D10N', monFunc10D, '(sum(x_0-4)+x_9/sum(x_5-8))^2', 5000, repeats=10)
    classic_random_experiment('singleH_classic_random_random_10D10N', dsrandom10D10N, 'random10D10N', monFunc10D, '(sum(x_0-4)+x_9/sum(x_5-8))^2', 5000, repeats=10)
    
    #heuristic optpair experiments
    heuristic_distOptPair_experiment('singleH_heuristic_distOptPair_linear_1D2N', dslinear1D2N, 'linear1D2N', monFunc1D, 'x', 600, repeats=10)
    heuristic_distOptPair_experiment('singleH_heuristic_distOptPair_random_1D2N', dsrandom1D2N, 'random1D2N', monFunc1D, 'x', 600, repeats=10)

    heuristic_distOptPair_experiment('singleH_heuristic_distOptPair_linear_1D10N', dslinear1D10N, 'linear1D10N', monFunc1D, 'x', 600, repeats=10)
    heuristic_distOptPair_experiment('singleH_heuristic_distOptPair_random_1D10N', dsrandom1D10N, 'random1D10N', monFunc1D, 'x', 600, repeats=10)

    heuristic_distOptPair_experiment('singleH_heuristic_distOptPair_linear_5D5N', dslinear5D5N, 'linear5D5N', monFunc5D, 'sq(x_0+x_4+x_3)-(x[1]+x[2])', 5000, repeats=10)
    heuristic_distOptPair_experiment('singleH_heuristic_distOptPair_random_5D5N', dsrandom5D5N, 'random5D5N', monFunc5D, 'sq(x_0+x_4+x_3)-(x[1]+x[2])', 5000, repeats=10)

    heuristic_distOptPair_experiment('singleH_heuristic_distOptPair_linear_10D10N', dslinear10D10N, 'linear10D10N', monFunc10D, '(sum(x_0-4)+x_9/sum(x_5-8))^2', 5000, repeats=10)
    heuristic_distOptPair_experiment('singleH_heuristic_distOptPair_random_10D10N', dsrandom10D10N, 'random10D10N', monFunc10D, '(sum(x_0-4)+x_9/sum(x_5-8))^2', 5000, repeats=10)
    