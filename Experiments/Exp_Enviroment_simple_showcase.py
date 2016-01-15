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

#===============================================================================
# CLASSIC RANDOM
#===============================================================================
def classic_random_experiment(expName,train, test,datasetName, monFunc,monFuncDescription, threshold, repeats, wl, wr, approxorder, tolerance):
    
    for i in range(repeats):
        
        print('**************************************REPEAT %d****************************************'%i)
        
        #create OptimalPairer
        pairer=RandomPairer(train)
        
        #create network
        ntw=SingleHandlingNetwork()
        
        #create nodes
        nWd={nId: 1.0 for nId in test.items}
        nodes={nId:MonitoringNode(ntw,test.loc[nId,:,:],threshold,monFunc,nid=nId,wl=wl,wr=wr,approximationOrder=approxorder,tolerance=tolerance) for nId in test.items}
        
        #create coordinator Node
        coord=CoordinatorNode(network=ntw, nodes=nodes.keys(), threshold=threshold,monFunc=monFunc,tolerance=tolerance)
        
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
              'node_num':len(test.items),
              'data_dims':len(test.minor_axis),
              'dataset_name':datasetName,
              'node_dict':nWd,
              'repeat':i,
              'wl':wl,
              'wr':wr,
              'apporder':approxorder,
              'tol':tolerance}
        saveExpResults(expName+'_'+str(i), '/home/ak/git/GM_Experiment/Experiments/'+expName+'/', conf, pairer, nodes, coord, ntw, train, test)

#===============================================================================
# HEURISIC RANDOM
#===============================================================================

def heuristic_random_experiment(expName, train, test,datasetName, monFunc,monFuncDescription, threshold, repeats, wl, wr, approxorder, tolerance):
    
    for i in range(repeats):
        
        print('**************************************REPEAT %d****************************************'%i)

        
        #create OptimalPairer
        pairer=RandomPairer(train)
        
        #create network
        ntw=SingleHandlingNetwork()
        
        #create nodes
        nWd={nId: 1.0 for nId in test.items}
        nodes={nId:MonitoringNode(ntw,test.loc[nId,:,:],threshold,monFunc,nid=nId,wl=wl,wr=wr,approximationOrder=approxorder,tolerance=tolerance) for nId in test.items}
        
        #create coordinator Node
        coord=CoordinatorNode(network=ntw, nodes=nodes.keys(), threshold=threshold,monFunc=monFunc,tolerance=tolerance)
        
        #set node request mechanism
        selectNodeReq=lambda coordInstance,x: pairer.getOptPairing(x)
    
        setattr(CoordinatorNode,'selectNodeReq',selectNodeReq)
        
        #set balancing method
        setattr(CoordinatorNode,'balancer', heuristicBalancer)
        
        #simulate
        ntw.simulate()
        
        #save results
        conf={'threshold':threshold,
              'monFunc':monFuncDescription,
              'bal_type':'heuristic',
              'pairer_type':'random',
              'network_type':'singleHandling',
              'node_num':len(test.items),
              'data_dims':len(test.minor_axis),
              'dataset_name':datasetName,
              'node_dict':nWd,
              'repeat':i,
              'wl':wl,
              'wr':wr,
              'apporder':approxorder,
              'tol':tolerance}
        saveExpResults(expName+'_'+str(i), '/home/ak/git/GM_Experiment/Experiments/'+expName+'/', conf, pairer, nodes, coord, ntw, train, test)

#===============================================================================
# CLASSIC DISTANCE OPTPAIR
#===============================================================================

def classic_distOptPair_experiment(expName, train, test,datasetName, monFunc,monFuncDescription, threshold, repeats, wl, wr, approxorder, tolerance):
    
    for i in range(repeats):
        
        print('**************************************REPEAT %d****************************************'%i)
        
        #create network
        ntw=SingleHandlingNetwork()
           
        #create nodes
        nWd={nId: 1.0 for nId in test.items}
        nodes={nId:MonitoringNode(ntw,test.loc[nId,:,:],threshold,monFunc,nid=nId,wl=wl,wr=wr,approximationOrder=approxorder,tolerance=tolerance) for nId in test.items}
        
        #create coordinator Node
        coord=CoordinatorNode(network=ntw, nodes=nodes.keys(), threshold=threshold,monFunc=monFunc,tolerance=tolerance)
        
        #create OptimalPairer
        pairer=RandomPairer(train)
        distPairer=DistancePairer(deDec(train),nWd,monFunc)
        
        
        #set node request mechanism
        selectNodeReq=lambda coordInstance,x: distPairer.getOptPairingfromSubset(x) and distPairer.getOptPairingfromSubset(x) or pairer.getOptPairing(x)
    
        setattr(CoordinatorNode,'selectNodeReq',selectNodeReq)
        
        #set balancing method
        setattr(CoordinatorNode,'balancer', classicBalancer)
        
        #simulate
        ntw.simulate()
        
        #save results
        conf={'threshold':threshold,
              'monFunc':monFuncDescription,
              'bal_type':'classic',
              'pairer_type':'distance_opt_pair_and_random',
              'network_type':'singleHandling',
              'node_num':len(test.items),
              'data_dims':len(test.minor_axis),
              'dataset_name':datasetName,
              'node_dict':nWd,
              'repeat':i,
              'wl':wl,
              'wr':wr,
              'apporder':approxorder,
              'tol':tolerance}
        
        saveExpResults(expName+'_'+str(i), '/home/ak/git/GM_Experiment/Experiments/'+expName+'/', conf, distPairer, nodes, coord, ntw, train, test)

#===============================================================================
# HEURISTIC DISTANCE OPTPAIR
#===============================================================================

def heuristic_distOptPair_experiment(expName,train, test,datasetName, monFunc,monFuncDescription, threshold, repeats, wl, wr, approxorder, tolerance):
    
    for i in range(repeats):
        
        print('**************************************REPEAT %d****************************************'%i)
        
        #create network
        ntw=SingleHandlingNetwork()
           
        #create nodes
        nWd={nId: 1.0 for nId in test.items}
        nodes={nId:MonitoringNode(ntw,test.loc[nId,:,:],threshold,monFunc,nid=nId,wl=wl,wr=wr,approximationOrder=approxorder,tolerance=tolerance) for nId in test.items}
        
        #create coordinator Node
        coord=CoordinatorNode(network=ntw, nodes=nodes.keys(), threshold=threshold,monFunc=monFunc,tolerance=tolerance)
        
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
              'node_num':len(test.items),
              'data_dims':len(test.minor_axis),
              'dataset_name':datasetName,
              'node_dict':nWd,
              'repeat':i,
              'wl':wl,
              'wr':wr,
              'apporder':approxorder,
              'tol':tolerance}
        
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
    return ((x[0]-x[1]+x[2]-x[3]+x[4]-x[5]+x[6]-x[7]+x[8]-x[9])/10)**2
#===============================================================================
# RUN
#===============================================================================
if __name__=='__main__':
    #tolerance
    tolerance=1e-3
    
    #global decimal context
    context=decimal.getcontext()
    context.prec=4
    context.rounding=getattr(decimal,'ROUND_HALF_EVEN')
    
    #datasets Load
    datasetPath='/home/ak/git/GM_Experiment/Experiments/datasets/'
    
    train_dslinear1D2N,test_dslinear1D2N=splitTrainTestDataset(pd.read_pickle(datasetPath+'linear1D2N.p'))
    train_dsrandom1D2N,test_dsrandom1D2N=splitTrainTestDataset(pd.read_pickle(datasetPath+'random1D2N.p'))
  
    train_dslinear1D5N,test_dslinear1D5N=splitTrainTestDataset(pd.read_pickle(datasetPath+'linear1D5N.p'))
    train_dsrandom1D5N,test_dsrandom1D5N=splitTrainTestDataset(pd.read_pickle(datasetPath+'random1D5N.p'))
     
    train_dslinear1D10N,test_dslinear1D10N=splitTrainTestDataset(pd.read_pickle(datasetPath+'linear1D10N.p'))
    train_dsrandom1D10N,test_dsrandom1D10N=splitTrainTestDataset(pd.read_pickle(datasetPath+'random1D10N.p'))
     
    train_dslinear5D2N,test_dslinear5D2N=splitTrainTestDataset(pd.read_pickle(datasetPath+'linear5D2N.p'))
    train_dsrandom5D2N,test_dsrandom5D2N=splitTrainTestDataset(pd.read_pickle(datasetPath+'random5D2N.p'))
      
    train_dslinear5D5N,test_dslinear5D5N=splitTrainTestDataset(pd.read_pickle(datasetPath+'linear5D5N.p'))
    train_dsrandom5D5N,test_dsrandom5D5N=splitTrainTestDataset(pd.read_pickle(datasetPath+'random5D5N.p'))
      
    train_dslinear5D10N,test_dslinear5D10N=splitTrainTestDataset(pd.read_pickle(datasetPath+'linear5D10N.p'))
    train_dsrandom5D10N,test_dsrandom5D10N=splitTrainTestDataset(pd.read_pickle(datasetPath+'random5D10N.p'))
      
    train_dslinear10D2N,test_dslinear10D2N=splitTrainTestDataset(pd.read_pickle(datasetPath+'linear10D2N.p'))
    train_dsrandom10D2N,test_dsrandom10D2N=splitTrainTestDataset(pd.read_pickle(datasetPath+'random10D2N.p'))
     
    train_dslinear10D5N,test_dslinear10D5N=splitTrainTestDataset(pd.read_pickle(datasetPath+'linear10D5N.p'))
    train_dsrandom10D5N,test_dsrandom10D5N=splitTrainTestDataset(pd.read_pickle(datasetPath+'random10D5N.p'))
       
    train_dslinear10D10N,test_dslinear10D10N=splitTrainTestDataset(pd.read_pickle(datasetPath+'linear10D10N.p'))
    train_dsrandom10D10N,test_dsrandom10D10N=splitTrainTestDataset(pd.read_pickle(datasetPath+'random10D10N.p'))
     
    
   #============================================================================
   #  #classic random experiments
   #  classic_random_experiment('singleH_classic_random_linear_1D2N', train_dslinear1D2N,test_dslinear1D2N, 'linear1D2N', monFunc1D, 'x', 4*10**3, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
   #  classic_random_experiment('singleH_classic_random_random_1D2N', train_dsrandom1D2N,test_dsrandom1D2N, 'random1D2N', monFunc1D, 'x', 4*10**3, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
   #      
   #  classic_random_experiment('singleH_classic_random_linear_1D5N', train_dslinear1D5N,test_dslinear1D5N, 'linear1D5N', monFunc1D, 'x', 4*10**3, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
   #  classic_random_experiment('singleH_classic_random_random_1D5N', train_dsrandom1D5N,test_dsrandom1D5N, 'random1D5N', monFunc1D, 'x', 4*10**3, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
   #      
   #  classic_random_experiment('singleH_classic_random_linear_1D10N', train_dslinear1D10N,test_dslinear1D10N, 'linear1D10N', monFunc1D, 'x', 4*10**3, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
   #  classic_random_experiment('singleH_classic_random_random_1D10N', train_dsrandom1D10N,test_dsrandom1D10N, 'random1D10N', monFunc1D, 'x', 4*10**3, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
   #      
   #  classic_random_experiment('singleH_classic_random_linear_5D2N', train_dslinear5D2N,test_dslinear5D2N, 'linear5D2N', monFunc5D, 'sq(x_0+x_4+x_3)-(x[1]+x[2])', 1*10**6, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
   #  classic_random_experiment('singleH_classic_random_random_5D2N', train_dsrandom5D2N,test_dsrandom5D2N, 'random5D2N', monFunc5D, 'sq(x_0+x_4+x_3)-(x[1]+x[2])', 1*10**6, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
   #       
   #  classic_random_experiment('singleH_classic_random_linear_5D5N', train_dslinear5D5N,test_dslinear5D5N, 'linear5D5N', monFunc5D, 'sq(x_0+x_4+x_3)-(x[1]+x[2])', 1*10**6, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
   #  classic_random_experiment('singleH_classic_random_random_5D5N', train_dsrandom5D5N,test_dsrandom5D5N, 'random5D5N', monFunc5D, 'sq(x_0+x_4+x_3)-(x[1]+x[2])', 1*10**6, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
   #     
   #  classic_random_experiment('singleH_classic_random_linear_5D10N', train_dslinear5D10N,test_dslinear5D10N, 'linear5D10N', monFunc5D, 'sq(x_0+x_4+x_3)-(x[1]+x[2])', 1*10**6, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
   #  classic_random_experiment('singleH_classic_random_random_5D10N', train_dsrandom5D10N,test_dsrandom5D10N, 'random5D10N', monFunc5D, 'sq(x_0+x_4+x_3)-(x[1]+x[2])', 1*10**6, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
   #     
   #  classic_random_experiment('singleH_classic_random_linear_10D2N', train_dslinear10D2N,test_dslinear10D2N, 'linear10D2N', monFunc10D, '((x[0]-x[1]+x[2]-x[3]+x[4]-x[5]+x[6]-x[7]+x[8]-x[9])/10)**2', 1*10**6, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
   #  classic_random_experiment('singleH_classic_random_random_10D2N', train_dsrandom10D2N,test_dsrandom10D2N, 'random10D2N', monFunc10D, '((x[0]-x[1]+x[2]-x[3]+x[4]-x[5]+x[6]-x[7]+x[8]-x[9])/10)**2', 1*10**6, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
   #      
   #  classic_random_experiment('singleH_classic_random_linear_10D5N', train_dslinear10D5N,test_dslinear10D5N, 'linear10D5N', monFunc10D, '((x[0]-x[1]+x[2]-x[3]+x[4]-x[5]+x[6]-x[7]+x[8]-x[9])/10)**2', 1*10**6, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
   #  classic_random_experiment('singleH_classic_random_random_10D5N', train_dsrandom10D5N,test_dsrandom10D5N, 'random10D5N', monFunc10D, '((x[0]-x[1]+x[2]-x[3]+x[4]-x[5]+x[6]-x[7]+x[8]-x[9])/10)**2', 1*10**6, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
   #      
   #  classic_random_experiment('singleH_classic_random_linear_10D10N', train_dslinear10D10N,test_dslinear10D10N, 'linear10D10N', monFunc10D, '((x[0]-x[1]+x[2]-x[3]+x[4]-x[5]+x[6]-x[7]+x[8]-x[9])/10)**2', 1*10**6, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
   #  classic_random_experiment('singleH_classic_random_random_10D10N', train_dsrandom10D10N,test_dsrandom10D10N, 'random10D10N', monFunc10D, '((x[0]-x[1]+x[2]-x[3]+x[4]-x[5]+x[6]-x[7]+x[8]-x[9])/10)**2', 1*10**6, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
   #    
   #  #heuristic random experiments
   #  heuristic_random_experiment('singleH_heuristic_random_linear_1D2N', train_dslinear1D2N,test_dslinear1D2N, 'linear1D2N', monFunc1D, 'x', 4*10**3, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
   #  heuristic_random_experiment('singleH_heuristic_random_random_1D2N', train_dsrandom1D2N,test_dsrandom1D2N, 'random1D2N', monFunc1D, 'x', 4*10**3, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
   #       
   #  heuristic_random_experiment('singleH_heuristic_random_linear_1D5N', train_dslinear1D5N,test_dslinear1D5N, 'linear1D5N', monFunc1D, 'x', 4*10**3, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
   #  heuristic_random_experiment('singleH_heuristic_random_random_1D5N', train_dsrandom1D5N,test_dsrandom1D5N, 'random1D5N', monFunc1D, 'x', 4*10**3, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
   #      
   #  heuristic_random_experiment('singleH_heuristic_random_linear_1D10N', train_dslinear1D10N,test_dslinear1D10N, 'linear1D10N', monFunc1D, 'x', 4*10**3, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
   #  heuristic_random_experiment('singleH_heuristic_random_random_1D10N', train_dsrandom1D10N,test_dsrandom1D10N, 'random1D10N', monFunc1D, 'x', 4*10**3, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
   #     
   #  heuristic_random_experiment('singleH_heuristic_random_linear_5D2N', train_dslinear5D2N,test_dslinear5D2N, 'linear5D2N', monFunc5D, 'sq(x_0+x_4+x_3)-(x[1]+x[2])', 1*10**6, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
   #  heuristic_random_experiment('singleH_heuristic_random_random_5D2N', train_dsrandom5D2N,test_dsrandom5D2N, 'random5D2N', monFunc5D, 'sq(x_0+x_4+x_3)-(x[1]+x[2])', 1*10**6, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
   #     
   #  heuristic_random_experiment('singleH_heuristic_random_linear_5D5N', train_dslinear5D5N,test_dslinear5D5N, 'linear5D5N', monFunc5D, 'sq(x_0+x_4+x_3)-(x[1]+x[2])', 1*10**6, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
   #  heuristic_random_experiment('singleH_heuristic_random_random_5D5N', train_dsrandom5D5N,test_dsrandom5D5N, 'random5D5N', monFunc5D, 'sq(x_0+x_4+x_3)-(x[1]+x[2])', 1*10**6, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
   # 
   #============================================================================
    heuristic_random_experiment('singleH_heuristic_random_linear_5D10N', train_dslinear5D10N,test_dslinear5D10N, 'linear5D10N', monFunc5D, 'sq(x_0+x_4+x_3)-(x[1]+x[2])', 1*10**6, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
    heuristic_random_experiment('singleH_heuristic_random_random_5D10N', train_dsrandom5D10N,test_dsrandom5D10N, 'random5D10N', monFunc5D, 'sq(x_0+x_4+x_3)-(x[1]+x[2])', 1*10**6, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
   
    heuristic_random_experiment('singleH_heuristic_random_linear_10D2N', train_dslinear10D2N,test_dslinear10D2N, 'linear10D2N', monFunc10D, '((x[0]-x[1]+x[2]-x[3]+x[4]-x[5]+x[6]-x[7]+x[8]-x[9])/10)**2', 1*10**6, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
    heuristic_random_experiment('singleH_heuristic_random_random_10D2N', train_dsrandom10D2N,test_dsrandom10D2N, 'random10D2N', monFunc10D, '((x[0]-x[1]+x[2]-x[3]+x[4]-x[5]+x[6]-x[7]+x[8]-x[9])/10)**2', 1*10**6, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
      
    heuristic_random_experiment('singleH_heuristic_random_linear_10D5N', train_dslinear10D5N,test_dslinear10D5N, 'linear10D5N', monFunc10D, '((x[0]-x[1]+x[2]-x[3]+x[4]-x[5]+x[6]-x[7]+x[8]-x[9])/10)**2', 1*10**6, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
    heuristic_random_experiment('singleH_heuristic_random_random_10D5N', train_dsrandom10D5N,test_dsrandom10D5N, 'random10D5N', monFunc10D, '((x[0]-x[1]+x[2]-x[3]+x[4]-x[5]+x[6]-x[7]+x[8]-x[9])/10)**2', 1*10**6, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
     
    heuristic_random_experiment('singleH_heuristic_random_linear_10D10N', train_dslinear10D10N,test_dslinear10D10N, 'linear10D10N', monFunc10D, '((x[0]-x[1]+x[2]-x[3]+x[4]-x[5]+x[6]-x[7]+x[8]-x[9])/10)**2', 1*10**6, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
    heuristic_random_experiment('singleH_heuristic_random_random_10D10N', train_dsrandom10D10N,test_dsrandom10D10N, 'random10D10N', monFunc10D, '((x[0]-x[1]+x[2]-x[3]+x[4]-x[5]+x[6]-x[7]+x[8]-x[9])/10)**2', 1*10**6, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
   
    #classic optpair experiments
    classic_distOptPair_experiment('singleH_classic_distOptPair_linear_1D2N', train_dslinear1D2N,test_dslinear1D2N, 'linear1D2N', monFunc1D, 'x', 4*10**3, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
    classic_distOptPair_experiment('singleH_classic_distOptPair_random_1D2N', train_dsrandom1D2N,test_dsrandom1D2N, 'random1D2N', monFunc1D, 'x', 4*10**3, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
     
    classic_distOptPair_experiment('singleH_classic_distOptPair_linear_1D5N', train_dslinear1D5N,test_dslinear1D5N, 'linear1D5N', monFunc1D, 'x', 4*10**3, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
    classic_distOptPair_experiment('singleH_classic_distOptPair_random_1D5N', train_dsrandom1D5N,test_dsrandom1D5N, 'random1D5N', monFunc1D, 'x', 4*10**3, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
     
    classic_distOptPair_experiment('singleH_classic_distOptPair_linear_1D10N', train_dslinear1D10N,test_dslinear1D10N, 'linear1D10N', monFunc1D, 'x', 4*10**3, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
    classic_distOptPair_experiment('singleH_classic_distOptPair_random_1D10N', train_dsrandom1D10N,test_dsrandom1D10N, 'random1D10N', monFunc1D, 'x', 4*10**3, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
     
    classic_distOptPair_experiment('singleH_classic_distOptPair_linear_5D2N', train_dslinear5D2N,test_dslinear5D2N, 'linear5D2N', monFunc5D, 'sq(x_0+x_4+x_3)-(x[1]+x[2])', 1*10**6, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
    classic_distOptPair_experiment('singleH_classic_distOptPair_random_5D2N', train_dsrandom5D2N,test_dsrandom5D2N, 'random5D2N', monFunc5D, 'sq(x_0+x_4+x_3)-(x[1]+x[2])', 1*10**6, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
      
    classic_distOptPair_experiment('singleH_classic_distOptPair_linear_5D5N', train_dslinear5D5N,test_dslinear5D5N, 'linear5D5N', monFunc5D, 'sq(x_0+x_4+x_3)-(x[1]+x[2])', 1*10**6, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
    classic_distOptPair_experiment('singleH_classic_distOptPair_random_5D5N', train_dsrandom5D5N,test_dsrandom5D5N, 'random5D5N', monFunc5D, 'sq(x_0+x_4+x_3)-(x[1]+x[2])', 1*10**6, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
  
    classic_distOptPair_experiment('singleH_classic_distOptPair_linear_5D10N', train_dslinear5D10N,test_dslinear5D10N, 'linear5D10N', monFunc5D, 'sq(x_0+x_4+x_3)-(x[1]+x[2])', 1*10**6, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
    classic_distOptPair_experiment('singleH_classic_distOptPair_random_5D10N', train_dsrandom5D10N,test_dsrandom5D10N, 'random5D10N', monFunc5D, 'sq(x_0+x_4+x_3)-(x[1]+x[2])', 1*10**6, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
  
    classic_distOptPair_experiment('singleH_classic_distOptPair_linear_10D2N', train_dslinear10D2N,test_dslinear10D2N, 'linear10D2N', monFunc10D, '((x[0]-x[1]+x[2]-x[3]+x[4]-x[5]+x[6]-x[7]+x[8]-x[9])/10)**2', 1*10**6, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
    classic_distOptPair_experiment('singleH_classic_distOptPair_random_10D2N', train_dsrandom10D2N,test_dsrandom10D2N, 'random10D2N', monFunc10D, '((x[0]-x[1]+x[2]-x[3]+x[4]-x[5]+x[6]-x[7]+x[8]-x[9])/10)**2', 1*10**6, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
     
    classic_distOptPair_experiment('singleH_classic_distOptPair_linear_10D5N', train_dslinear10D5N,test_dslinear10D5N, 'linear10D5N', monFunc10D, '((x[0]-x[1]+x[2]-x[3]+x[4]-x[5]+x[6]-x[7]+x[8]-x[9])/10)**2', 1*10**6, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
    classic_distOptPair_experiment('singleH_classic_distOptPair_random_10D5N', train_dsrandom10D5N,test_dsrandom10D5N, 'random10D5N', monFunc10D, '((x[0]-x[1]+x[2]-x[3]+x[4]-x[5]+x[6]-x[7]+x[8]-x[9])/10)**2', 1*10**6, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
     
    classic_distOptPair_experiment('singleH_classic_distOptPair_linear_10D10N', train_dslinear10D10N,test_dslinear10D10N, 'linear10D10N', monFunc10D, '((x[0]-x[1]+x[2]-x[3]+x[4]-x[5]+x[6]-x[7]+x[8]-x[9])/10)**2', 1*10**6, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
    classic_distOptPair_experiment('singleH_classic_distOptPair_random_10D10N', train_dsrandom10D10N,test_dsrandom10D10N, 'random10D10N', monFunc10D, '((x[0]-x[1]+x[2]-x[3]+x[4]-x[5]+x[6]-x[7]+x[8]-x[9])/10)**2', 1*10**6, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)

    #heuristic optpair experiments
    heuristic_distOptPair_experiment('singleH_heuristic_distOptPair_linear_1D2N', train_dslinear1D2N,test_dslinear1D2N, 'linear1D2N', monFunc1D, 'x', 4*10**3, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
    heuristic_distOptPair_experiment('singleH_heuristic_distOptPair_random_1D2N', train_dsrandom1D2N,test_dsrandom1D2N, 'random1D2N', monFunc1D, 'x', 4*10**3, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
     
    heuristic_distOptPair_experiment('singleH_heuristic_distOptPair_linear_1D5N', train_dslinear1D5N,test_dslinear1D5N, 'linear1D5N', monFunc1D, 'x', 4*10**3, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
    heuristic_distOptPair_experiment('singleH_heuristic_distOptPair_random_1D5N', train_dsrandom1D5N,test_dsrandom1D5N, 'random1D5N', monFunc1D, 'x', 4*10**3, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
     
    heuristic_distOptPair_experiment('singleH_heuristic_distOptPair_linear_1D10N', train_dslinear1D10N,test_dslinear1D10N, 'linear1D10N', monFunc1D, 'x', 4*10**3, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
    heuristic_distOptPair_experiment('singleH_heuristic_distOptPair_random_1D10N', train_dsrandom1D10N,test_dsrandom1D10N, 'random1D10N', monFunc1D, 'x', 4*10**3, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
     
    heuristic_distOptPair_experiment('singleH_heuristic_distOptPair_linear_5D2N', train_dslinear5D2N,test_dslinear5D2N, 'linear5D2N', monFunc5D, 'sq(x_0+x_4+x_3)-(x[1]+x[2])', 1*10**6, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
    heuristic_distOptPair_experiment('singleH_heuristic_distOptPair_random_5D2N', train_dsrandom5D2N,test_dsrandom5D2N, 'random5D2N', monFunc5D, 'sq(x_0+x_4+x_3)-(x[1]+x[2])', 1*10**6, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
      
    heuristic_distOptPair_experiment('singleH_heuristic_distOptPair_linear_5D5N', train_dslinear5D5N,test_dslinear5D5N, 'linear5D5N', monFunc5D, 'sq(x_0+x_4+x_3)-(x[1]+x[2])', 1*10**6, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
    heuristic_distOptPair_experiment('singleH_heuristic_distOptPair_random_5D5N', train_dsrandom5D5N,test_dsrandom5D5N, 'random5D5N', monFunc5D, 'sq(x_0+x_4+x_3)-(x[1]+x[2])', 1*10**6, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
  
    heuristic_distOptPair_experiment('singleH_heuristic_distOptPair_linear_5D10N', train_dslinear5D10N,test_dslinear5D10N, 'linear5D10N', monFunc5D, 'sq(x_0+x_4+x_3)-(x[1]+x[2])', 1*10**6, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
    heuristic_distOptPair_experiment('singleH_heuristic_distOptPair_random_5D10N', train_dsrandom5D10N,test_dsrandom5D10N, 'random5D10N', monFunc5D, 'sq(x_0+x_4+x_3)-(x[1]+x[2])', 1*10**6, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
  
    heuristic_distOptPair_experiment('singleH_heuristic_distOptPair_linear_10D2N', train_dslinear10D2N,test_dslinear10D2N, 'linear10D2N', monFunc10D, '((x[0]-x[1]+x[2]-x[3]+x[4]-x[5]+x[6]-x[7]+x[8]-x[9])/10)**2', 1*10**6, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
    heuristic_distOptPair_experiment('singleH_heuristic_distOptPair_random_10D2N', train_dsrandom10D2N,test_dsrandom10D2N, 'random10D2N', monFunc10D, '((x[0]-x[1]+x[2]-x[3]+x[4]-x[5]+x[6]-x[7]+x[8]-x[9])/10)**2', 1*10**6, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
     
    heuristic_distOptPair_experiment('singleH_heuristic_distOptPair_linear_10D5N', train_dslinear10D5N,test_dslinear10D5N, 'linear10D5N', monFunc10D, '((x[0]-x[1]+x[2]-x[3]+x[4]-x[5]+x[6]-x[7]+x[8]-x[9])/10)**2', 1*10**6, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
    heuristic_distOptPair_experiment('singleH_heuristic_distOptPair_random_10D5N', train_dsrandom10D5N,test_dsrandom10D5N, 'random10D5N', monFunc10D, '((x[0]-x[1]+x[2]-x[3]+x[4]-x[5]+x[6]-x[7]+x[8]-x[9])/10)**2', 1*10**6, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
     
    heuristic_distOptPair_experiment('singleH_heuristic_distOptPair_linear_10D10N', train_dslinear10D10N,test_dslinear10D10N, 'linear10D10N', monFunc10D, '((x[0]-x[1]+x[2]-x[3]+x[4]-x[5]+x[6]-x[7]+x[8]-x[9])/10)**2', 1*10**6, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
    heuristic_distOptPair_experiment('singleH_heuristic_distOptPair_random_10D10N', train_dsrandom10D10N,test_dsrandom10D10N, 'random10D10N', monFunc10D, '((x[0]-x[1]+x[2]-x[3]+x[4]-x[5]+x[6]-x[7]+x[8]-x[9])/10)**2', 1*10**6, repeats=3, wl=200, wr=0, approxorder=3,tolerance=tolerance)
    
