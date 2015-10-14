'''
@author: ak
'''
import random
from Simulation.OptimalPairer.OptimalPairer import OptimalPairer

class RandomPairer(OptimalPairer):
    '''
    node random pairing as in original Geometric Monitoring method
    '''
    def __init__(self,dataset):
        '''
        Constructor
        args:
            @param dataset: training dataset as Pandas Panel with NodeIds as Items
                                                Updates as Major_Column
                                                Update types as Minor_Column
        '''
        OptimalPairer.__init__(self, dataset)
    
    
    '''
    ----------------------------------------------
    getters
    ----------------------------------------------
    '''
    def getOptPairing(self, nodes):
        '''
        args:
            @param nodes: set of nodeIds
        @return set with random pair or None
        '''
        diffSet=set(self.dataset.items)-set(nodes)
        if diffSet:
            return set([random.sample(diffSet,1)[0]])
        else:
            return None
        
    '''
    ----------------------------------------------
    optimizing helper functions
    ----------------------------------------------
    '''
    def __computeWeight(self, nodes):
        '''
        do nothing
        '''
        pass
    
    '''
    ----------------------------------------------
    main function: OPTIMIZER
    ----------------------------------------------
    '''
    def __optimize(self):
        '''
        do nothing
        '''
        pass
    
    
    
    
#----------------------------------------------------------------------------
#---------------------------------TEST-OK------------------------------------
#----------------------------------------------------------------------------
if __name__=='__main__':
    
    import pandas as pd
    from Simulation.Utilities.DatasetHandler import createNormalsDataset
    
    ds=createNormalsDataset(3, 3, [4,20,1], cumsum=True, items=['n1','n2','n3','n4'])
    
    print('---------------the dataset-------------------')
    print(ds)
    print(ds.values)
    print('---------------------------------------------')
    pairer=RandomPairer(ds)
    
    print(pairer.getOptPairing(set()))
    
    
    print(pairer.getOptPairing(set(['n1'])))
    
    
    print(pairer.getOptPairing(set(['n1','n2'])))
    
    
    print(pairer.getOptPairing(set(['n1','n2','n3','n4'])))
    
    
    print(pairer.getOptPairing(set()))
    
    
    print(pairer.getOptPairing(set(['n1'])))
    
    
    print(pairer.getOptPairing(set(['n1','n2'])))
    
    
    print(pairer.getOptPairing(set(['n1','n2','n3','n4'])))
    
    