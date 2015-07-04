'''
@author: ak
'''
import networkx as nx
import numpy as np
from scipy.stats import norm
from GM_Exp.Util import Utils
import itertools

class OptimalPairerWDistr:
    '''
    class implementing optimal pairing as in paper Geometric Monitoring of Heterogeneous Streams
    '''
    
    def __init__(self,nodes=None,threshold=None):
        '''
        constructor
        args:
            @param nodes: dictionary of {nodeId: (mean,std)}
            @param threshold: to compute edge weights for max_weight_matching, i.e. compute cdf(threshold) 
        '''
        self.nodes=nodes
        self.threshold=threshold
        
        self.typeDict={} #contains optimal pairings {n:{(id1, id2, ...idn):(idk,....idz)}}
        self.distrDict={}
        

        
    '''
    --------------getters
    '''
    def getTypeDict(self):
        '''
        @return dictionary of pairs by type
        '''
        return self.typeDict
    
    def getDistrDict(self):
        '''
        @return dictionary of distributions
        '''
        return self.distrDict
    
    
    def getOptPairing(self, nodes):
        '''
        args:
            @param nodes: set of nodeIds, length equals to pairing type
        @return list with optimal pair
        '''
        if len(nodes) in self.typeDict:
            if frozenset(nodes) in self.typeDict[len(nodes)]:
                return self.typeDict[len(nodes)][frozenset(nodes)]
        return None
    
    def getOptPairingOfTypeFromSet(self,t,s):
        '''
        args:
            @param t: type number ( i.e. 1,2,4,8,16,... )
            @param s: starting set
        @return list with optimal pair
        '''
        l=set()
        for el in set(itertools.combinations(s,t)):
            if frozenset(list(el)) in self.typeDict[t]:
                l=l.union(self.typeDict[t][frozenset(list(el))])
        return l-s
            
    
    '''
    --------------main function: OPTIMIZER
    '''
    def optimize(self,nodes=None,threshold=None):
        '''
        constructor
        args:
            @param nodes: dictionary of {nodeId: (mean,std)} 
            @param threshold: to compute edge weights for max_weight_matching, i.e. compute cdf(threshold) 
        @return: typeDict dictionary of pairings OR None at fail
        '''
        if nodes:
            self.nodes=nodes
        if threshold:
            self.threshold=threshold
            
        #DBG
        #print("OPTIMAL PAIRER: DISTRIBUTIONS")
        #print(self.nodes)
        
        if self.threshold and self.nodes:
            return self._optimize([frozenset([n]) for n in self.nodes.keys()],self.threshold)
            
            
    def _optimize(self,nodes,threshold=None):
        '''
        builds optimization tree/dictionary, recursive func
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
            self.typeDict[len(nodes[0])]=nodes[0]
            return self.typeDict
        
        #create complete Graph
        g=nx.complete_graph(len(nodes))
        
        #assign actual nodeIds and distribution data to graph
        nx.relabel_nodes(g, mapping=dict(zip(range(len(nodes)),nodes)), copy=False)
        for n in g.nodes():
            g.node[n]['distr']=self._computeAvgDistr(n)
            self.distrDict[n]=g.node[n]['distr']
         
        #DBG
        #print("!!!NODES!!!")
        #print(g.nodes(data=True))
        
        #add edge weights
        for (i,j) in g.edges():
            g[i][j]['weight']=self._computeCdfWeight(self._computeAvgDistr(list(i.union(j))),threshold)
        
        #DBG
        #print("!!!EDGES!!!")
        #print(g.edges(data=True))
        
        #max weight matching
        pairs=nx.max_weight_matching(g, maxcardinality=True)
        
        #store type i pairs
        self.typeDict[len(pairs.keys()[0])]=pairs
        
        #recurse
        self._optimize(list(set(n.union(pairs[n]) for n in pairs.keys())), threshold)
    
    '''
    --------------Helper functions
    '''    
        
    def _computeAvgDistr(self,nodes):
        '''
        args:
            @param nodes: iterable of nodes
        
        @return tuple (mean, std) 
        '''
        m=Utils.deDec(sum([self.nodes[node][0] for node in nodes])/Utils.dec(len(nodes)))
        std=Utils.deDec(np.sqrt(sum([Utils.dec(self.nodes[node][1])**2 for node in nodes])/(Utils.dec(len(nodes))**2)))
        
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
    
    





'''
---------------------------------------------DATA UPDATE OPTIMAL PAIRER------------------------------------------------
'''




class OptimalPairerWDataUpdates:
    '''
    class implementing optimal pairing as in paper Geometric Monitoring of Heterogeneous Streams
    '''
    
    def __init__(self,nodes=None, threshold=None,func=None):
        '''
        constructor
        args:
            @param nodes: dictionary of {nodeId: data updates}
            @param threshold: to compute edge weights for max_weight_matching, i.e. compute cdf(threshold) 
            @param func: function of data to respect threshold

        '''
        self.nodes=nodes
        self.threshold=threshold
        self.func=func
        self.globalMean=[]
        
        self.typeDict={} #contains optimal pairings {n:{(id1, id2, ...idn):(idk,....idz)}}
        self.percentageDict={}
        
        
    '''
    --------------getters
    '''
    def getTypeDict(self):
        '''
        @return dictionary of pairs by type
        '''
        return self.typeDict
    
    def getPercentageDict(self):
        '''
        @return dictionary of distributions
        '''
        return self.percentageDict
    
    
    def getOptPairing(self, nodes):
        '''
        args:
            @param nodes: set of nodeIds, length equals to pairing type
        @return list with optimal pair
        '''
        if len(nodes) in self.typeDict:
            if frozenset(nodes) in self.typeDict[len(nodes)]:
                return self.typeDict[len(nodes)][frozenset(nodes)]
        return None
    
    def getOptPairingOfTypeFromSet(self,t,s):
        '''
        args:
            @param t: type number ( i.e. 1,2,4,8,16,... )
            @param s: starting set
        @return list with optimal pair
        '''
        l=set()
        for el in set(itertools.combinations(s,t)):
            if frozenset(list(el)) in self.typeDict[t]:
                l=l.union(self.typeDict[t][frozenset(list(el))])
        return l-s
    '''
    --------------main function: OPTIMIZER
    '''
    def optimize(self,nodes=None,threshold=None,func=None):
        '''
        constructor
        args:
            @param nodes: dictionary of {nodeId: data updates} 
            @param threshold: to compute edge weights for max_weight_matching, i.e. compute cdf(threshold) 
            @param func: function of data to respect threshold

        @return: typeDict dictionary of pairings OR None at fail
        '''
        
        if nodes:
            self.nodes=nodes
        if threshold:
            self.threshold=threshold
        if func:
            self.func=func
             
        if not self.globalMean:
            dataTups=zip(*[self.nodes[n] for n in nodes])
            self.globalMean=[np.mean(t) for t in dataTups]
            #DBG
            #print("GLOBAL MEAN COMPUTATION")
            #print(self.globalMean)
        if self.threshold and self.nodes and self.func:
            return self._optimize([frozenset([n]) for n in self.nodes.keys()],self.threshold,self.func)
        else:
            return None
            
    def _optimize(self,nodes,threshold=None,func=None):
        '''
        builds optimization tree/dictionary, recursive func
        args:
            @param nodes: list of node sets
            @param threshold: cdf threshold as weights
            @param func: function of data to respect threshold
        
        @return: typeDict dictionary of pairings OR None at fail
        '''
        #DBG
        #print nodes
        
        if not threshold and self.threshold:
            threshold=self.threshold
        if not func and self.func:
            func=self.func
        
        #recursion finish
        if len(nodes)==1:
            self.typeDict[len(nodes[0])]=nodes[0]
            return self.typeDict
        
        #create complete Graph
        g=nx.complete_graph(len(nodes))
        
        #assign actual nodeIds and distribution data to graph
        nx.relabel_nodes(g, mapping=dict(zip(range(len(nodes)),nodes)), copy=False)
         
        #DBG
        #print("!!!NODES!!!")
        #print(g.nodes(data=True))
        
        #add edge weights
        for (i,j) in g.edges():
            g[i][j]['weight']=self._computePercentageWeight(list(i.union(j)),threshold,func)
            self.percentageDict[i.union(j)]=g[i][j]['weight']
        
        #DBG
        #print("!!!EDGES!!!")
        #print(g.edges(data=True))
        
        #max weight matching
        pairs=nx.max_weight_matching(g, maxcardinality=True)
        
        #store type i pairs
        self.typeDict[len(pairs.keys()[0])]=pairs
        
        #recurse
        self._optimize(list(set(n.union(pairs[n]) for n in pairs.keys())), threshold,func)
    
    '''
    --------------Helper functions
    '''    
    
    def _computePercentageWeight(self,nodes,thresh,func):
        '''
        args:
            @param nodes: list of nodes
            @param thresh: P(f(x)<=thresh)
            @param func: function f()
            
        @return P(f(X)<=thresh)
        '''
        z=zip(*[self.nodes[n] for n in nodes])
        counter=0.0
        for i in range(len(z)):
            if func(np.mean(z[i]))<thresh:
                #DBG
                #print("in Func: Qualifying %f"%func(np.mean(t)))
                #print(t)
                counter+=(-abs(Utils.deDec(func(self.globalMean[i]))-Utils.deDec(func(np.mean(z[i])))))
        #DBG
        '''
        print("OPTIMAL PAIRER PERCENTAGE COMPUTATION:")
        print(z)
        print(nodes)
        print("Counter Val:%f"%counter)
        print("Normalized Counter Val:%f"%(counter/float(len(z))))
        '''
        return counter/float(len(z))









    





'''
---------------------------------------------WEIGHTED DATA UPDATE OPTIMAL PAIRER------------------------------------------------
'''




class WeightedOptimalPairerWDataUpdates:
    '''
    class implementing optimal pairing as in paper Geometric Monitoring of Heterogeneous Streams
    '''
    
    def __init__(self,nodes=None, threshold=None,func=None):
        '''
        constructor
        args:
            @param nodes: dictionary of {nodeId: data updates}
            @param threshold: to compute edge weights for max_weight_matching, i.e. compute cdf(threshold) 
            @param func: function of data to respect threshold

        '''
        self.nodes=nodes
        self.threshold=threshold
        self.func=func
        self.globalMean=[]
        self.normalizer=1
        self.typeDict={} #contains optimal pairings {n:{(id1, id2, ...idn):(idk,....idz)}}
        self.percentageDict={}
        
        
    '''
    --------------getters
    '''
    def getTypeDict(self):
        '''
        @return dictionary of pairs by type
        '''
        return self.typeDict
    
    def getPercentageDict(self):
        '''
        @return dictionary of distributions
        '''
        return self.percentageDict
    
    
    def getOptPairing(self, nodes):
        '''
        args:
            @param nodes: set of nodeIds, length equals to pairing type
        @return list with optimal pair
        '''
        if len(nodes) in self.typeDict:
            if frozenset(nodes) in self.typeDict[len(nodes)]:
                return self.typeDict[len(nodes)][frozenset(nodes)]
        return None
    
    def getOptPairingOfTypeFromSet(self,t,s):
        '''
        args:
            @param t: type number ( i.e. 1,2,4,8,16,... )
            @param s: starting set
        @return list with optimal pair
        '''
        l=set()
        for el in set(itertools.combinations(s,t)):
            if frozenset(list(el)) in self.typeDict[t]:
                l=l.union(self.typeDict[t][frozenset(list(el))])
        return l-s
    '''
    --------------main function: OPTIMIZER
    '''
    def optimize(self,nodes=None,threshold=None,func=None):
        '''
        constructor
        args:
            @param nodes: dictionary of {nodeId: data updates} 
            @param threshold: to compute edge weights for max_weight_matching, i.e. compute cdf(threshold) 
            @param func: function of data to respect threshold

        @return: typeDict dictionary of pairings OR None at fail
        '''
        
        if nodes:
            self.nodes=nodes
        if threshold:
            self.threshold=threshold
        if func:
            self.func=func
             
        if not self.globalMean:
            dataTups=zip(*[self.nodes[n] for n in nodes])
            self.globalMean=[np.mean(t) for t in dataTups]
            #DBG
            #print("GLOBAL MEAN COMPUTATION")
            #print(self.globalMean)
        if self.threshold and self.nodes and self.func:
            return self._optimize([frozenset([n]) for n in self.nodes.keys()],self.threshold,self.func)
        else:
            return None
            
    def _optimize(self,nodes,threshold=None,func=None):
        '''
        builds optimization tree/dictionary, recursive func
        args:
            @param nodes: list of node sets
            @param threshold: cdf threshold as weights
            @param func: function of data to respect threshold
        
        @return: typeDict dictionary of pairings OR None at fail
        '''
        #DBG
        #print nodes
        
        if not threshold and self.threshold:
            threshold=self.threshold
        if not func and self.func:
            func=self.func
        
        #recursion finish
        if len(nodes)==1:
            self.typeDict[len(nodes[0])]=nodes[0]
            return self.typeDict
        
        #create complete Graph
        g=nx.complete_graph(len(nodes))
        
        #assign actual nodeIds and distribution data to graph
        nx.relabel_nodes(g, mapping=dict(zip(range(len(nodes)),nodes)), copy=False)
         
        #DBG
        #print("!!!NODES!!!")
        #print(g.nodes(data=True))
        
        #add edge weights
        for (i,j) in g.edges():
            g[i][j]['weight']=self._computePercentageWeight(list(i.union(j)),threshold,func)
            self.percentageDict[i.union(j)]=g[i][j]['weight']
        
        #DBG
        #print("!!!EDGES!!!")
        #print(g.edges(data=True))
        
        #max weight matching
        pairs=nx.max_weight_matching(g, maxcardinality=True)
        
        #store type i pairs
        self.typeDict[len(pairs.keys()[0])]=pairs
        
        #recurse
        self._optimize(list(set(n.union(pairs[n]) for n in pairs.keys())), threshold,func)
    
    '''
    --------------Helper functions
    '''    
    
    def _computePercentageWeight(self,nodes,thresh,func):
        '''
        args:
            @param nodes: list of nodes
            @param thresh: P(f(x)<=thresh)
            @param func: function f()
            
        @return P(f(X)<=thresh)
        '''
        z=zip(*[self.nodes[n] for n in nodes])
        counter=0.0
        for i in range(len(z)):
            #if func(np.mean(z[i]))<thresh:
                #DBG
                #print("in Func: Qualifying %f"%func(np.mean(t)))
                #print(t)
            w=0
            ps=list(itertools.combinations(set(z[i]),2))
            for j in ps:
                w+=abs(j[0]-j[1])
            counter+=(-abs(Utils.deDec(func(self.globalMean[i]))-Utils.deDec(func(np.mean(z[i])))))+Utils.deDec(w/self.normalizer)
        #DBG
        '''
        print("OPTIMAL PAIRER PERCENTAGE COMPUTATION:")
        print(z)
        print(nodes)
        print("Counter Val:%f"%counter)
        print("Normalized Counter Val:%f"%(counter/float(len(z))))
        '''
        return counter/float(len(z))    
if __name__=="__main__":
    #run test - OK
    thresh=100
    #dummy node dictionary
    #print("----------------- DISTRIBUTION OPTIMAL PAIRER ------------------------------")
    nodeDict={"n0":(100,3),
              "n1":(90,5),
              "n2":(0,4),
              "n3":(6,1)
              }
    '''
              "n4":(1,10),
              "n5":(8,2),
              "n6":(4,2),
              "n7":(0,0.1)
    '''
    
    #print(nodeDict)
    '''
    o=OptimalPairerWDistr(nodeDict, thresh)
    o.optimize(nodeDict, thresh)
    d=o.getTypeDict()
    for ty in d.keys():
        print("Type: %d"%ty)
        print(d[ty])
    print("--------------")
    di=o.getDistrDict()
    
    for n in di:
        print("Node: %s"%str(n))
        print(di[n])
        print(norm(di[n][0],di[n][1]).cdf(thresh))
    '''
    
    print("-----------------WEIGHTED DATA UPDATES OPTIMAL PAIRER ------------------------------")
    import pickle
    from GM_Exp.Util.Plotter import multiplePlots2d
    dataSet=pickle.load(open("/home/ak/workspace/GM_Experiment/Experiments/datasets/DATASET_l-1_n-5_m-5_std-5.p","rb"))
    nodeDict2={}
    for i in range(dataSet["streams"]):
        nodeDict2["n"+str(i)]=dataSet["updates"][i]
        
    sortedKeys=list(d for d in nodeDict2)
    sortedKeys.sort()
    #updates detailed
    multiplePlots2d([np.arange(10)]*dataSet["streams"],
                    [nodeDict2[d][0:10] for d in sortedKeys],
                    labels=sortedKeys,
                    xLabel="iterations",
                    yLabel="update",
                    saveFlag=True,
                    filename="/home/ak/workspace/GM_Experiment/ups",
                    showFlag=False)
    
    f=lambda x:x
    o=WeightedOptimalPairerWDataUpdates(nodeDict2,thresh,f)
    o.optimize(nodeDict2,thresh,f)
    d=o.getTypeDict()
    for t in d:
        print("Type: %d"%t)
        print(d[t])
    
    