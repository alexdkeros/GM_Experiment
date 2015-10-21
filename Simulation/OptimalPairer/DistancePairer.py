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
        OptimalPairer.__init__(self,dataset)
        
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
        subsetMean=ArrayOp.computeMean(self.dataset.loc[nodes,:,:], weightDict=self.nodeWeightDict)
        
        #cumulative distance of node subset
        cumDist=pd.DataFrame([sum(linalg.norm(self.dataset.loc[it1,i,:]-self.dataset.loc[it2,i,:])
                for it1,it2 in itertools.combinations(nodes,2)) for i in self.dataset.major_axis])
        
        weight=(pd.DataFrame(-abs(self.globalMean.apply(self.monFunc, axis=1)-subsetMean.apply(self.monFunc, axis=1))).add(cumDist,axis=0)).sum(axis=0).values[0]
        
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
            self.typeDict[len(nodeSetCollection[0])]={nodeSetCollection[0]:nodeSetCollection[0]}
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
        return self.__optimize(list(set(n.union(pairs[n]) for n in pairs.keys())))
    
#----------------------------------------------------------------------------
#---------------------------------TEST---------------------------------------
#----------------------------------------------------------------------------
def monFunc10D(x):
    nom=x[0]+x[1]+x[2]+x[3]+x[4]+x[9]
    denom=x[5]+x[6]+x[7]+x[8]
    
    return (nom/denom)**2


if __name__=='__main__':
    
    import time
    import random
    import pandas as pd
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    from Simulation.Utilities.DatasetHandler import createNormalsDataset
    from Simulation.Utilities.Dec import *   
    from Simulation.Utilities.DatasetHandler import splitTrainTestDataset
    '''
    r=random.Random()
    
    #ds=pd.Panel({i:createNormalsDataset(r.randint(0, 10), 0.01, [20,2], cumsum=True) for i in range(4)})
    ds=createNormalsDataset(loc=5, scale=3, size=[4,20,2], cumsum=True)
    
    ds=deDec(ds)
    nWd={i:1.0 for i in range(4)}
    mf=lambda x:sum(x)
    t=40
    
    print('---------------the dataset-------------------')
    print(ds)
    print(ds.values)
    fig=plt.figure()
    ax=fig.add_subplot(1,1,1,projection='3d') #3D -  projection='3d'
    for item in ds.items:
        #ax.plot(ds.loc[item,:,:],label=item)
        ax.plot(ds.loc[item,:,1], ds.loc[item,:,0],zs=ds.major_axis,label=item)
        ax.legend()
    ax.view_init(30,45)
    ax.legend()
    
    print('---------------------------------------------')
    p=DistancePairer(ds,nWd,mf)
    print(p.getTypeDict())
    print(p.getWeightDict())
    
    fig.show()
    #time.sleep(2)
    '''
    ds=pd.read_pickle('/home/ak/git/GM_Experiment/Experiments/datasets/linear10D10N.p')
    nWd={nId:1.0 for nId in ds.items}
    train, test=splitTrainTestDataset(ds)
    p=DistancePairer(deDec(train),nWd,monFunc10D)
    print(p.getTypeDict())
    print(p.getWeightDict())