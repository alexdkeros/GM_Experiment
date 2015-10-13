'''
@author: ak
'''
import uuid
import scipy as sp
from Simulation.Utilities.Dec import *

class GenericNode:
    '''
    generic Node class
    '''
    
    def __init__(self,
                 network,
                 dataset,
                 nid=uuid.uuid4(),
                 weight=1):
        '''
        Constructor
        args:
            @param network: communication network
            @param dataset: pandas' Dataframe containing updates
            @param nid: unique node id
            @param weight: node's weight
        '''
        self.network=network
        self.dataset=dataset
        self.id=nid
        self.weight=dec(weight)
        
        #register node to the network
        self.network.registerNode(self)
        
    '''
    --------------getters
    '''
    def getDataset(self):
        return self.dataset
    
    def getWeight(self):
        return self.weight
    
    def getId(self):
        return self.id
    
    '''
    -------------node execution
    '''
    def check(self):
        '''
        check for Local Violation
        '''
        raise NotImplementedError
        
    def run(self):
        '''
        main node execution method, update handling
        '''
        raise NotImplementedError
    
    
    '''
    ------------signal handling
    '''
    def send(self,target,msg,data):
        '''
            calls network method "signal"
            tuple (id, target id ([] or single target), message([] or single msg), data)
        '''
        if not isinstance(target, list):
            target=[target]
        if not isinstance(data, list):
            data=[data]
        
        for targ,dat in zip(target,(len(target)==len(data)) and data or data*len(target)): #to cover cases of multiple targets, one data | multiple targets, multiple data
            self.network.signal((self.id, targ , msg, dat))
        
    def rcv(self,data):
        '''
            is called by env
            data is tuple (sender id, target id , msg, data)
            
            dispaches msg to appropriate message handler with arguments data, sender
        '''
        if data[1]==self.id:
            if data:
                getattr(self, data[2])(data[3],data[0])
        
        
