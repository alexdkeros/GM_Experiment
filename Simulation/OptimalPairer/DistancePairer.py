'''
@author: ak
'''
import pandas as pd
import scipy as sp
import scipy.linalg as linalg
import networkx as nx
import Simulation.Utilities.ArrayOperations as ArrayOp
from Simulation.OptimalPairer.OptimalPairer import OptimalPairer
import itertools

class DistancePairer(OptimalPairer):
    '''
    node optimal pairing based on distance criteria
    '''
    def __init__(self, dataset, nodeWeightDict, monFunc):
        '''
        constructor
        see OptimalPairer Base class
        args:
            @param dataset: training dataset as Pandas Panel with NodeIds as Items
                                                Updates as Major_Column
                                                Update types as Minor_Column
            @param nodeWeightDict: dictionary of node weights {id:w, }
            @param monFunc: the monitoring function
        '''
        OptimalPairer.__init__(dataset)
        
        self.monFunc=monFunc
        self.nodeWeightDict=nodeWeightDict
        #optimization procedure
        self.globalMean=ArrayOp.computeMean(self.dataset, self.nodeWeightDict)
        self.typeDict=self.__optimize([frozenset([n]) for n in self.dataset.items])
        
    
    '''
    ----------------------------------------------
    optimizing helper functions
    ----------------------------------------------
    '''
    def __computeWeight(self,nodes):
        '''
        compute weight based on mean distance from global mean and im between distance of nodes
        args:
            @param nodes:list of nodes for which to compute weight
        @return weight
        '''
        #mean of node subset
        subsetMean=ArrayOp.computeMean(self.dataset.loc[nodes,:,:], weightDict=self.weightDict)
        
        #cumulative distance of node subset
        cumDist=[sum(linalg.norm(self.dataset.loc[it1,i,:]-self.dataset.loc[it2,i,:])
                for it1,it2 in itertools.combinations(nodes,2)) for i in self.dataset.major_axis]
        
        weight=sum(-abs(self.globalMean.apply(self.monFunc, axis=1)-subsetMean.apply(self.monFunc, axis=1))+cumDist)
        
        return weight
        


    
    '''
    ----------------------------------------------
    main function: OPTIMIZER
    ----------------------------------------------
    '''
    def __optimize(self,nodeSetCollection):
        '''
        main optimizing function using distance criteria
        a.distance of mean of node pair from the global mean
        b.distance of node updates
        args:
            @param nodeSetCollection: node set collection to optimally pair, taken from self.dataset.items 
        @return: typeDict dictionary of pairings
        '''
        #----recursion finish, all nodes grouped together
        if len(nodeSetCollection)==1:
            self.typeDict[len(nodeSetCollection[0])]=nodeSetCollection[0]
            return self.typeDict
        
        #----recursion operation, graph and weight maximal matching
        #create complete Graph
        g=nx.complete_graph(len(nodeSetCollection))
        
        #assign actual nodeIds to graph
        nx.relabel_nodes(g, mapping=dict(zip(range(len(nodeSetCollection)),nodeSetCollection)), copy=False)
        
        #add edge weights
        for (i,j) in g.edges():
            g[i][j]['weight']=self.__computeWeight(list(i.union(j)))
            self.weightDict[i.union(j)]=g[i][j]['weight']
            
        #max weight matching
        pairs=nx.max_weight_matching(g, maxcardinality=True)
        
        #store type i pairs
        self.typeDict[len(pairs.keys()[0])]=pairs
            
        #recurse
        self.__optimize(list(set(n.union(pairs[n]) for n in pairs.keys())))
    