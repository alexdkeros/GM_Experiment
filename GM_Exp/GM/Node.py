'''
@author: ak
'''
import uuid
from GM_Exp import Config


class Node:
    '''
    general Node class
    '''
    
    def __init__(self,env, nid=uuid.uuid4(), weight=1):
        '''
        Constructor
        args:
            @param env: enviroment creating Node, called for communication, msg passing
            @param nid: unique node id
            @param weight: node's weight
        '''
        self.env=env
        self.id=nid
        self.weight=weight

    
    '''
    --------------getters
    '''
    def getWeight(self):
        return self.weight
    
    def getId(self):
        return self.id
    
    '''
    -------------node execution
    '''
    def check(self):
        pass
        
    def run(self):
        pass
    
    '''
    ------------signal handling
    '''
    def send(self,target,msg,data):
        '''
            calls enviroment method "signal"
            tuple (id, target id, message, data)
        '''
        if not isinstance(target, list):
            target=[target]
        if not isinstance(data, list):
            data=[data]
        for targ,dat in zip(target,len(target)==len(data) and data or data*len(target)): #to cover cases of multiple targets, one data | multiple targets, multiple data
            self.env.signal((self.id,targ , msg, dat))
        
    def rcv(self,data):
        '''
            is called by env
            data is tuple (sender id, target id , msg, data)
        '''
        if data[1]==self.id:
            if data:
                getattr(self, data[2])(data[3],data[0])
        
        
