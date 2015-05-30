'''
@author: ak
'''
import networkx as nx

class OptimalPairer:
    '''
    class implementing optimal pairing as in paper Geometric Monitoring of Heterogeneous Streams
    '''
    
    def __init__(self,nodes,threshold=None):
        '''
        constructor
        args:
            @param nodes: list of node instances
            @param threshold: to compute edge weights for max_weight_matching, i.e. compute cdf(threshold) 
        '''
        self.nodes=nodes
        self.threshold=threshold
        
        self.typeDict={} #contains optimal pairings {n:{(id1, id2, ...idn):(idk,....idz)}}
        
        if self.threshold:
            self.optimize([(n,) for n in self.nodes.keys()])
        
    
    def optimize(self,nodes,threshold=None):
        '''
        builds optimization tree/dictionary
        args:
            @param nodes: list of node tuples
            @param threshold: cdf threshold as weights
        
        @return: typeDict dictionary of pairings OR None at fail
        '''
        if not threshold and self.threshold:
            threshold=self.threshold
        else:
            print("OptimalPairer:no threshold set")
            return None
        
        #recursion finish
        if len(nodes)==1:
            return self.typeDict
        
        #create complete Graph
        g=nx.complete_graph(len(nodes))
        
        #assign actual nodeIds and distribution data to graph
        nx.relabel_nodes(g, mapping=dict(zip(range(len(nodes)),nodes)), copy=False)
        for n in g.nodes():
            g[n]['distr']=self._computeAvgDistr(n)
         
        #add edge weights
        for (i,j) in g.edges():
            g[i][j]['weight']=self._computeCdfWeight(g.node[i]["distr"],threshold)
        
        #max weight matching
        pairs=nx.max_weight_matching(g, maxcardinality=True)
        
        #store type i pairs
        self.typeDict[len(pairs.keys()[0])]=pairs
        
        #recurse
        self.optimize([n+pairs[n] for n in pairs.keys()], threshold)
        
        
    def _computeAvgDistr(self,nodes):
        '''
        args:
            @param nodes: iterable of nodes
        
        @return tuple (mean, std) 
        '''