'''
@author: ak
'''
import itertools
import pandas as pd
import scipy as sp
import networkx as nx
from scipy import math

class OptimalPairer:
    '''
    Geometric Monitoring
    base class for node optimal pairing for balancing reasons
    '''
    def __init__(self, dataset):
        '''
        Constructor
        args:
            @param dataset: training dataset as Pandas Panel with NodeIds as Items
                                                Updates as Major_Column
                                                Update types as Minor_Column
        '''
        self.dataset=dataset
        
        self.typeDict={}  #contains optimal pairings {n:{(id1, id2, ...idn):(idk,....idz), ... }, ... }
        self.weightDict={} #contains computed weights {(id1,id2):w_12, ...}
    
    '''
    ----------------------------------------------
    getters
    ----------------------------------------------
    '''
    def getTypeDict(self):
        '''
        @return dictionary of pairs by type
        '''
        return self.typeDict
    
    def getWeightDict(self):
        '''
        @return dictionary of pair weights
        '''
        return self.weightDict
    
    def getOptPairing(self, nodes):
        '''
        args:
            @param nodes: set of nodeIds, length equals to pairing type
        @return set with optimal pair or None
        '''
        if len(nodes) in self.typeDict:
            if frozenset(nodes) in self.typeDict[len(nodes)]:
                diffSet=set(self.typeDict[len(nodes)][frozenset(nodes)])-nodes
                if diffSet:
                    return diffSet
                else:
                    return None
        return None
    
    def getOptPairingfromSubset(self,nodes):
        '''
        args:
            @param nodes: set of nodeIds
        @param set with optimal pair of whole set or union of matching subsets, or None
        '''
        t=2**int(math.log(len(nodes),2)/1)
        
        retSet=self.getOptPairingOfTypeFromSet(t, nodes)
        
        while not retSet:
            t=t/2
            
            if not t:
                return None
            
            retSet=self.getOptPairingOfTypeFromSet(t, nodes)
        
        return retSet
            
            
            
    def getOptPairingOfTypeFromSet(self,t,s):
        '''
        args:
            @param t: type number ( i.e. 1,2,4,8,16,... )
            @param s: starting set
        @return set with optimal pair
        '''
        l=set()
        for el in set(itertools.combinations(s,t)):
            if frozenset(list(el)) in self.typeDict[t]:
                l=l.union(self.typeDict[t][frozenset(list(el))])
        return set(l-s)
    
    '''
    ----------------------------------------------
    main function: OPTIMIZER
    ----------------------------------------------
    '''
    def __optimize(self):
        '''
        main optimizing function setting things up
        @return: typeDict dictionary of pairings OR None at fail
        '''
        raise NotImplementedError
    
    '''
    ----------------------------------------------
    optimizing helper functions
    ----------------------------------------------
    '''
    def __computeWeight(self,nodes):
        '''
        weight computation Function
        args:
            @param nodes: nodeIds set to compute weight
        @return pairing weight
        '''
        raise NotImplementedError