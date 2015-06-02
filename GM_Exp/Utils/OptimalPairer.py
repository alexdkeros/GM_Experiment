'''
@author: ak
'''
import networkx as nx
import numpy as np
from scipy.stats import norm

class OptimalPairer:
    '''
    class implementing optimal pairing as in paper Geometric Monitoring of Heterogeneous Streams
    '''
    
    def __init__(self,nodes,threshold=None):
        '''
        constructor
        args:
            @param nodes: dictionary of {nodeId: (mean,std)}
            @param threshold: to compute edge weights for max_weight_matching, i.e. compute cdf(threshold) 
        '''
        self.nodes=nodes
        self.threshold=threshold
        
        self.typeDict={} #contains optimal pairings {n:{(id1, id2, ...idn):(idk,....idz)}}
        
        if self.threshold:
            self.optimize([frozenset([n]) for n in self.nodes.keys()])
        
    '''
    --------------getters
    '''
    def getTypeDict(self):
        '''
        @return dictionary of pairs by type
        '''
        return self.typeDict
    
    def getOptPairing(self, nodes):
        '''
        args:
            @param nodes: set of nodeIds, length equals to pairing type
        '''
        return self.typeDict[len(nodes)][nodes]
    
    '''
    --------------main function: OPTIMIZER
    '''
    def optimize(self,nodes,threshold=None):
        '''
        builds optimization tree/dictionary
        args:
            @param nodes: list of node sets
            @param threshold: cdf threshold as weights
        
        @return: typeDict dictionary of pairings OR None at fail
        '''
        #DBG
        #print nodes
        
        if not threshold and self.threshold:
            threshold=self.threshold
        
        #recursion finish
        if len(nodes)==1:
            self.typeDict[len(nodes[0])]=nodes
            return self.typeDict
        
        #create complete Graph
        g=nx.complete_graph(len(nodes))
        
        #assign actual nodeIds and distribution data to graph
        nx.relabel_nodes(g, mapping=dict(zip(range(len(nodes)),nodes)), copy=False)
        for n in g.nodes():
            g.node[n]['distr']=self._computeAvgDistr(n)
         
        #DBG
        #print(g.nodes(data=True))
        
        #add edge weights
        for (i,j) in g.edges():
            g[i][j]['weight']=self._computeCdfWeight(g.node[i]['distr'],threshold)
        
        #max weight matching
        pairs=nx.max_weight_matching(g, maxcardinality=True)
        
        #store type i pairs
        self.typeDict[len(pairs.keys()[0])]=pairs
        
        #recurse
        self.optimize(list(set(n.union(pairs[n]) for n in pairs.keys())), threshold)
    
    '''
    --------------Helper functions
    '''    
        
    def _computeAvgDistr(self,nodes):
        '''
        args:
            @param nodes: iterable of nodes
        
        @return tuple (mean, std) 
        '''
        m=np.mean([self.nodes[node][0] for node in nodes])
        std=np.sqrt(sum([self.nodes[node][1]**2 for node in nodes])/float(len(nodes)))
        
        return (m,std)
        
    def _computeCdfWeight(self,distr,thresh):
        '''
        args:
            @param distr: tuple (mean, std)
            @param thresh: P(x<=thresh)
            
        @return P(X<=thresh)
        '''
        d=norm(distr[0], distr[1])
        return d.cdf(thresh)
    
if __name__=="__main__":
    #run test - OK
    #dummy node dictionary
    nodeDict={"n0":(2,3),
              "n1":(2,5),
              "n2":(0,4),
              "n3":(6,1),
              "n4":(1,10),
              "n5":(8,2),
              "n6":(4,2),
              "n7":(0,0.1)}
    print(nodeDict)
    o=OptimalPairer(nodeDict, 8)
    d=o.getTypeDict()
    for ty in d.keys():
        print("Type: %d"%ty)
        print(d[ty])