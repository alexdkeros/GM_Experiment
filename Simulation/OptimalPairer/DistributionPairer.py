'''
@author: ak
'''
import networkx as nx
from scipy.stats import norm
from Simulation.OptimalPairer.OptimalPairer import OptimalPairer


class DistributionPairer(OptimalPairer):
    '''
    node optimal pairing based on distribution criteria
    '''
    def __init__(self, dataset, monFunc, threshold):
        '''
        constructor
        see OptimalPairer Base Class
        args:
            @param dataset: training dataset as Pandas Panel with NodeIds as Items
                                                Updates as Major_Column
                                                Update types as Minor_Column
            @param monFunc: the monitoring function
            @param threshold: f(x)<=threshold
        '''
        OptimalPairer.__init__(self,dataset)
        
        self.monFunc=monFunc
        self.threshold=threshold
        
        self.distrDict={}   #distribution data dictionary
        
        #optimization procedure
        self.typeDict=self.__optimize([frozenset([n]) for n in self.dataset.items])
    
    '''
    ----------------------------------------------
    optimizing helper functions
    ----------------------------------------------
    '''
    def __computeAvgFuncDistr(self,nodes):
        '''
        args:
            @param nodes: pandas of training dataset
        
        @return tuple (mean, std) 
        '''
        fval=self.dataset.loc[nodes,:,:].mean(axis=0).apply(self.monFunc,axis=1)
        
        return (fval.mean(), fval.std())
   
    def __computeWeight(self,distr):
        '''
        args:
            @param distr: tuple (mean, std)            
        @return P(X<=thresh)
        '''
        d=norm(distr[0], distr[1])
        return d.cdf(self.threshold)
    
    
    
    '''
    ----------------------------------------------
    main function: OPTIMIZER
    ----------------------------------------------
    '''
    def __optimize(self,nodeSetCollection):
        '''
        main optimizing function using distribution criteria
        i.e. P(f(x))<=T
        args:
            @param nodeSetCollection: node set collection to optimally pair, taken from self.dataset.items 
        @return: typeDict dictionary of pairings
        '''
        
        #----recursion finish, all nodes grouped together
        if len(nodeSetCollection)==1:
            self.typeDict[len(nodeSetCollection[0])]={nodeSetCollection[0]:nodeSetCollection[0]}
            
            return self.typeDict
        
        #----recursion operation, graph and weight maximal matching
        #create complete Graph
        g=nx.complete_graph(len(nodeSetCollection))
        
        #assign actual nodeIds to graph
        nx.relabel_nodes(g, mapping=dict(zip(range(len(nodeSetCollection)),nodeSetCollection)), copy=False)
            
        #add edge weights
        for (i,j) in g.edges():
            g[i][j]['weight']=self.__computeWeight(self.__computeAvgFuncDistr(list(i.union(j))))
            self.weightDict[i.union(j)]=g[i][j]['weight']

        #max weight matching
        pairs=nx.max_weight_matching(g, maxcardinality=True)
        
        
        #store type i pairs
        self.typeDict[len(pairs.keys()[0])]=pairs

            
        #recurse
        return self.__optimize(list(set(n.union(pairs[n]) for n in pairs.keys())))
        
        
    
#----------------------------------------------------------------------------
#---------------------------------TEST-OK------------------------------------
#----------------------------------------------------------------------------
if __name__=='__main__':
    
    import time
    import random
    import pandas as pd
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    from Simulation.Utilities.DatasetHandler import createNormalsDataset
    from Simulation.Utilities.Dec import *
    
    r=random.Random()
    
    ds=pd.Panel({i:createNormalsDataset(r.randint(0, 7), 0.01, [20,2], cumsum=True) for i in range(4)})
    
    ds=deDec(ds)
    mf=lambda x:sum(x)
    t=40
    print('---------------the dataset-------------------')
    print(ds)
    print(ds.values)
    fig=plt.figure()
    ax=fig.add_subplot(1,1,1, projection='3d')
    for item in ds.items:
        ax.plot(ds.loc[item,:,1], ds.loc[item,:,0],zs=ds.major_axis,label=item)
        ax.legend()
    ax.view_init(45,28)
    ax.legend()

    print('---------------------------------------------')
    p=DistributionPairer(ds,mf,t)
    print(p.getTypeDict())
    print(p.getWeightDict())
    
    fig.show()
    time.sleep(2)
    