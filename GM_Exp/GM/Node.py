'''
@author: ak
'''
import uuid
from GM_Exp import Config


class Node:
    
    def __init__(self,env, id=uuid.uuid4(), weight=0, threshold=Config.threshold,monitoringFunction=Config.defMonFunc):
        self.env=env
        self.id=id
        self.threshold=threshold
        self.monitoringFunction=monitoringFunction
        self.weight=weight
        self.v=0    #statistics vector
        self.e=0    #estimate vector
        
    def getWeight(self):
        return self.weight
    
    def getId(self):
        return self.id
    
    def run(self):
        pass
    
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
            data is tuple (sender id, target id , msg, data)
        '''
        if data[1]==self.id:
            if data:
                getattr(self, data[2])(data[3],data[0])
        
        
