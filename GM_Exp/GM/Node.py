'''
@author: ak
'''
import uuid
from GM_Exp import Config


class Node:
    
    def __init__(self,env, id=uuid.uuid4(),threshold=Config.threshold,monitoringFunction=Config.defMonFunc):
        self.env=env
        self.id=id
        self.threshold=threshold
        self.monitoringFunction=monitoringFunction
        self.v=0    #statistics vector
        self.e=0    #estimate vector
        
    def getId(self):
        return self.id
    
    def send(self,target,msg,data):
        '''
            calls enviroment method "signal"
            tuple (id, target id, message, data)
        '''
        if not isinstance(target, list):
            target=[target]
        if not isinstance(data, list):
            data=[data]
        if len(target)==len(data):
            for targ,dat in zip(target,data):
                self.env.signal((self.id,targ , msg, dat))
        
    def rcv(self,data):
        '''
            data is tuple (sender id, target id , msg, data)
        '''
        if data[1]==self.id:
            if data:
                getattr(self, data[2])(data[3],sender=data[0])
        
        
